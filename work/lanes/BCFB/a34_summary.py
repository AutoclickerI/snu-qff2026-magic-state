"""Consolidate measured results and physical aliases without inventing receipts."""
from a34_dedup import *

def summarize():
 rows=[];bykey={}
 for p in (D/'candidates').glob('*.allorders.json'):
  stem=Path(str(p).replace('.allorders.json',''));a=json.loads(p.read_text());m=json.loads(stem.with_suffix('.json').read_text());row=dict(stem=str(stem.relative_to(H)),loss=a['loss'],acceptance=a['acceptance'],CX=m['CX'],native_depth=m['native_depth'],options=m['options'],omission_bound=a['conditional_loss_kernel_omission_bound'])
  k=physical_key(stem);row['physical_key']=k
  if k in bykey:row['same_physics_as']=bykey[k]
  else:bykey[k]=row['stem']
  v=Path(str(stem)+'.verification.json')
  if v.exists():row['verification']=json.loads(v.read_text())
  s=Path(str(stem)+'.speed.json')
  if s.exists():row['speed']=json.loads(s.read_text())
  rows.append(row)
 rows.sort(key=lambda r:r['loss']);(D/'allorders_summary.json').write_text(json.dumps(rows,indent=2))
 eligible=[r for r in rows if r['loss']<4.6629334817191845e-5 and r['acceptance']>=.5005]
 ranked=[];seen=set()
 for r in eligible:
  if r['physical_key'] in seen:continue
  seen.add(r['physical_key']);ranked.append(r)
 print('TOTAL',len(rows),'UNIQUE',len(bykey),'ELIGIBLE',len(ranked))
 for r in ranked[:15]:print(r['stem'],r['loss'],r['acceptance'],r.get('speed',{}).get('classification'),r.get('verification',{}).get('passed'))
 (D/'ranked_unique.json').write_text(json.dumps(ranked,indent=2));return rows,ranked
if __name__=='__main__':summarize()
