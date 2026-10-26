"""Refresh review status from immutable receipts and complete judge-verification records."""
from wide5 import *
hist=json.loads((R/'wide_history.json').read_text());candidates=[]
for p in (H/'cand').glob('merge5_*.json'):
 r=json.loads(p.read_text());j=r.get('judge_1e6',{})
 if feasible(r) and j.get('gates_ok')and j.get('speed_ok'):candidates.append(r)
best=min(candidates+[hist[-1]['price']],key=lambda r:r['loss']);update_status('running',best,hist,phase='best verified publication; widened convergence work still running')
print(json.dumps(dict(event='status_refreshed',loss=best['loss'],acceptance=best['acceptance'],sha256=best['sha256'],history_rounds=len(hist))),flush=True)
