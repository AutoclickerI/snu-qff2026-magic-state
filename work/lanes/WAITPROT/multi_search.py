"""Full-circuit forward/backward set search across beneficial storage intervals."""
import os,sys,json,itertools
from pathlib import Path
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
H=Path(__file__).resolve().parent
import tick_build as tb,moments,xtim
xtim.cache_dir=str(H/'.xtim_cache')
rows=json.loads((H/'tick_singles.json').read_text());pool={int(r['stem'][1:3]):r['gadgets'][0] for r in rows}
items=[0,3,9,10,12,15,19,22,24,26,29,33,36]
cache={};allrows=[]
def score(ids):
 ids=tuple(sorted(ids))
 if ids in cache:return cache[ids]
 gs=[pool[k] for k in ids]
 if not tb.compatible(gs):return None
 name='m_'+'_'.join(f'{k:02d}' for k in ids);p=tb.emit(name,gs)
 try:
  ev=tb.Eval(p.with_suffix('.qasm').read_text(),tb.DATA)
  acc=float(__import__('numpy').exp(-ev.fp@(1-ev.a_single)))
  if acc<.5002:r=dict(exp_minus_A1=acc,screened_acceptance=True)
  else:r=moments.evaluate(ev)
  r.update(stem=name,ids=ids,gadgets=gs)
 except Exception as e:r=dict(stem=name,ids=ids,error=repr(e))
 (H/(name+'.screen.json')).write_text(json.dumps(r));cache[ids]=r;allrows.append(r)
 return r if r.get('exp_minus_A1',0)>=.5002 else None
current=();best=5.823933151420156e-5;path=[]
while True:
 candidates=[]
 for i in items:
  ids=tuple(x for x in current if x!=i) if i in current else tuple(sorted((*current,i)))
  if not ids:continue
  r=score(ids)
  if r and r.get('exp_minus_A1',0)>=.5002 and 'total' in r:candidates.append(r)
 if not candidates:break
 r=min(candidates,key=lambda x:x['total'])
 if r['total']>=best-1e-12:break
 current=tuple(r['ids']);best=r['total'];path.append(r);print(json.dumps(r),flush=True)
# Four best complete sets are retained for unchanged reference/official gates.
valid=[r for r in allrows if r.get('exp_minus_A1',0)>=.5002 and 'total' in r];valid.sort(key=lambda x:x['total'])
for r in valid[:4]:tb.check(H/r['stem'])
(H/'multi_screen.json').write_text(json.dumps(allrows,indent=2));(H/'multi_reference.json').write_text(json.dumps(valid[:4],indent=2));print('evaluated',len(allrows),'best',valid[0]['stem'],best,flush=True)
