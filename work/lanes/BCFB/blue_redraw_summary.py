import json,statistics,math
from pathlib import Path
H=Path(__file__).resolve().parent;D=H/'blue'
def summarize():
 groups={};sources={}
 for f in sorted((D/'runs').glob('*_redraw_*.jsonl')):
  stem=f.name.rsplit('_redraw_',1)[0];rows=groups.setdefault(stem,{});sources.setdefault(stem,[]).append(str(f.relative_to(H)))
  for line in f.read_text().splitlines():
   try:r=json.loads(line)
   except ValueError:continue
   k=r['draw']
   if k in rows:assert r==rows[k],(stem,k)
   rows[k]=r
 out={}
 for stem,rows in groups.items():
  if not rows:continue
  rr=[rows[k] for k in sorted(rows)];n=len(rr);out[stem]=dict(draws=n,complete100=set(range(100))<=set(rows),mean=statistics.mean(r['score'] for r in rr),sem=statistics.stdev(r['score'] for r in rr)/math.sqrt(n) if n>1 else None,min_acceptance=min(r['acceptance'] for r in rr),draw_ids=sorted(rows),sources=sources[stem])
 (D/'redraw_summary.json').write_text(json.dumps(out,indent=2));return out
if __name__=='__main__':
 for k,v in summarize().items():print(k,{q:r for q,r in v.items() if q not in ('draw_ids','sources')})
