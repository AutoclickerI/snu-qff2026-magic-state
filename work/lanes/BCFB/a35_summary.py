from a35_prep import *
rows=[];errors=[];paths=sorted((D/'candidates').glob('*.allorders.json'))
for p in paths:
 stem=Path(str(p).replace('.allorders.json',''));a=json.loads(p.read_text());md=json.loads(stem.with_suffix('.json').read_text());r=dict(stem=str(stem.relative_to(H)),loss=a['loss'],acceptance=a['acceptance'],CX=md['CX'],native_depth=md['native_depth'],R=md['R'],options=md['options'],qasm_sha256=hashlib.sha256(stem.with_suffix('.qasm').read_bytes()).hexdigest(),physical_key=physical_key(stem),omission_bound=a['conditional_loss_kernel_omission_bound'])
 for tag in ['verification','speed','judge']:
  path=Path(str(stem)+'.'+tag+'.json')
  if path.exists():r[tag]=json.loads(path.read_text())
 rows.append(r)
rows.sort(key=lambda r:r['loss']);(D/'allorders_summary.json').write_text(json.dumps(rows,indent=2));print('prices',len(rows),'physical',len({r['physical_key'] for r in rows}))
for r in [r for r in rows if r['acceptance']>=.5005][:15]:print(r['stem'],r['loss'],r['acceptance'],r.get('verification',{}).get('passed'),r.get('speed',{}).get('classification'))
