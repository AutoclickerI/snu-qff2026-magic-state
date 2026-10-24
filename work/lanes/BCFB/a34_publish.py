from a34_summary import *
import shutil
rows,ranked=summarize();eligible=[r for r in rows if r['loss']<4.6629334817191845e-5 and r['acceptance']>=.5005 and r.get('verification',{}).get('passed')]
best=min(eligible,key=lambda r:r['loss']);stem=H/best['stem'];text=stem.with_suffix('.qasm').read_text();md=json.loads(stem.with_suffix('.json').read_text());sha=hashlib.sha256(text.encode()).hexdigest()
md.update(selection_source=best['stem'],qasm_sha256=sha,allorders={k:best[k] for k in ('loss','acceptance','omission_bound')},verification=best['verification'])
(H/'best.qasm').write_text(text);(H/'best.json').write_text(json.dumps(md,indent=2));(H/'BEST.json').write_text(json.dumps(dict(stem=best['stem'],qasm='best.qasm',metadata='best.json',qasm_sha256=sha,allorders=md['allorders'],verification=best['verification']),indent=2));print('PUBLISHED',best['stem'],sha)
