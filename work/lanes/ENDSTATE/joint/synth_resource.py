"""Read-only reuse of FRESH's clean rank-three SAT CEGAR, on explicit roles."""
import os,sys,json,time,argparse,hashlib,collections
from pathlib import Path
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
H=Path(__file__).resolve().parent;ROOT=H.parents[3];sys.path.insert(0,str(H/'fresh_snapshot'))
import synth as F
import stim

def configure(B,C):
 for mod in [F,F.S,F.ft]:mod.B=list(B);mod.C=list(C)
 F.H=H;F.S.HERE=H

def endpoint(d,B,C):
 circ=stim.Circuit();circ.append('R',B+C);circ.append('H',d['pivots'])
 for layer in d['ops']:
  busy=set()
  for u,v in layer:assert v in F.S.nb(u)and not({u,v}&busy);busy|={u,v};circ.append('CX',[u,v])
 for b,c in zip(B,C):circ.append('CX',[b,c])
 sim=stim.TableauSimulator();sim.do(circ);checks=[]
 for pauli,row in [('X',r)for r in F.ROWS]+[('Z',r)for r in F.ROWS]+[('Z',list(range(7)))]:
  p=stim.PauliString(36)
  for i in row:p[B[i]]=pauli
  checks.append(sim.peek_observable_expectation(p))
 for q in C:p=stim.PauliString(36);p[q]='Z';checks.append(sim.peek_observable_expectation(p))
 assert all(v==1 for v in checks),checks
 return dict(post_transversal_B_zeroL_C_zero7=True,expectations=checks)

def run(a):
 row=json.loads((H/'labelled_regions.json').read_text())[a.row];B=row['final']['b'];C=row['final']['c'];configure(B,C);start=time.monotonic();m=F.Model(a.depth,a.cap,a.seed,clean=True)
 if a.hint:m.warm(json.loads(Path(a.hint).read_text()))
 if a.eager:
  for t in range(a.depth+1):
   for q in B+C:m.cut((t,(q,)))
 nc=0;status='UNKNOWN';witness=None
 while time.monotonic()-start<a.seconds:
  m.s.conf_budget(5000);ok=m.s.solve_limited()
  if ok is False:status='UNSAT';break
  if ok is None:continue
  nc+=1;d=m.candidate();v=F.verify(d,clean=True);assert v['target_ok'];print(json.dumps(dict(model=nc,cx=v['cx'],bad=len(v['bad']),seconds=time.monotonic()-start)),flush=True)
  if not v['bad']:
   witness=dict(d,verification=v,endpoint=endpoint(d,B,C),B=B,C=C,row_index=a.row,resource_contract='sum_x_in_S |x>_B |x>_C; after transversal C is |0>^7 and all seven literal bits are checked',clean=True)
   status='SAT';(H/(a.out+'.prep.json')).write_text(json.dumps(witness,indent=2));break
  for src in v['bad']:m.cut(src)
  m.warm(d)
 rec=dict(args=vars(a),status=status,seconds=time.monotonic()-start,models=nc,cuts=len(m.added),stats=m.s.accum_stats(),row_name=row['name'],source_sha256=hashlib.sha256((H/'fresh_snapshot/synth.py').read_bytes()).hexdigest());(H/(a.out+'.receipt.json')).write_text(json.dumps(rec,indent=2));print(json.dumps(rec),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--row',type=int,required=True);p.add_argument('--out',required=True);p.add_argument('--depth',type=int,default=11);p.add_argument('--cap',type=int,default=77);p.add_argument('--seconds',type=float,default=600);p.add_argument('--seed',type=int,default=0);p.add_argument('--hint');p.add_argument('--eager',action='store_true');run(p.parse_args())
