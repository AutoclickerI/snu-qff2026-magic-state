"""Audit actual task coverage, immutable circuits, selected recipes and finalists."""
from pass5 import *

def audit():
 hf=R/'wide_history.json';history=json.loads(hf.read_text())
 assert history and history[-1]['stop'] and history[-1]['phase']=='complete widened neighborhood'
 tasks={};seen={};errors=[];stats=collections.Counter();families={}
 for p in sorted(R.glob('*_tasks.json')):
  tag=p.stem.removesuffix('_tasks');ledger=R/(tag+'.jsonl')
  if not ledger.exists():continue
  expected={tuple(x)for x in json.loads(p.read_text())};rows=[json.loads(l)for l in ledger.read_text().splitlines()];done={tuple(r['edits'])for r in rows};missing=expected-done
  # A strong improvement can end a prior neighborhood before it is expanded.
  required=tag.startswith('wide_r'+str(history[-1]['round'])+'_') or tag=='detector_v37h'
  tasks[tag]=dict(expected=len(expected),completed=len(expected&done),missing=len(missing),required_for_completion=required)
  if required:assert not missing,(tag,sorted(missing)[:10])
  for r in rows:
   stats['receipts']+=1
   if 'sha256'not in r:stats['edit_conflicts']+=1;continue
   st=Path(r['stem']);identity=r['sha256']+'|'+','.join(map(str,r['data_qubits']))
   if identity not in seen:
    assert sha(st)==r['sha256'],st
    assert json.loads(st.with_suffix('.json').read_text())['data_qubits']==r['data_qubits'],st
    seen[identity]=str(st)
   if 'loss'in r:
    assert len(r['raw_stabilizers'])==6 and all(abs(v-1)<1e-10 for v in r['raw_stabilizers']),st
    stats['numerical']+=1
   else:stats['evaluator_rejections']+=1
 for e in history:
  before=e['before'];current=e['price'];assert current['loss']<=before['loss']+1e-15 and feasible(current)
  if e['selected']:
   es=json.loads((R/f'wide_r{e["round"]}_menu.json').read_text());c,txt=apply(M.read(before['stem']),[es[i]for i in e['selected']]);assert hashlib.sha256(txt.encode()).hexdigest()==current['sha256'],e['round']
  assert current['judge_1e6']['gates_ok'] and current['judge_1e6']['speed_ok']
 finals=[]
 for p in sorted((H/'cand').glob('merge5_*.json')):
  r=json.loads(p.read_text());assert sha(p)==r['sha256'],p
  j=r.get('judge_1e6')
  if not j or not j.get('gates_ok') or not j.get('speed_ok'):continue
  assert feasible(r) and r['loss']<TAU-3e-8
  finals.append(dict(stem=str(p.with_suffix('')),sha256=r['sha256'],loss=r['loss'],acceptance=r['acceptance'],ratio=j['ratio'],expected_key_gain=TAU-r['loss']-j.get('expected_key_penalty',0)))
 outcome=dict(complete=True,rounds=len(history),last_gain=history[-1]['gain'],counts=dict(stats),unique_circuit_outputs=len(seen),task_coverage=tasks,finalists=finals,best=history[-1]['price'],unproven='Finite grammar only: larger rescheduling windows, more than four buyers, or nonlocal circuit architecture are not certified.')
 dump(R/'audit.json',outcome)
 print(json.dumps(dict(event='audit_complete',rounds=len(history),last_gain=outcome['last_gain'],counts=outcome['counts'],finalists=len(finals))),flush=True)
 return outcome
if __name__=='__main__':audit()
