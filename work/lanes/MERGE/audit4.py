from pass4 import *
from functools import cache

@cache
def digest(path):
 return hashlib.sha256(Path(path).read_bytes()).digest()

def audit():
 receipts=[];errors=[];hashes=set();stems=set();contexts=set()
 for f in R.glob('*.jsonl'):
  for line in f.read_text().splitlines():
   r=json.loads(line)
   if 'sha256'not in r:continue
   receipts.append(r);st=Path(r['stem']);hashes.add(r['sha256']);contexts.add(r['evaluator_hash'])
   if str(st)not in stems:
    assert sha(st)==r['sha256'],st
    assert json.loads(st.with_suffix('.json').read_text())['data_qubits']==r['data_qubits'],st
    stems.add(str(st))
   assert r['cache_key']==r['sha256']+'|'+','.join(map(str,r['data_qubits']))+'|'+r['evaluator_hash']
   assert digest(r['evaluator_basis']).hex()==r['basis_sha256']
   settings={'warm':str(Path(r['evaluator_basis']).relative_to(H)),'width':12}
   expected=hashlib.sha256(b''.join(digest(E.SP/f)for f in ('sparse_walsh.py','frontend.py','fastfill.py'))+digest(r['evaluator_basis'])+digest(H/'ev37.py')+json.dumps(settings,sort_keys=True).encode()).hexdigest()[:16]
   assert expected==r['evaluator_hash'],(expected,r['evaluator_hash'])
   if 'loss'in r:assert len(r['raw_stabilizers'])==6 and max(abs(x-1)for x in r['raw_stabilizers'])<1e-10
 hist=json.loads((R/'wide_history.json').read_text());assert hist[-1]['stop']and hist[-1]['gain']<1e-9 and hist[-1]['phase']=='complete widened neighborhood'
 for h in hist:
  r=h['price'];before=h['before'];es=json.loads((R/f"wide_r{h['round']}_menu.json").read_text())
  plan,txt=apply(M.read(before['stem']),[es[i]for i in h['selected']]);assert hashlib.sha256(txt.encode()).hexdigest()==r['sha256']
  assert r['loss']<=before['loss']and r['acceptance']>=FLOOR
  assert h['gain']==before['loss']-r['loss']
  jf=R/f"judge_{r['sha256']}.json";j=json.loads(jf.read_text());assert j['gates_ok']and j['speed_ok']
  assert j['ratio']<=1.5 and all(x['procs']==1 and x['shots']==10**6 for x in j['judge_runs']+j['baseline_runs'])
 completed_stages={}
 for h in hist:
  if h['phase']!='complete widened neighborhood':continue
  tag=f"wide_r{h['round']}"
  for tasks in R.glob(tag+'*_tasks.json'):
   stage=tasks.name[:-len('_tasks.json')];out=R/(stage+'.jsonl')
   assert out.exists(),stage
   expected={tuple(x)for x in json.loads(tasks.read_text())};actual={tuple(json.loads(x)['edits'])for x in out.read_text().splitlines()}
   assert expected<=actual,(stage,len(expected-actual));completed_stages[stage]=len(expected)
 candidates=[]
 for p in (H/'cand').glob('merge4_*.json'):
  r=json.loads(p.read_text());assert sha(p)==r['sha256']and feasible(r)and r['loss']<TAU-3e-8
  assert r['judge_1e6']['gates_ok']and r['judge_1e6']['ratio']<=1.5;candidates.append(p.name)
 lines=(H/'REPORT.md').read_text().splitlines();assert len(lines)<=100 and max(map(len,lines))<2000
 out=dict(receipts=len(receipts),qasm_hashes=len(hashes),saved_stems=len(stems),evaluator_contexts=sorted(contexts),rounds=len(hist),last_gain=hist[-1]['gain'],candidates=candidates,report_lines=len(lines),completed_final_stages=completed_stages,errors=errors)
 if (R/'resume_artifact.json').exists():
  a=json.loads((R/'resume_artifact.json').read_text());b=json.loads((R/'resume_v37g_reproduction.json').read_text());j=a['judge_1e6']
  assert sha(H/'cand'/a['name'])==a['sha256']==hist[-1]['price']['sha256']
  assert a['loss']==hist[-1]['price']['loss'] and a['acceptance']==hist[-1]['price']['acceptance']
  assert j['baseline']=='v37g' and j['baseline_sha256']==b['sha256']
  assert j['gates_ok']and j['speed_ok']and j['ratio']<=1.5
  for r in j['judge_runs']+j['baseline_runs']:
   assert r['host']==j['host']and r['shots']==10**6 and r['procs']==1 and r['gates_ok']
   assert 'gates_ok=True'in r['stdout']
   assert r['format_ok']and r['class_ok']
   assert r['fast_check_sha256']==digest(H/'judge_snapshot/fast_check.py').hex()
  assert a['qualifies_vs_v37g']==(a['loss']<b['loss']-3e-8)
  assert a['gain_from_v37g']==b['loss']-a['loss']
  ledger=json.loads((H/'results.json').read_text())
  for r in receipts:
   x=ledger[r['sha256']];variants=[x]+list(x.get('ordered_output_variants',{}).values())
   assert any(v.get('data_qubits')==r['data_qubits']and (('loss'not in r and 'error'in v)or('loss'in r and 'loss'in v and abs(v['loss']-r['loss'])<1e-12 and abs(v['acceptance']-r['acceptance'])<1e-12))for v in variants),r['sha256']
  fronts=json.loads((R/'resume_pareto4.json').read_text())
  for rnd in [3,4]:
   for name,front in fronts[f'wide_r{rnd}'].items():
    for values in (front.values()if isinstance(front,dict)else[front]):
     assert all(y['loss']>=x['loss']and y['acceptance']>x['acceptance']for x,y in zip(values,values[1:]))
  out.update(baseline_sha256=b['sha256'],new_finalists=int(a['qualifies_vs_v37g']),
             gain_from_v37g=a['gain_from_v37g'],judge_ratio=j['ratio'],ledger_entries=len(ledger))
  dump(R/'resume_audit.json',out)
 dump(R/'final_audit.json',out);print(json.dumps(out),flush=True)
if __name__=='__main__':audit()
