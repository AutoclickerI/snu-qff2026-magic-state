"""All-geometry scheduling relaxation with free instantaneous data relocation.

The bound preserves prefix final-release times and fragment per-wire order;
it removes every data-route collision and transfer cost. It is conditional on
the emitter's final-release reuse model, not a universal circuit bound.
"""
from endstate_emit import *
import argparse
p=argparse.ArgumentParser();p.add_argument('endstate');p.add_argument('--prefix',default='v29');p.add_argument('--out',required=True);a=p.parse_args();d=json.loads(Path(a.endstate).read_text());pre,tail,data=prefix(a.prefix);release={}
for o in pre:
 for q in unit(o).qs:release[q]=max(release.get(q,0),o['t']+1)
rows=[];seen=set()
for ch in choices(d,a.prefix):
 key=(ch['prefix_row'],ch['prefix_col'],ch['sym'],ch['end_row'],ch['end_col'])
 if key in seen:continue
 seen.add(key);rel={transform(q,0,ch['prefix_row'],ch['prefix_col']):t for q,t in release.items()};free=collections.defaultdict(int,rel);cause={q:('prefix_release',q,t)for q,t in rel.items()};frag,_,rs=fragment(d,ch['sym'],0,ch['end_row'],ch['end_col']);trace=[]
 # All preparation operations, before the canonical simultaneous round.
 for i,o in enumerate(frag[:rs]):
  qs=unit(o).qs;q=max(qs,key=lambda q:free[q]);t=free[q];trace.append(dict(index=i,t=t,lines=o['lines'],blocking_predecessor=cause.get(q)))
  for q in qs:free[q]=t+1;cause[q]=('fragment',i,t)
 ready=[transform(q,ch['sym'],ch['end_row'],ch['end_col'])for k in('a','b','c')for q in d['final'][k]];R=max(max(release.values()),*(free[q]for q in ready));rows.append(dict(choice=ch,R_lower_bound=R,critical_preparation=trace))
out=dict(prefix=a.prefix,source=str(Path(a.endstate).resolve()),minimum_R_lower_bound=min(r['R_lower_bound']for r in rows),geometries=len(rows),rows=rows,scope=__doc__)
Path(a.out).write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items()if k!='rows'}),flush=True)
