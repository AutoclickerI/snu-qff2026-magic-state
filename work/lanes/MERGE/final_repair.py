from campaign import *
from merge_build import menu
from greedy_pass import eligible,make_tasks,run_tasks,choose
def fullmenu(c):
 es=menu(c)
 for p in M.pairs(c,M.status(c)):
  for a,b in [(p['a'],p['b']),(p['b'],p['a'])]:
   e=M.mk(fam='pair',g=dict(kind='pair',a=a,b=b,t=p['t']));es[e['id']]=e
 return es
def main():
 sources=[H/'res'/f'{n}.jsonl' for n in ['greedy_joint_local','refresh_expanded_local','final_refresh_local']]
 rows=[json.loads(l) for f in sources for l in f.read_text().splitlines()]
 current=choose(rows);base=M.read(current['stem']);start=dict(current)
 # Regenerate each previously useful recipe on the actual refreshed circuit.
 old=price(H/'builds/CPGcore_read','final repair reference')
 singles=[json.loads(l) for host in ['local','hippo'] for l in (H/'res'/f'cpg_scan_{host}.jsonl').read_text().splitlines()]
 ids={r['what_moved']['edits'][0] for r in singles if eligible(r,old)}
 ids|={'cx:32_33@37','pair:24_25@22','shift:CX19_25@19>20','rmcx:7_6@5','rmcx:19_25@13'}
 es=fullmenu(base);present=sorted(ids&es.keys());missing=sorted(ids-es.keys())
 write(H/'res/final_repair_menu.json',es);write(H/'res/final_repair_regeneration.json',dict(base=current['stem'],available=present,changed_or_consumed=missing))
 tasks=make_tasks(base,[[i] for i in present],es,'final_repair_scan')
 print(json.dumps(dict(event='final_repair_start',base=current['stem'],loss=current['loss'],tasks=len(tasks))),flush=True)
 receipts=[H/'res'/f'final_repair_scan_{host}.jsonl' for host in ['local','hippo']]
 prior=[json.loads(l) for f in receipts if f.exists() for l in f.read_text().splitlines()]
 wanted={Path(t['stem']).name for t in tasks}
 recorded={Path(r['stem']).name for r in prior}
 if wanted<=recorded:rows=prior
 else:rows=run_tasks(tasks,'final_repair_scan')
 moves=sorted([r for r in rows if 'loss' in r and r['J_tau']<start['J_tau']-5e-14],key=lambda r:r['J_tau'])
 history=[]
 for candidate in moves:
  i=candidate['what_moved']['edits'][0]
  try:
   fresh=fullmenu(M.read(current['stem']))
   if i not in fresh:history.append(dict(edit=i,status='changed/consumed'));continue
   c,_=M.apply_bundle(M.read(current['stem']),[fresh[i]])
   st=save(c,'final_greedy_'+str(len(history)),f'final refreshed greedy extension {i}')
   r=price(st,dict(stage='final_greedy',edit=i,base=current['stem']))
   accepted=bool('loss'in r and r['acceptance']>=FLOOR and r['J_tau']<current['J_tau']-5e-14)
   history.append(dict(edit=i,accepted=accepted,price=r))
   if accepted:current=r
  except Exception as ex:history.append(dict(edit=i,error=repr(ex)))
 st=snapshot(current['stem'],'final_repaired')
 write(H/'res/final_repair_outcome.json',dict(start=start,best=current,stem=str(st),history=history,scan_count=len(rows),regenerated=len(present)))
 print(json.dumps(dict(event='final_repair_complete',best=current,accepted=sum(r.get('accepted',False) for r in history))),flush=True)
if __name__=='__main__':main()
