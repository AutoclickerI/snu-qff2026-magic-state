"""CP-SAT Clifford-instrument synthesis on a moving cultivation boundary.

Three-wire c-d-a line: arbitrary cat/data joint input, fresh a=0, output a.
Accepted Kraus operators must be proportional to the exact original instrument,
with sum of squared factors one (no hidden acceptance loss). State variables are
GL(3,2) transforms at each native CX step. All circuit prices are full cubic.
"""
from common import *
import numpy as np,itertools,collections,argparse,gzip
EDGES=[(0,1),(1,0),(1,2),(2,1)]
def trans(state,e):
 u,v=e;return tuple(y^(((y>>u)&1)<<v)for y in state)
ID=tuple(range(8));states=[ID];index={ID:0}
for st in states:
 for e in EDGES:
  ns=trans(st,e)
  if ns not in index:index[ns]=len(states);states.append(ns)
assert len(states)==168
TABLE=[(i,g,index[trans(st,e)])for i,st in enumerate(states)for g,e in enumerate(EDGES)]

def kraus(st,bases,r,s):
 K=np.zeros((2,4))
 for x in range(4):
  y=st[x];amp=1.
  for bit,b,m in zip([y&1,(y>>1)&1],bases,[r,s]):amp*=float(bit==m)if b=='Z'else (-1.)**(bit*m)/math.sqrt(2)
  K[(y>>2)&1,x]+=amp
 return K
ref=ID
for e in[(0,1),(1,2),(2,1)]:ref=trans(ref,e)
TARGET=kraus(ref,'XZ',0,0);den=float((TARGET*TARGET).sum())
contracts={}
for i,st in enumerate(states):
 for bases in ['XX','XZ','ZX','ZZ']:
  for parity in [(1,0),(0,1),(1,1)]:
   for watch in [-1,0,1]:
    ks=[];weight=0.;ok=True
    for r,s in itertools.product([0,1],repeat=2):
     if (r*parity[0]^s*parity[1])or(watch>=0 and [r,s][watch]):continue
     K=kraus(st,bases,r,s);v=float((K*TARGET).sum())/den
     if np.max(np.abs(K-v*TARGET))>1e-12:ok=False;break
     weight+=v*v;ks.append(v)
    if ok and abs(weight-1)<1e-12:contracts.setdefault(i,[]).append(dict(bases=bases,parity=parity,watch=watch,factors=ks))

def witnesses(depth):
 m=cp_model.CpModel();gs=[m.NewIntVar(0,3,f'g{t}')for t in range(depth)];ss=[m.NewIntVar(0,167,f's{t}')for t in range(depth+1)];m.Add(ss[0]==0)
 for t,g in enumerate(gs):
  m.AddAllowedAssignments([ss[t],g,ss[t+1]],TABLE)
  if t:m.Add(g!=gs[t-1])
 m.AddAllowedAssignments([ss[-1]],[(i,)for i in contracts]);solver=cp_model.CpSolver();solver.parameters.num_workers=1;solver.parameters.cp_model_presolve=False
 while True:
  status=solver.Solve(m)
  if status==cp_model.INFEASIBLE:return
  assert status in(cp_model.OPTIMAL,cp_model.FEASIBLE)
  gates=[solver.Value(g)for g in gs];end=solver.Value(ss[-1]);yield gates,end
  m.AddForbiddenAssignments(gs,[gates])

