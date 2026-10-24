"""Close causal multi-unit timing shifts using the full pair-plus-cubic objective."""
from temporal import *
import concurrent.futures,multiprocessing as mp
QMODEL=None
def evaluate_times(ts):return tuple(ts),QMODEL.score(ts)

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('stem');ap.add_argument('--label',default='cone');ap.add_argument('--workers',type=int,default=6);a=ap.parse_args();base=read(a.stem);q=Cubic(base);QMODEL=q;ts=base['t'][:];pred,succ=S.build_dag(base['u']);horizon=max(ts)+2
 cur=q.score(ts);ref=base['meta']['lns_result'];err=max(abs(cur[k]-ref[k])for k in ('second','third','total'));assert err<1e-14
 # Prioritize the cells in the largest measured idle triples, but inspect all
 # units before claiming closure. A shift propagates to every causal neighbor.
 focus={0,3,10,7,20,9,1,16,21};order=sorted(range(len(ts)),key=lambda i:not bool(set(base['u'][i].qs)&focus));seen={tuple(ts):cur};trace=[];rounds=0;initial=cur
 pool=concurrent.futures.ProcessPoolExecutor(a.workers,mp_context=mp.get_context('fork'))
 while True:
  rounds+=1;winner=None;best=cur;tried=0;proposals=[];pending={}
  for i in order:
   for delta in [-6,-3,-2,-1,1,2,3,6]:
    nt=shift(ts,i,delta,pred,succ,horizon)
    if nt is None or nt==ts:continue
    # Skip a proven equivalent pure phase move, without skipping cones that
    # also retime other operations or change occupied native layers.
    if base['u'][i].name in ('T','TDG') and set(nt)==set(ts) and sum(x!=y for x,y in zip(nt,ts))==1:continue
    key=tuple(nt)
    if key not in seen:pending[key]=nt
    proposals.append((key,i,delta));tried+=1
  for key,v in pool.map(evaluate_times,pending.values(),chunksize=8):seen[key]=v
  for key,i,delta in proposals:
    v=seen[key];nt=list(key)
    if v['exp_minus_A1']>=.505 and v['total']<best['total']-1e-12:best=v;winner=(nt,i,delta)
  print(json.dumps(dict(round=rounds,proposals=tried,current=cur,best=best)),flush=True)
  if winner is None:break
  ts,i,d=winner;cur=best;trace.append(dict(round=rounds,unit=i,delta=d,score=cur))
  c=clone(base);c['t']=ts;c=normalize(c);independent=score(textof(c));assert max(abs(cur[k]-independent[k])for k in ('second','third','total'))<1e-14
  checkpoint=dict(desc=dict(family='triple',move='causal_cone_checkpoint',source=a.stem,parent_total=initial['total'],round=rounds,unit=i,delta=d),**independent,stem=f'{a.label}_r{rounds}');save(checkpoint['stem'],textof(c),c['meta'],checkpoint);report();print(json.dumps(checkpoint),flush=True)
 pool.shutdown()
 c=clone(base);c['t']=ts;c=normalize(c);independent=score(textof(c));err=max(abs(cur[k]-independent[k])for k in ('second','third','total'));assert err<1e-14
 row=dict(desc=dict(family='triple',move='causal_cone_local_closure',source=a.stem,parent_total=initial['total'],rounds=rounds,unique=len(seen)),**independent,stem=a.label+'_best');save(row['stem'],textof(c),c['meta'],row)
 (OUT/(a.label+'.jsonl')).write_text(json.dumps(row)+'\n');(OUT/(a.label+'.certificate.json')).write_text(json.dumps(dict(source=a.stem,initial=initial,final=independent,rounds=rounds,unique=len(seen),trace=trace,scope='All native units; causal predecessor/successor cone shifts by -6,-3,-2,-1,1,2,3,6, fixed per-wire order, original maximum step+2, exp(-A1)>=0.505, strict objective improvement >1e-12. Analytically equivalent pure-phase idle relocations are skipped. Not arbitrary joint retimings.',independent_error=err),indent=2));report();print('DONE',json.dumps(row),flush=True)
