"""Enumerate every one-node shift/conflict swap and two-node time swap near the winner."""
from cycles import *
import multiprocessing as mp
from evaluate import screen_one

def score_neighbor(job):
 name,row=job;m=Cycle(row['layout'],row['leaves'],row['orient']);ts=row['times'];text=m.text(ts)
 rep=tprep.check(text,m.pos,shots=10**6,seed=0);assert rep.passed,str(rep)
 row.update(data_qubits=m.pos,nodes=m.nodes,detectors=m.detectors,nbits=m.nbits,depth=max(ts)+1,prefix_audit=audit(text),check=dict(passed=rep.passed,score=rep.score,acceptance=rep.acceptance,shots=10**6,report=str(rep)))
 (HERE/f'{name}.qasm').write_text(text);(HERE/f'{name}.json').write_text(json.dumps(row,indent=2));return screen_one(name)

if __name__=='__main__':
 row=json.loads((HERE/'cycle_0058.json').read_text());m=Cycle(row['layout'],row['leaves'],row['orient']);ts=row['times'];seen={tuple(ts)};jobs=[];counts=dict(raw=0,feasible=0,deterministic=0)
 trials=[]
 for j in range(len(ts)):
  for t in range(m.lower[j],max(ts)+2):
   if t==ts[j]:continue
   for swap in (False,True):
    tt=list(ts);tt[j]=t
    if swap:
     for k,(_,qs,_) in enumerate(m.nodes):
      if j!=k and ts[k]==t and set(qs)&set(m.nodes[j][1]):tt[k]=ts[j]
    trials.append((tt,dict(kind='shift',node=j,to=t,conflict_swap=swap)))
 for j in range(len(ts)):
  for k in range(j):
   tt=list(ts);tt[j],tt[k]=tt[k],tt[j];trials.append((tt,dict(kind='swap',nodes=[j,k])))
 for tt,change in trials:
  counts['raw']+=1;tt=m.norm(tt)
  if tuple(tt) in seen:continue
  seen.add(tuple(tt))
  if not m.valid(tt):continue
  counts['feasible']+=1;cost=m.cost(tt)
  if cost is None:continue
  counts['deterministic']+=1
  name=f'neighbor_{len(jobs):03d}';r=dict(layout=m.layout,leaves=m.leaves,orient=m.orient,times=tt,proxy=cost,proxy_second=ep.exact_loss(*m.probes(tt)),source='cycle_0058',change=change)
  jobs.append((name,r))
 (HERE/'neighbor_manifest.json').write_text(json.dumps(dict(counts=counts,jobs=[dict(name=n,proxy=r['proxy'],change=r['change']) for n,r in jobs]),indent=2));print(counts,flush=True)
 with mp.get_context('fork').Pool(3) as pool:results=list(pool.imap_unordered(score_neighbor,jobs))
 results.sort(key=lambda r:r['loss']);(HERE/'neighbor_results.json').write_text(json.dumps(results,indent=2));print('BEST',results[:8],flush=True)
