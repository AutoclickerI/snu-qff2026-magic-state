"""Exact joint region ablations using the same model; no additive gadget assumptions.
Region split is diagnostic. Reference ranking comes from unchanged exact2 CLI.
"""
import os,sys,json,math
from pathlib import Path
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
import tick_build as tb
sys.path.insert(0,str(ROOT/'work/lanes/FRESH'))
import moments,numpy as np,xtim
xtim.cache_dir=str(H/'.xtim_cache')
def evaluate(stem):
 md=json.loads((H/(stem+'.json')).read_text());gs=md.get('protected',[]);text=(H/(stem+'.qasm')).read_text();ev=tb.Eval(text,tb.DATA)
 inserted=set();ln=len(tb.HEADER)+1
 for t,orig in enumerate(tb.BLOCKS):
  ln+=len(orig)
  for k,g in enumerate(gs):
   for tt,qs,ls in tb.extra_ops(g,264+k):
    if tt==t:
     inserted.update(range(ln,ln+len(ls)));ln+=len(ls)
  if t<len(tb.BARRIERS):ln+=1
 cats=[]
 for ci,ch in enumerate(ev.m.chans):
  lab=ev.chan_label(ci);gap=ch['gap'];q=ch['qubits'][0];cat='other'
  if gap is not None:
   q,first,n=gap;last=first+n-1
   if any(q==g['h'] and g['reset']<=first<=last<=g['measure'] for g in gs):cat='helper'
   elif first>=18 and last<48 and any(cell==q and ta<=first<=last<=tb_ for path in tb.TRAJECTORIES.values() for cell,ta,tb_ in path):cat='wait'
   elif first>=48:cat='round'
  elif lab['line'] in inserted:cat='helper'
  elif ev.m.steps[ch['ins']] and ev.m.steps[ch['ins']][0][1]>=48:cat='round'
  cats.append(cat)
 cats=np.array(cats);fp=ev.fp.copy()
 def price(allowed):
  ev.fp=fp*np.isin(cats[ev.fch],allowed)
  return moments.evaluate(ev)
 groups=['wait','round','helper','other'];prices={}
 for mask in range(16):
  allowed=[c for i,c in enumerate(groups) if mask>>i&1];prices[str(mask)]=price(allowed)
 ev.fp=fp
 full=prices['15'];out=dict(stem=stem,groups=groups,full=full,prices=prices,
  wait_only_weight3=prices['1']['T3a'],
  wait_round_pairs=prices['3']['second']-prices['1']['second']-prices['2']['second'],
  helper_containing_pairs=full['second']-prices['11']['second'],
  helper_containing_weight3=full['T3a']-prices['11']['T3a'],
  wait_containing_weight3=full['T3a']-prices['14']['T3a'],
  helper_full_minus_nohelper=full['total']-prices['11']['total'],
  channel_counts={c:int(sum(cats==c)) for c in groups})
 (H/(stem+'.decomposition.json')).write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items() if k!='prices'}),flush=True)
 return out
if __name__=='__main__':
 for stem in sys.argv[1:]:evaluate(stem)
