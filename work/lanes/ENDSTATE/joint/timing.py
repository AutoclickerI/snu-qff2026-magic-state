import os,sys,json,collections,heapq,random,time,argparse
from pathlib import Path
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from ortools.sat.python import cp_model
H=Path(__file__).resolve().parent;P=H.parent
NB={q:[p for p in range(36)if abs(q//6-p//6)+abs(q%6-p%6)==1]for q in range(36)}

def route(source,goals,region,seed=0):
 rng=random.Random(seed);pos=list(source);paths=[[q]for q in pos];events=[]
 for guard in range(150):
  if pos==goals:return paths,events
  order=[i for i in range(7)if pos[i]!=goals[i]and goals[i]not in set(pos)-{pos[i]}];rng.shuffle(order);opts=[]
  for i in order:
   blocked=set(pos)-{pos[i]};dist={pos[i]:0};prev={pos[i]:None};todo=[(0,rng.random(),pos[i])]
   while todo:
    w,_,q=heapq.heappop(todo)
    if q==goals[i]:break
    if w!=dist[q]:continue
    for v in NB[q]:
     if v in blocked:continue
     nw=w+1+12*(v in region)
     if nw<dist.get(v,100000):dist[v]=nw;prev[v]=q;heapq.heappush(todo,(nw,rng.random(),v))
   if goals[i]in prev:
    rev=[goals[i]]
    while rev[-1]!=pos[i]:rev.append(prev[rev[-1]])
    opts.append((dist[goals[i]],rng.random(),i,list(reversed(rev[:-1]))))
  if opts:
   _,_,i,path=min(opts)
   for v in path:events.append((i,pos[i],v));paths[i].append(v);pos[i]=v
  else:
   opts=[(int(v in region),rng.random(),i,v)for i,q in enumerate(pos)for v in NB[q]if v not in pos and v not in goals]
   if not opts:raise ValueError('no vacancy')
   _,_,i,v=min(opts);events.append((i,pos[i],v));paths[i].append(v);pos[i]=v
 raise ValueError('route iteration limit')

def schedule(row,depth,seed=0,seconds=5):
 pref=json.loads((P/(row['prefix']+'.prefix.json')).read_text());mp={int(k):v for k,v in row['mapping'].items()};ops=pref['ops'];first={};release={}
 for o in ops:
  for oq in o['qs']:
   q=mp[oq];first[q]=min(first.get(q,999),o['asap']);release[q]=max(release.get(q,0),o['asap']+1)
 source=row['initial_data'];goals=row['final']['d'];paths,events=route(source,goals,set(row['region']),seed);m=cp_model.CpModel();V=lambda n,lo=0,hi=120:m.NewIntVar(lo,hi,n);R=V('R',28,115);lives=collections.defaultdict(list)
 def occ(q,s,e,n):
  length=V(n+'len');m.Add(length==e-s);lives[q].append(m.NewIntervalVar(s,length,e,n))
 for q in first:
  if q not in source:occ(q,first[q],release[q],f'pref{q}')
 bs=V('bc_init');m.Add(bs==R-depth-1)
 for q in row['region']:
  m.Add(bs>=release.get(q,0));occ(q,bs,R+(3 if q in row['final']['b']else 2),'bc'+str(q))
 A=row['final']['a'];ai={q:V('a_init'+str(q))for q in A};at=[];last=ai.copy()
 for q in A:m.Add(ai[q]>=release.get(q,0));occ(q,ai[q],R+2,'a'+str(q))
 for i,(u,v)in enumerate(row['a_prep']['ops']):
  t=V('ag'+str(i));m.Add(t>last[u]);m.Add(t>last[v]);m.Add(t<R);last[u]=last[v]=t;at.append(t)
 for q in A:m.Add(ai[q]<R)
 ht=[]
 for i,path in enumerate(paths):
  ts=[V(f'd{i}h{j}',1,112)for j in range(len(path)-1)];ht.append(ts)
  for j,(u,v)in enumerate(zip(path,path[1:])):
   m.Add(ts[j]>=release[source[i]]if j==0 else ts[j]>=ts[j-1]+2);m.Add(ts[j]-1>=release.get(v,0));m.Add(ts[j]+2<=R)
  if row['prefix']=='v30f_hopT'and ts:m.Add(ts[-1]+3<=R)
  for j,q in enumerate(path):occ(q,first[source[i]]if j==0 else ts[j-1]-1,R+3 if j==len(path)-1 else ts[j]+3,f'd{i}s{j}')
 for iv in lives.values():m.AddNoOverlap(iv)
 s=cp_model.CpSolver();s.parameters.num_workers=1;s.parameters.cp_model_presolve=False;s.parameters.max_time_in_seconds=seconds;m.Minimize(R);st=s.Solve(m)
 rec=dict(name=row['name'],resource_depth=depth,route_seed=seed,status=s.StatusName(st),seconds=s.WallTime(),bound=s.BestObjectiveBound(),paths=paths)
 if st not in(cp_model.OPTIMAL,cp_model.FEASIBLE):return rec
 r=s.Value(R);m.Add(R==r);exposure=7*R-sum(ai.values())-7-2*len(at)+14*depth # BC proxy includes all resource live ticks; actual gates unknown.
 m.Minimize(exposure+2*sum(len(x)for x in ht));st=s.Solve(m)
 if st not in(cp_model.OPTIMAL,cp_model.FEASIBLE):return dict(rec,tie_status=s.StatusName(st))
 rec.update(R=r,bc_init=s.Value(bs),a_init={q:s.Value(t)for q,t in ai.items()},a_times=[s.Value(t)for t in at],hop_times=[[s.Value(t)for t in ts]for ts in ht],data_hops=sum(map(len,ht)),exposure_proxy=s.Value(exposure),region=row['region'],final=row['final'],scope='fixed region, role split, A encoder, fixed data paths and ASAP prefix; atomic depth-d BC lifetime, no real BC synthesis yet')
 return rec
if __name__=='__main__':
 rows=json.loads((H/'labelled_regions.json').read_text());out=[];seen=set()
 # First pass: every geometry/class candidate receives the same deterministic route.
 for i,row in enumerate(rows):
  rec=schedule(row,11,0);rec['row_index']=i;out.append(rec)
  if 'R'in rec:print(json.dumps({k:rec[k]for k in('name','R','data_hops','exposure_proxy','row_index')}),flush=True)
 (H/'timed_regions_d11.json').write_text(json.dumps(out,indent=1))
