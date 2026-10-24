"""Port moves.py's three phase-transfer choices to the current physical hops."""
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));import pop35_support as v
rr=[json.loads(p.read_text())for p in v.OUT.glob('*/*.score.json')];rr=[r for r in rr if r.get('eligible')and'loss'in r];best=min(rr,key=lambda r:r['loss']);base=v.C.read(v.H/best['stem'])
def proposals():
 for mask in range(8):
  c=v.C.clone(base);changes=[]
  for j,(q,t,qq,tt)in enumerate([(10,42,4,31),(16,34,22,37),(8,30,21,39)]):
   i=next(i for i,u in enumerate(c['u'])if u.name=='TDG'and u.qs[0]in(q,qq));target,time=(qq,tt)if mask>>j&1 else(q,t);changes.append(dict(old=c['u'][i].lines,old_time=c['t'][i],target=target,time=time));c['u'][i]=v.C.Unit([f'tdg q[{target}];']);c['t'][i]=time
  yield f'phase_{mask:03b}',c,dict(family='phase_hop',parent=best['stem'],changes=changes,budget_screen=True)
v.a.batch(proposals(),'phase',7)
