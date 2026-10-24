"""Assemble verified marginal prices and solve interacting candidate knapsacks."""
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));import v34_campaign as v,knapsack_select as k

def assemble():
 a=v.a;c=v.d.normalize(v.C.read(v.V/'base'));od=v.V/'prices';od.mkdir(exist_ok=True);rows=[]
 ledger=json.loads((v.V/'base.detector_prices.json').read_text())
 for r in ledger['detector_rows']:
  x=v.C.clone(c);x['tail'].pop(r['row']);name=f'det_{r["row"]:02}';st=od/name;v.d.save(x,st)
  rr=dict(r,stem=str(st.relative_to(v.H)),description=dict(family='detector_only',row=r['row'],detector=r['detector']),ok=True,eligible=r['acceptance']>=.5005,c1=0,c1_note='not needed for all-orders price; singles audited separately on selected circuits',method=ledger['method'])
  st.with_suffix('.score.json').write_text(json.dumps(rr,indent=2));rows.append(rr)
 for name,x,desc in v.physical():
  st=v.V/'physical'/name
  if not st.with_suffix('.score.json').exists():continue
  v.d.save(x,st);r=json.loads(st.with_suffix('.score.json').read_text())
  if desc.get('audit'):continue
  rows.append(r)
 (od/'results.json').write_text(json.dumps(dict(rows=rows),indent=2));return rows
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--workers',type=int,default=5);args=p.parse_args();rr=assemble();print('assembled',len(rr),flush=True)
 def candidates():
  for n,c,r in k.proposals():yield n,c,dict(r,budget_screen=True)
 v.a.batch(candidates(),'selected',args.workers)
