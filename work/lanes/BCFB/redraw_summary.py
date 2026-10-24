"""Merge completed draws, not partial sample chunks; no duplicated re-draw IDs."""
import json,statistics,math
from pathlib import Path
H=Path(__file__).resolve().parent

def summarize():
 out={}
 for stem,files in json.loads((H/'redraw_manifest.json').read_text()).items():
  rows={}
  for f in files:
   p=H/f
   if not p.exists():continue
   for line in p.read_text().splitlines():
    if not line.startswith('{"draw"'):continue
    r=json.loads(line);k=r['draw']
    if k in rows:assert rows[k]['score']==r['score'] and rows[k]['acceptance']==r['acceptance']
    rows[k]=r
  if not rows:continue
  ys=[r['score'] for r in rows.values()];r=dict(draws=len(ys),mean=statistics.mean(ys),sd=statistics.stdev(ys) if len(ys)>1 else None,sem=statistics.stdev(ys)/math.sqrt(len(ys)) if len(ys)>1 else None,min_acceptance=min(r['acceptance'] for r in rows.values()),complete100=set(range(100))<=set(rows),indices=sorted(rows));out[stem]=r
 (H/'redraw_summary.json').write_text(json.dumps(out,indent=2));return out
if __name__=='__main__':
 for stem,r in summarize().items():print(stem,r['draws'],r['mean'],r['sem'],r['complete100'])
