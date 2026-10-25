from campaign import *
def collect():
 rows={}
 for f in sorted((H/'res').glob('*.jsonl')):
  for ln in f.read_text().splitlines():
   try:r=json.loads(ln)
   except json.JSONDecodeError:continue
   if 'sha256' not in r:continue
   s=r['sha256'];old=rows.get(s,dict(r,aliases=[]))
   alias=dict(stem=r.get('stem'),what_moved=r.get('what_moved'))
   if alias not in old['aliases']:old['aliases'].append(alias)
   rows[s]=old
 for s,r in rows.items():
  if 'loss' in r:r['J_tau']=r['acceptance']*(r['loss']-TAU)
 runtime=json.loads((H/'res/runtime_status.json').read_text()) if (H/'res/runtime_status.json').exists() else {}
 for s,v in runtime.items():
  if s in rows:rows[s]['runtime']=v
 write(H/'results.json',rows)
 good=sorted([r for r in rows.values() if 'loss' in r and r['acceptance']>=FLOOR and r.get('runtime',{}).get('eligible',True)],key=lambda r:r['J_tau'])
 print(json.dumps(dict(priced=len(rows),valid=sum('loss' in r for r in rows.values()),best=[dict(stem=r['stem'],loss=r['loss'],acceptance=r['acceptance'],J_tau=r['J_tau'],sha256=r['sha256'],what_moved=r.get('what_moved')) for r in good[:12]]),indent=2))
if __name__=='__main__':collect()
