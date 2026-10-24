import os,sys,json,random,time,argparse
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
H=Path(__file__).resolve().parent;sys.path.insert(0,str(H.parent/'DR'));import synth
GENS=[[0,2,4,6],[1,2,5,6],[3,4,5,6]]
p=argparse.ArgumentParser();p.add_argument('layout');p.add_argument('--out',required=True);p.add_argument('--samples',type=int,default=2000);z=p.parse_args();d=json.loads(Path(z.layout).read_text());results={}
def connected(cells,avail):
 seen={cells[0]}
 for _ in avail:seen|={v for q in seen for v in synth.nbrs(q) if v in avail}
 return set(cells)<=seen
for tag,cells,avail,rows in [('a',d['a'],sorted(set(d['F'])-set(d['b'])),GENS+[[0,1,2]]),('b',d['b'],d['F'],GENS),('c',d['c'],sorted(set(d['F'])-set(d['b'])),GENS)]:
 if not connected(cells,avail):print(tag,'disconnected');continue
 best=None;front=[]
 for seed in range(z.samples):
  rng=random.Random(seed);order=list(range(len(rows)));rng.shuffle(order)
  try:ops,piv=synth.greedy([{cells[i] for i in r} for r in rows],avail,order,rng)
  except (ValueError,TypeError):continue
  layers=[];ts={q:0 for q in avail}
  for u,v in ops:
   t=max(ts[u],ts[v]);ts[u]=ts[v]=t+1
   while len(layers)<=t:layers.append([])
   layers[t].append([u,v])
  cand=dict(ops=layers,pivots=piv,cx=len(ops),depth=len(layers),seed=seed,avail=avail,cells=cells)
  if tag=='a':cand['danger']=synth.dangerous_z(layers,piv,cells,avail)
  score=(cand['depth'],cand.get('danger',0),cand['cx'])
  if best is None or score<best[0]:best=score,cand
  if tag=='a' and cand['depth']<=18:front.append(cand)
 results[tag]=best[1];print(tag,{k:v for k,v in best[1].items() if k not in ['ops','pivots','avail','cells']},flush=True)
 Path(z.out+f'_{tag}.json').write_text(json.dumps(best[1],indent=2)+'\n')
 if front:Path(z.out+'_a_front.json').write_text(json.dumps(sorted(front,key=lambda c:(c['danger'],c['depth'],c['cx']))[:100],indent=2)+'\n')
Path(z.out+'.summary.json').write_text(json.dumps({k:{q:v for q,v in d.items() if q!='ops'} for k,d in results.items()},indent=2)+'\n')
