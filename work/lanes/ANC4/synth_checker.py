import os,sys,json,time
sys.dont_write_bytecode=True
from pathlib import Path
from ortools.sat.python import cp_model
HERE=Path(__file__).resolve().parent
from generate import REVIEW,PAR
B=[8,9,22,26,16,13,19];F=[14,15,21,20]

def run(depth):
 qs=B+F;m=cp_model.CpModel();one=m.NewBoolVar('one');m.Add(one==1)
 ed=[(i,j) for i in range(11) for j in range(7,11) if i!=j and abs(qs[i]//6-qs[j]//6)+abs(qs[i]%6-qs[j]%6)==1]
 s=[{e:m.NewBoolVar('') for e in ed} for _ in range(depth)]
 c=[[[m.NewBoolVar('') for bit in range(7)] for q in range(11)] for _ in range(depth+1)]
 for q in range(11):
  for bit in range(7):m.Add(c[0][q][bit]==int(q==bit))
 for t in range(depth):
  for q in range(11):
   m.AddAtMostOne([v for e,v in s[t].items() if q in e])
   for bit in range(7):
    incoming=[]
    for u,v in ed:
     if v==q:
      a=m.NewBoolVar('');m.AddMultiplicationEquality(a,[s[t][u,v],c[t][u][bit]]);incoming.append(a)
    m.AddBoolXOr([c[t+1][q][bit],c[t][q][bit],*incoming,one])
 for j,row in enumerate(PAR):
  for bit in range(7):m.Add(c[-1][7+j][bit]==int(bit in row))
 # Four leaf checks at final layer; restrict to <=18 CX.
 for i in range(4):m.Add(s[-1][i,7+i]==1)
 n=sum(v for d in s for v in d.values());m.Add(n<=18)
 last=[]
 for i in range(7):
  ls=[]
  for t in range(depth):
   a=m.NewIntVar(0,depth-1,'');m.Add(a==t*sum(v for e,v in s[t].items() if e[0]==i));ls.append(a)
  l=m.NewIntVar(0,depth-1,'');m.AddMaxEquality(l,ls);last.append(l)
 exp=7*(depth-1)-sum(last)
 m.Minimize(1000*exp+n)
 if depth==6:
  for t,l in enumerate(REVIEW):
   for e,v in s[t].items():m.AddHint(v,int(e in l))
 solver=cp_model.CpSolver();solver.parameters.num_workers=1;solver.parameters.max_time_in_seconds=120
 start=time.time();st=solver.Solve(m);out=dict(depth=depth,status=solver.StatusName(st),seconds=time.time()-start,bound=solver.BestObjectiveBound())
 if st in (cp_model.OPTIMAL,cp_model.FEASIBLE):out.update(layers=[[e for e in ed if solver.Value(s[t][e])] for t in range(depth)],cx=solver.Value(n),exposure=solver.Value(exp),last=[solver.Value(v) for v in last])
 (HERE/f'checker_d{depth}.json').write_text(json.dumps(out,indent=2)+'\n');print(out,flush=True)
if __name__=='__main__':
 assert os.getloadavg()[0]<os.cpu_count()-2
 for d in [6,7,8]:run(d)
