import os,sys,json,itertools,importlib.util
sys.dont_write_bytecode=True
from pathlib import Path
from ortools.sat.python import cp_model
ROOT=Path('/home/jihoon/competitions/quantumn');HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'work/lanes/DR'));sys.path.insert(0,str(ROOT/'work/lanes/EARLY'))
import early_merge
from steane_full import GENS,PRE_DETECTORS
from gf33 import enc,PRE_DATA,FREE,LAYERS0,PIV
PAR=[[0,5,6],[1,4,6],[2,4,5],[3,4,5,6]]
REVIEW=[[(5,7),(6,10)],[(7,8)],[(10,7),(4,8)],[(8,9)],[(9,10),(7,8)],[(0,7),(1,8),(2,9),(3,10)]]

def direct(rows,depth):
 m=cp_model.CpModel();edges=[(i,7+j) for j,row in enumerate(rows) for i in row];t=[m.NewIntVar(0,depth-1,f't{k}') for k in range(len(edges))]
 for q in range(7+len(rows)):
  ix=[k for k,e in enumerate(edges) if q in e]
  if ix:m.AddAllDifferent([t[k] for k in ix])
 last=[]
 for q in range(7):
  v=m.NewIntVar(0,depth-1,f'last{q}');m.AddMaxEquality(v,[t[k] for k,e in enumerate(edges) if e[0]==q]);last.append(v)
 m.Maximize(sum(last));s=cp_model.CpSolver();s.parameters.num_workers=1;st=s.Solve(m);assert st==cp_model.OPTIMAL
 return [[edges[k] for k in range(len(edges)) if s.Value(t[k])==r] for r in range(depth)]

def all_logicals():
 return [list(c) for c in itertools.combinations(range(7),3) if all(len(set(c)&set(g))%2==0 for g in GENS)]

SCHEDULES={'anc4':REVIEW,'direct4':direct(PAR,4),'redundant7':direct(all_logicals(),3)}