def build(base,gates,contract,mode):
 c=copy.deepcopy(base);ops=c['ops'];mi=next(i for i,o in enumerate(ops)if 'measure q[9] -> c[9];'in o['lines']);ci=max(i for i in range(mi)if ops[i]['lines']==['cx q[9],q[15];']);T=ops[ci]['t'];drop={ci,mi}
 for line in ['tdg q[15];','measure q[16] -> c[43];','cx q[15],q[16];','cx q[16],q[15];','measure q[15] -> c[53];']:
  drop.add(next(i for i,o in enumerate(ops)if line in o['lines']))
 new=[dict(id=1000,lines=['measure q[16] -> c[43];'],t=T-1)]
 for j,g in enumerate(gates):
  u,v=( [9,15,16][x]for x in EDGES[g]);new.append(dict(id=1001+j,lines=[f'cx q[{u}],q[{v}];'],t=T+j))
 for j,(q,basis,bit)in enumerate(zip([9,15],contract['bases'],[9,91])):
  new.append(dict(id=1100+j,lines=([f'h q[{q}];']if basis=='X'else[])+[f'measure q[{q}] -> c[{bit}];'],t=T+len(gates)))
 new.append(dict(id=1102,lines=['tdg q[16];'],t=T+len(gates)))
 # Source is safely reusable without reset exactly when its Z bit is checked.
 if not(contract['bases'][1]=='Z' and contract['watch']==1):new.append(dict(id=1103,lines=['reset q[15];'],t=T+len(gates)+1))
 c['ops']=[o for i,o in enumerate(ops[:ci])if i not in drop]+new+[o for i,o in enumerate(ops[ci:],ci)if i not in drop]
 c['tail']=[l for l in c['tail']if l!='// DETECTOR c[53]']
 repl=' '.join(f'c[{q}]'for yes,q in zip(contract['parity'],[9,91])if yes)
 c['tail']=[re.sub(r'c\[9\]',repl,l)for l in c['tail']]
 if contract['watch']>=0:c['tail'].append('// DETECTOR c['+str([9,91][contract['watch']])+']')
 c['ordered']=True;c['meta']['st1_instrument']=dict(gates=[EDGES[g]for g in gates],contract=contract,meaning='c=q9,d=q15,a=q16; arbitrary accepted input instrument')
 return schedule(c,mode=mode)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('stem');p.add_argument('--max-depth',type=int,default=5);p.add_argument('--min-depth',type=int,default=1);p.add_argument('--enumerate-only',action='store_true');a=p.parse_args();base=read(a.stem);rows=[];best=float('inf');n=0;cert=[]
 if a.min_depth>1:
  rows=json.loads(gzip.open(H/'instrument15_witnesses.json.gz','rt').read());best=json.loads((H/'instrument15_best.screen.json').read_text())['total'];cert=json.loads((H/'instrument15_certificate.json').read_text())['depths']
 for depth in range(a.min_depth,a.max_depth+1):
  count=0
  for gates,end in witnesses(depth):
   count+=1
   if a.enumerate_only:continue
   for k,contract in enumerate(contracts[end]):
    for mode in ['near','alap']:
     n+=1;name=f'instrument15_d{depth}_w{count}_c{k}_{mode}';d,rec=build(base,gates,contract,mode)
     if d is None:r=dict(error='schedule infeasible',receipt=rec)
     else:
      try:
       stem=save(d,name);r=score(stem)
       if r.get('total',1)<best and r['exp_minus_A1']>=.5002:
        best=r['total'];save(d,'instrument15_best');(H/'instrument15_best.screen.json').write_text(json.dumps(r,indent=2));print('BEST',name,best,flush=True)
      except Exception as e:r=dict(error=str(e))
     row=dict(name=name,depth=depth,gates=gates,contract=contract,mode=mode,result=r);rows.append(row)
     with gzip.open(H/'instrument15_witnesses.json.gz','wt')as f:json.dump(rows,f)
     with(H/'REPORT.md').open('a')as f:f.write('\n- Instrument '+name+': '+(f"exact {r['total']:.12g}, acceptance proxy {r['exp_minus_A1']:.9f}"if 'total'in r else json.dumps(r))+'. Complete line-3 recipe; mixed data/cat motion, retained exterior.\n')
     # Retain only current finalist; all circuit witnesses regenerate from this ledger.
     if d is not None:
      for ext in['.qasm','.json','.plan.json','.screen.json']:(H/(name+ext)).unlink(missing_ok=True)
  cert.append(dict(depth=depth,witnesses=count,status='EXHAUSTED',scope='irreducible adjacent CX words on three-wire line with accepted Kraus contract'))
  (H/'instrument15_certificate.json').write_text(json.dumps(dict(states=len(states),contract_states=len(contracts),contract_options=sum(map(len,contracts.values())),depths=cert),indent=2));print('depth',depth,count,flush=True)
