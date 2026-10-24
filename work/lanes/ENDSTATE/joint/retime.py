"""Fixed-wire native retiming only; all positions/routes/encoder gates stay fixed."""
import os,sys,json,copy,argparse,collections
from pathlib import Path
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from ortools.sat.python import cp_model
H=Path(__file__).resolve().parent

def run(stem,out):
 stem=Path(stem);p=json.loads(stem.with_suffix('.plan.json').read_text());ops=sorted(p['ops'],key=lambda o:o['t']);old=[o['t']for o in ops];Rold=p['meta']['R'];m=cp_model.CpModel();R=m.NewIntVar(0,Rold,'R');ts=[m.NewIntVar(0,Rold+2,f't{i}')for i in range(len(ops))];last={}
 for i,o in enumerate(ops):
  for q in o['qs']:
   if q in last:m.Add(ts[i]>ts[last[q]])
   last[q]=i
  if old[i]>=Rold:m.Add(ts[i]==R+old[i]-Rold)
  else:m.Add(ts[i]<R)
  m.AddHint(ts[i],old[i])
 s=cp_model.CpSolver();s.parameters.num_workers=1;s.parameters.cp_model_presolve=False;m.Minimize(R);st=s.Solve(m);assert st==cp_model.OPTIMAL;savedR=s.Value(R);m.Add(R==savedR)
 terminal=set()
 for q in range(36):
  seq=[i for i,o in enumerate(ops)if q in o['qs']]
  for j,i in enumerate(seq):
   if ops[i]['name']in('MX','MEASURE')and(j+1==len(seq)or ops[seq[j+1]]['name']in('RX','RESET')):terminal.add(i)
 m.Maximize(sum((-1 if i in terminal else 1)*t for i,t in enumerate(ts)));st=s.Solve(m);assert st==cp_model.OPTIMAL
 for o,t in zip(ops,ts):o['t']=s.Value(t)
 times=sorted({o['t']for o in ops});ct={t:i for i,t in enumerate(times)};used=sorted({q for o in ops for q in o['qs']});lines=p['h'][:];bar='barrier '+','.join(f'q[{q}]'for q in used)+';'
 for t in times:
  layer=[o for o in ops if o['t']==t];busy=[q for o in layer for q in o['qs']];assert len(busy)==len(set(busy))
  for o in layer:lines+=o['lines'];o['t']=ct[t]
  lines.append(bar)
 lines+=p['tail'];p['meta'].update(R=ct[savedR],native_depth=len(times),retiming=dict(status=s.StatusName(st),minimum_model_R=savedR,mode='ALAP; terminal/reset-followed measurements ASAP',source=str(stem)));p['ops']=sorted(ops,key=lambda o:o['t'])
 out=H/out;out.with_suffix('.qasm').write_text('\n'.join(lines)+'\n');out.with_suffix('.json').write_text(json.dumps(p['meta'],indent=2));out.with_suffix('.plan.json').write_text(json.dumps(p,indent=1));print(str(out),p['meta']['R'])
if __name__=='__main__':run(*sys.argv[1:])