def build(variant,R,measure=False,mx=False,layers=None):
 if variant=='sep':
  import gf33
  return gf33.build('sep',R,2)
 head,stmts=early_merge.prefix_steps();by={}
 for s,t in stmts:by.setdefault(t,[]).append(s)
 A,B,F=FREE[:7],FREE[7:14],FREE[14:21];cells=B+F
 lay=layers or SCHEDULES[variant];nf=max(q for l in lay for e in l for q in e)-6
 start=R-len(lay)+1
 ops=enc(A,True,R-3)+enc(B,False,start-3)
 n=14;initbits=[]
 if mx:
  for k,(t,s) in enumerate(ops):
   if s.startswith('reset') and any(s==f'reset q[{B[i]}];' for i in PIV):
    q=int(s.split('[')[1].split(']')[0]);ops[k]=(t,f'h q[{q}];\nmeasure q[{q}] -> c[{n}];')
    initbits.append(n);n+=1
 for f in F[:nf]:
  if measure:
   ops.append((start-1,f'measure q[{f}] -> c[{n}];'));initbits.append(n);n+=1
  else:ops.append((start-1,f'reset q[{f}];'))
 for t,l in enumerate(lay):
  for u,v in l:ops.append((start+t,f'cx q[{cells[u]}],q[{cells[v]}];'))
 for t,s in ops:by.setdefault(t,[]).extend(s.splitlines())
 bits={}
 by.setdefault(R,[]).extend(f'cx q[{PRE_DATA[i]}],q[{A[i]}];' for i in range(7))
 for key,qs in [('a',A),('f',F[:nf])]:
  for i,q in enumerate(qs):bits[key,i]=n;by.setdefault(R+1,[]).append(f'measure q[{q}] -> c[{n}];');n+=1
 by.setdefault(R+1,[]).extend(f'cx q[{B[i]}],q[{PRE_DATA[i]}];' for i in range(7))
 for i,q in enumerate(B):bits['b',i]=n;by.setdefault(R+2,[]).extend([f'h q[{q}];',f'measure q[{q}] -> c[{n}];']);n+=1
 bar='barrier '+','.join(f'q[{q}]' for q in range(36))+';';out=head+[f'creg c[{n}];']
 for t in range(min(by),R+3):out+=(by.get(t,[]) or ['id q[19];'])+[bar]
 out=out[:-1]
 dets=list(PRE_DETECTORS)
 for k in ['a','b']:
  for g in GENS:dets.append(' '.join(f'c[{bits[k,i]}]' for i in g))
 dets += [f'c[{bits["f",i]}]' for i in range(nf)]
 text='\n'.join(out)+'\n'
 if measure or mx:
  # Determine each random initialization's record offsets with the Clifford
  # suffix; all initializations occur on prefix-unused qubits.
  import stim
  circ=stim.Circuit()
  # QASM -> Stim has T; swap T with I for linear classical frame propagation.
  sys.path.insert(0,str(ROOT/'work'));import tprep.qasm as tq
  saved=tq.adjacent;tq.adjacent=lambda a,b:True
  st,labels,err=tq.convert(text);tq.adjacent=saved;assert not err,err
  # Use stabilizer simulator paired runs to recover deterministic parity basis
  # via random record covariance: converted circuit without T and noise.
  st='\n'.join(l for l in st.splitlines() if not l.startswith(('T ','T_DAG ')))
  sample_circuit=stim.Circuit(st)
  # measurement columns in c index order (QASM schedule writes not monotonic).
  import re,numpy as np
  order=[int(re.search(r'c\[(\d+)\]',s).group(1)) for s in out if s.startswith('measure')]
  inv={b:i for i,b in enumerate(order)}
  randomised=stim.Circuit(); mi=0
  for ins in sample_circuit:
   if ins.name in ("M","MX","MY"):
    for q in ins.targets_copy():
     if order[mi] in initbits:randomised.append("Z_ERROR" if ins.name=="MX" else "X_ERROR",[q.value],0.5)
     randomised.append(ins.name,[q.value]);mi+=1
   else:randomised.append(ins)
  sample=randomised.compile_sampler(seed=12).sample(1024)
  for j,det in enumerate(dets[14:],14):
   db=[int(v) for v in re.findall(r'c\[(\d+)\]',det)]
   val=np.logical_xor.reduce(sample[:,[inv[b] for b in db]],axis=1)
   matches=[]
   for mask in range(1<<len(initbits)):
    bs=[initbits[k] for k in range(len(initbits)) if mask>>k&1]
    vv=np.logical_xor.reduce(sample[:,[inv[b] for b in bs]],axis=1) if bs else np.zeros(len(sample),dtype=bool)
    if np.array_equal(val,vv):matches.append(bs)
   assert len(matches)==1,(variant,j,matches)
   dets[j]+=''.join(f' c[{b}]' for b in matches[0])
 return text+'\n'.join('// DETECTOR '+d for d in dets)+'\n'

if __name__=='__main__':
 out=HERE/'gf';out.mkdir(exist_ok=True)
 sched=[]
 for name,lay in SCHEDULES.items():
  last=[max(t for t,l in enumerate(lay) for u,v in l if u==i) for i in range(7)]
  sched.append(dict(name=name,layers=lay,cx=sum(map(len,lay)),depth=len(lay),exposure=[len(lay)-1-t for t in last]))
 (HERE/'schedules.json').write_text(json.dumps(sched,indent=2)+'\n')
 for name in ['sep','anc4','direct4','redundant7']:
  for R in [33,39,42,47]:
   stem=out/f'{name}_{R}';text=build(name,R);stem.with_suffix('.qasm').write_text(text);stem.with_suffix('.json').write_text(json.dumps(dict(data_qubits=PRE_DATA,grid_free=True,variant=name,R=R,cx=text.count('\ncx '))))
 for name in ['anc4','direct4','redundant7']:
  for mode in ['m','mx','mmx']:
   stem=out/f'{name}_{mode}_33';text=build(name,33,measure='m' in mode and mode!='mx',mx='x' in mode);stem.with_suffix('.qasm').write_text(text);stem.with_suffix('.json').write_text(json.dumps(dict(data_qubits=PRE_DATA,grid_free=True,variant=name,init=mode,R=33,cx=text.count('\ncx '))))
 print(json.dumps(sched))
