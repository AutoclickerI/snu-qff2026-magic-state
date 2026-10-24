"""Measurement-assisted encoder on the actual seven A cells, dualized to |+L>."""
from common import *
from build_prep import solve_support
from helper_synth import Model as Base,Solver
import argparse,itertools,random,collections
class Model(Base):
 def __init__(self,depth,cap,seed=0):
  self.D=depth;self.cells=A;self.n=0;self.clauses=[];self.s=None;self.edges=[(u,v)for u in A for v in A if abs(u//6-v//6)+abs(u%6-v%6)==1]
  self.sel=[{e:self.nv()for e in self.edges}for _ in range(depth)];self.ms=[{q:self.nv()for q in A}for _ in range(depth)]
  self.card([z for ss in self.sel for z in ss.values()],cap)
  self.card([z for ss in self.ms for z in ss.values()],4)
  for t,ss in enumerate(self.sel):
   for q in A:
    gates=[z for e,z in ss.items()if q in e]+[self.ms[t][q]]+([self.ms[t-1][q]]if t else[])
    for a,b in itertools.combinations(gates,2):self.add([-a,-b])
    if t==depth-1:self.add([-self.ms[t][q]])
  self.x=[{q:[self.nv()for _ in range(3)]for q in A}for _ in range(depth+1)]
  for i,q in enumerate(A):
   for b,z in enumerate(self.x[-1][q]):self.add([z if(i+1)>>b&1 else-z])
  for t in reversed(range(depth)):
   for q in A:
    es=[e for e in self.edges if e[1]==q]
    for b,z in enumerate(self.x[t][q]):
     a=self.x[t+1][q][b];self.add([self.ms[t][q]]+[self.sel[t][e]for e in es]+[-z,a]);self.add([self.ms[t][q]]+[self.sel[t][e]for e in es]+[z,-a]);self.add([-self.ms[t][q],-a])
     for e in es:self.xor_eq(z,[a,self.x[t+1][e[0]][b]],guard=[-self.sel[t][e]])
  self.nz={q:self.nv()for q in A}
  for q,z in self.nz.items():
   for y in self.x[0][q]:self.add([-y,z])
   self.add([-z]+self.x[0][q])
  self.card(list(self.nz.values()),3);self.s=Solver(name='cadical195',bootstrap_with=self.clauses,use_timer=True);self.clauses=[];self.s.configure({'seed':seed})
 def candidate(self):
  vals=set(self.s.get_model());return dict(ops=[[list(e)for e,z in ss.items()if z in vals]for ss in self.sel],measures=[[q for q,z in ss.items()if z in vals]for ss in self.ms],pivots=[q for q,z in self.nz.items()if z in vals])
def build(prep,name):
 orig=json.loads((H/'inputs/ladder_f00.json').read_text())['units'];base=read(H/'inputs/v23h_c2c9');removed={int(b)for o in orig if o['tag']=='A'for b in re.findall(r'c\[(\d+)\]',' '.join(o['lines']))};ops=[copy.deepcopy(o)for o in orig if o['tag']!='A'];tail=[]
 for l in base['tail']:
  if l.startswith('// DETECTOR'):
   bs=set(map(int,re.findall(r'c\[(\d+)\]',l)))-removed
   if bs:tail.append('// DETECTOR '+' '.join(f'c[{b}]'for b in sorted(bs)))
  else:tail.append(l)
 piv=prep['pivots'];vals={q:(1<<piv.index(q)if q in piv else 0)for q in A};new=[];meas=[];n=100
 for q in A:new.append(dict(lines=[f'reset q[{q}];']+([f'h q[{q}];']if q not in piv else[]),t=0,tag='a_init'))
 for t,L in enumerate(prep['ops'],1):
  for a,b in L:new.append(dict(lines=[f'cx q[{b}],q[{a}];'],t=t,tag='a_encoder'));vals[b]^=vals[a]
  for q in prep['measures'][t-1]:
   new.extend([dict(lines=[f'measure q[{q}] -> c[{n}];'],t=t,tag='a_midmeasure'),dict(lines=[f'reset q[{q}];',f'h q[{q}];'],t=t+1,tag='a_midreset')]);meas.append((n,vals[q]));vals[q]=0;n+=1
 rows=[vals[q]for q in A];corr={}
 for bit,row in meas:
  mask=solve_support(rows,row)
  for i,q in enumerate(A):
   if mask>>i&1:corr.setdefault(14+i,set()).add(bit)
 for j,l in enumerate(tail):
  if l.startswith('// DETECTOR'):
   bs=set(map(int,re.findall(r'c\[(\d+)\]',l)));ex=set()
   for b in bs:ex^=corr.get(b,set())
   tail[j]='// DETECTOR '+' '.join(f'c[{b}]'for b in sorted(bs^ex))
 new.sort(key=lambda o:o['t']);allops=ops+new;m=cp_model.CpModel();ts=[m.NewIntVar(0,85,f't{i}')for i in range(len(allops))];R=m.NewIntVar(45,80,'R')
 for i,o in enumerate(ops):m.Add(ts[i]==o['t']+(R-45 if o['t']>=45 else 0))
 for q in range(36):
  pre=sorted([i for i,o in enumerate(ops)if q in unit(o).qs and o['t']<45],key=lambda i:ops[i]['t']);post=sorted([i for i,o in enumerate(ops)if q in unit(o).qs and o['t']>=45],key=lambda i:ops[i]['t']);mid=[len(ops)+i for i,o in enumerate(new)if q in unit(o).qs]
  for a,b in zip(pre+mid+post,(pre+mid+post)[1:]):m.Add(ts[b]>ts[a])
 for i in range(len(ops),len(allops)):m.Add(ts[i]<R)
 s=cp_model.CpSolver();s.parameters.num_workers=1;s.parameters.max_time_in_seconds=10;m.Minimize(R);status=s.Solve(m);assert status in(cp_model.FEASIBLE,cp_model.OPTIMAL)
 m.Add(R==s.Value(R));m.Maximize(sum(ts[len(ops):]));status=s.Solve(m);assert status in(cp_model.FEASIBLE,cp_model.OPTIMAL)
 for i,o in enumerate(allops):o['t']=s.Value(ts[i]);o['id']=i
 c=dict(h=['OPENQASM 2.0;','include "qelib1.inc";','qreg q[36];',f'creg c[{n}];'],ops=allops,tail=tail,meta=dict(data_qubits=D,R=s.Value(R),a_prep=prep,source='MAIN/v23h_c2c9',method='Measurement-assisted independent A on fixed seven cells'))
 return save(c,name)
def main():
 p=argparse.ArgumentParser();p.add_argument('--depth',type=int,default=8);p.add_argument('--cap',type=int,default=10);p.add_argument('--seed',type=int,default=0);p.add_argument('--seconds',type=float,default=300);p.add_argument('--count',type=int,default=100);a=p.parse_args();m=Model(a.depth,a.cap,a.seed);st=time.monotonic();count=0;status='TIMEOUT'
 while time.monotonic()-st<a.seconds and count<a.count:
  m.s.conf_budget(20000);ok=m.s.solve_limited()
  if ok is None:continue
  if ok is False:status='UNSAT';break
  prep=m.candidate();name=f'amb_d{a.depth}_c{a.cap}_s{a.seed}_{count:03d}';(H/(name+'.prep.json')).write_text(json.dumps(prep,indent=2))
  try:
   stem=build(prep,name);r=score(stem);append_result(name,r,'Independent A measurement encoder on seven existing A cells.');print(json.dumps(dict(name=name,score=r)),flush=True)
  except Exception as e:print(json.dumps(dict(name=name,error=repr(e))),flush=True)
  vals=set(m.s.get_model());m.add([-z if z in vals else z for ss in m.sel+m.ms for z in ss.values()]);count+=1
 rec=dict(args=vars(a),status=status,count=count,seconds=time.monotonic()-st);(H/f'amb_d{a.depth}_c{a.cap}_s{a.seed}.receipt.json').write_text(json.dumps(rec,indent=2));append_result(f'amb_d{a.depth}_c{a.cap}_s{a.seed}',rec,'Exact finite A instrument search; UNSAT only within depth/CX/measurement bounds.');print(json.dumps(rec),flush=True)
if __name__=='__main__':main()
