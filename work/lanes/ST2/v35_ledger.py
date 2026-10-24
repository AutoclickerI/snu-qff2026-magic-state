import sys,json,csv
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));import v35_campaign as v
base=json.loads((v.V/'base.detector_prices.json').read_text());out=[]
for row in base['detector_rows']:out.append(dict(name=f'detector_only/{row["row"]}',family='detector_only',**row))
for label in ('fasttrack','physical','additions'):
 for p in sorted((v.V/label).glob('*.score.json')):
  r=json.loads(p.read_text());out.append(dict(name=str(p.relative_to(v.V)).replace('.score.json',''),family=r['description']['family'],**r))
for r in out:
 if 'loss'in r:
  r['delta_loss']=r['loss']-base['base_loss'];r['acceptance_change']=r['acceptance']-base['base_acceptance']
  r['loss_per_acceptance']=r['delta_loss']/r['acceptance_change']if abs(r['acceptance_change'])>1e-15 else None
(v.V/'all_prices.json').write_text(json.dumps(dict(base_loss=base['base_loss'],base_acceptance=base['base_acceptance'],rows=out),indent=2))
with (v.V/'all_prices.csv').open('w')as f:
 keys=['name','family','loss','acceptance','delta_loss','acceptance_change','loss_per_acceptance','error'];w=csv.DictWriter(f,keys,extrasaction='ignore');w.writeheader();w.writerows(out)
print('LEDGER',len(out),'prices',sum('loss'in r for r in out),'rejected',sum('error'in r for r in out))
