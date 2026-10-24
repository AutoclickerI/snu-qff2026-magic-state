import os,sys,json,itertools,random,collections
sys.dont_write_bytecode=True
from pathlib import Path
ROOT=Path('/home/jihoon/competitions/quantumn');HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'work/lanes/DR'))
from synth import greedy,check,nbrs,synth
from steane_full import GENS

def layers(ops):
 last={};out=[]
 for a,b in ops:
  t=max(last.get(a,-1),last.get(b,-1))+1
  while len(out)<=t:out.append([])
  out[t].append((a,b));last[a]=last[b]=t
 return out

def path(u,v,avail):
 todo=collections.deque([[u]]);seen={u}
 while todo:
  p=todo.popleft()
  if p[-1]==v:return p
  for q in nbrs(p[-1]):
   if q in avail and q not in seen:todo.append(p+[q]);seen.add(q)
 raise ValueError((u,v))
def remote(p):
 # Dirty-intermediate exact CX, restored intermediate wires.
 if len(p)==2:return [(p[0],p[1])]
 e=list(zip(p,p[1:]));return e+e[-2::-1]+e[1:]+e[-2:0:-1]

def parity_network(B,F,avail,rows):
 # Route each parity CX exactly; gates commute at logical level. Search order
 # plus cancel adjacent involutions using only disjoint commutations.
 import stim
 logical=[(B[i],F[j]) for j,row in enumerate(rows) for i in row]
 best=None
 for seed in range(100):
  rng=random.Random(seed);edges=logical.copy();rng.shuffle(edges);ops=[]
  for u,v in edges:
   for e in remote(path(u,v,avail)):
    for k in range(len(ops)-1,-1,-1):
     if set(e)&set(ops[k]):
      if e==ops[k]:ops.pop(k);break
      ops.append(e);break
    else:ops.append(e)
  ll=layers(ops);key=(len(ll),len(ops))
  if best is None or key<best[0]:best=(key,ll)
 c=stim.Circuit()
 for l in best[1]:
  for e in l:c.append('CX',e)
 inv=stim.Tableau.from_circuit(c).inverse()
 for j,row in enumerate(rows):
  z=inv.z_output(F[j]);assert [i for i,q in enumerate(B) if z[q]==3]==row
 return best[1]

if __name__=='__main__':
 assert os.getloadavg()[0]<os.cpu_count()-2
 lay=json.loads((ROOT/'work/lanes/LAYOUT3/hopt_s4_r0_c2.json').read_text());B=lay['b'];F=[33,34,25,31];av=B+F
 best=None
 for seed in range(100):
  try:
   flat,piv=greedy([{B[i] for i in g} for g in GENS],av,rng=random.Random(seed));ll=layers(flat)
  except:continue
  if not check(B,GENS,av,ll,piv):continue
  key=(len(ll),sum(map(len,ll)))
  if best is None or key<best[0]:best=(key,dict(ops=ll,pivots=piv))
 assert best
 (HERE/'grid_B.json').write_text(json.dumps(best[1],indent=2)+'\n');print('B',best[0],flush=True)
 # Small exact A encoder: CP-SAT all pivots, 7 cells, 8 layers.
 a=lay['a'];res=synth(a,GENS+[[0,1,2]],a,8,seconds=120,workers=1)
 if res:
  aa=dict(ops=res[0],pivots=res[1],status=res[2]);assert check(a,GENS+[[0,1,2]],a,aa['ops'],aa['pivots']);(HERE/'grid_A.json').write_text(json.dumps(aa,indent=2)+'\n');print('A',len(res[0]),sum(map(len,res[0])),flush=True)
 from generate import PAR
 checker=parity_network(B,F,av,PAR);(HERE/'grid_checker.json').write_text(json.dumps(dict(ops=checker,B=B,F=F,parities=PAR),indent=2)+'\n');print('checker',len(checker),sum(map(len,checker)),flush=True)
 lay['f']=F;(HERE/'grid_layout.json').write_text(json.dumps(lay,indent=2)+'\n')
