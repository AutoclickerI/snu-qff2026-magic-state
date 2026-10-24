"""Exact memoization of unchanged sparse characteristic factors across keys.
No factor arithmetic or contraction order changes; cached arrays are immutable.
"""
import sys,time,json,contextlib,io
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));import acceptance as a
import numpy as np
sw=a.d.sw
cache={};states_ids={};masks={};hits=misses=nbytes=0

def factors_for(compiled,states,emask):
 global hits,misses,nbytes
 sid=states_ids.setdefault(states.tobytes(),len(states_ids));outer_cache={0:np.ones(len(states))};factors=[]
 for ci,(scope,p0,terms)in enumerate(compiled):
  if ci not in masks:
   mask=0
   for km,rm,e,p in terms:mask|=e
   masks[ci]=mask
  key=(sid,ci,emask&masks[ci])
  if key in cache:factors.append((scope,cache[key]));hits+=1;continue
  full=any(km for km,_,_,_ in terms);size=len(states)if full else 1
  ix=np.arange(1<<len(scope),dtype=np.uint32);vals=np.full((size,len(ix)),p0)
  for km,rm,e,p in terms:
   if km not in outer_cache:outer_cache[km]=1-2*(np.bitwise_count(states&km)&1).astype(np.int8)
   outer=outer_cache[km]if full else np.ones(1);inner=1-2*(np.bitwise_count(ix&rm)&1).astype(np.int8)
   vals+=(p*(-1 if(e&emask).bit_count()&1 else 1))*outer[:,None]*inner[None,:]
  vals=vals.reshape((size,)+(2,)*len(scope),order='F');vals.flags.writeable=False
  if nbytes+vals.nbytes<768*1024**2:cache[key]=vals;nbytes+=vals.nbytes
  factors.append((scope,vals));misses+=1
 return factors

def run(stem):
 global cache,states_ids,masks,hits,misses,nbytes
 cache={};states_ids={};masks={};hits=misses=nbytes=0;old=sw.factors_for;sw.factors_for=factors_for
 od=Path(stem).parent/'sparse_results'/Path(stem).name;od.mkdir(parents=True,exist_ok=True);sw.__file__=str(od/'sparse_walsh.py')
 try:
  with contextlib.redirect_stdout(io.StringIO()):r=sw.run(Path(stem),72,True,1)
 finally:sw.factors_for=old
 r['cache_stats']=dict(hits=hits,misses=misses,nbytes=nbytes,state_sets=len(states_ids))
 (od/(Path(stem).name+'_canonical_sparse_result.json')).unlink();od.rmdir();cache={};return r
if __name__=='__main__':
 r=run(sys.argv[1]);p=Path(sys.argv[1]);p.with_suffix('.cached.json').write_text(json.dumps(r,indent=2));print(json.dumps({k:v for k,v in r.items()if k!='results'}),flush=True)
