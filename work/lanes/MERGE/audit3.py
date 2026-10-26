from pass3 import *
from report3 import report
def audit(final=False):
 report(final)
 rows=json.loads((H/'results.json').read_text());checked=0
 for s,r in rows.items():
  if r['phase']!='v37d pass3':continue
  st=Path(r['stem']);assert st.with_suffix('.qasm').exists()and sha(st)==s,(s,st)
  assert json.loads(st.with_suffix('.json').read_text())['data_qubits']==r['data_qubits']
  checked+=1
 hist=json.loads((R/'bc3polish_history.json').read_text());menu=json.loads((R/'bc3polish_menu.json').read_text());base=M.read(C/'bc3_7')
 for r in hist:
  _,txt=M.apply_bundle(base,[menu[i]for i in r['selected']]);assert hashlib.sha256(txt.encode()).hexdigest()==r['price']['sha256']
 candidates=[]
 for p in (H/'cand').glob('*.json'):
  r=json.loads(p.read_text())
  if r.get('tau')!=TAU:continue
  assert sha(p.with_suffix(''))==r['sha256'];v=r['judge_1e6'];assert v['gates_ok']and v['speed_ok']and v['median_judge_seconds']<=4.8
  assert feasible(r)and r['loss']<TAU-5e-8;candidates.append(p.name)
 lines=(H/'REPORT.md').read_text().splitlines();assert len(lines)<=100 and max(map(len,lines))<2000
 if final:assert hist[-1]['stop']and hist[-1]['loss_gain']<1e-9
 out=dict(pass3_hashes=checked,total_hashes=len(rows),recipe_rounds=len(hist),candidate_files=candidates,report_lines=len(lines),max_line_chars=max(map(len,lines)),converged=hist[-1]['stop'],best=hist[-1]['price'])
 dump(R/'artifact_audit.json',out);print(json.dumps(dict(checked=checked,rounds=len(hist),candidates=len(candidates),report_lines=len(lines),converged=hist[-1]['stop'])),flush=True)
if __name__=='__main__':audit('--final'in sys.argv)
