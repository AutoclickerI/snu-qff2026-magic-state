"""Index the full standalone menu by physical data wait and its Pareto frontier."""
from v35_build import *
menu=json.loads((H/'menu_v35a.json').read_text());mapping=json.loads((V/'windows.json').read_text())
rows=[]
for window in mapping['windows']:
 q=window['q'];lo,hi=window['idle']
 logical=next((d for d,path in PATHS.items()for cell,a,z in path if cell==q and a<=lo<=hi<=z),None)
 if logical is None:continue
 matches=[]
 for row in menu['entries']:
  if not row['ok']:continue
  touched=False
  for change in row['lines']['add']:
   if lo<=change['t']<=hi and any(s.startswith('cx ')and q in map(int,re.findall(r'q\[(\d+)\]',s))for s in change['lines']):touched=True
  if touched:matches.append(row)
 frontier=[]
 for r in matches:
  if any(s['loss']<r['loss']-1e-13 and s['acceptance']>=r['acceptance']-1e-10 or s['loss']<=r['loss']+1e-13 and s['acceptance']>r['acceptance']+1e-10 for s in matches):continue
  frontier.append(r)
 def brief(r):return{k:r[k]for k in ['gadget','loss','acceptance','loss_gain','acceptance_cost','gain_per_acceptance','eligible']}
 rows.append(dict(logical_output=logical,stored_cell=q,idle=[lo,hi],standalone_prices=len(matches),all_candidate_ids=[r['gadget']for r in matches],frontier=[brief(r)for r in sorted(frontier,key=lambda r:r['loss'])],best_loss=brief(min(matches,key=lambda r:r['loss']))if matches else None,acceptance_free_gains=[brief(r)for r in sorted(matches,key=lambda r:r['loss'])if r['loss_gain']>1e-13 and r['acceptance_cost']<=0]))
(H/'menu_v35a_by_run.json').write_text(json.dumps(dict(base_sha256=BASE_SHA,note='Indexed by physical CXs added within each mapped data idle run. Marginals remain full-circuit standalone prices. The frontier ignores resource compatibility only for display; the full menu retains all candidates and exact patches.',runs=rows),indent=2)+'\n')
print('RUN_MENU',len(rows),'with proposals',sum(bool(r['all_candidate_ids'])for r in rows))
