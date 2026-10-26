"""Decisive same-minute one-process comparison after the search workers exit."""
from pass5 import *
from judge5 import one
import statistics,math,socket
hist=json.loads((R/'wide_history.json').read_text());assert hist[-1]['stop']
best=hist[-1]['price'];paths={'v37h':C/'base','lowest_loss':Path(best['stem'])}
for name in ['merge5_live_a449e1a694c1','merge5_live_40b4766b3e14','merge5_live_31c271d37407','merge5_live_8f4b236e8e56']:
 st=H/'cand'/name
 if st.with_suffix('.qasm').exists()and sha(st)not in [sha(p)for p in paths.values()]:paths[name]=st
runs={n:[]for n in paths};order=list(paths)
for k in range(3):
 for n in order[k:]+order[:k]:
  r=one(paths[n]);runs[n].append(r);print(json.dumps(dict(event='final_paired_judge',name=n,seconds=r['seconds'],gates_ok=r['gates_ok'])),flush=True)
bs=statistics.median(r['seconds']for r in runs['v37h']);out=[]
for n,st in paths.items():
 if n=='v37h':continue
 r=best if n=='lowest_loss'else json.loads(st.with_suffix('.json').read_text());cs=statistics.median(x['seconds']for x in runs[n]);j=dict(sha256=sha(st),host=socket.gethostname(),gates_ok=all(x['gates_ok']for x in runs[n]),speed_ok=cs<=20,median_seconds=cs,baseline_median_seconds=bs,ratio=cs/bs,expected_key_penalty=1.1e-7*math.log2(cs/bs),judge_runs=runs[n],baseline_runs=runs['v37h'])
 out.append(dict(name=n,stem=str(st),sha256=sha(st),loss=r['loss'],acceptance=r['acceptance'],gain=TAU-r['loss'],judge_1e6=j,expected_key_gain=TAU-r['loss']-j['expected_key_penalty']))
 if n=='lowest_loss':
  dest=H/'cand'/f'merge5_final_{r["sha256"][:12]}';shutil.copyfile(st.with_suffix('.qasm'),dest.with_suffix('.qasm'));dump(dest.with_suffix('.json'),dict(r,judge_1e6=j,status='finalist',qualifies_vs_v37h=bool(feasible(r)and r['loss']<TAU-3e-8 and j['gates_ok']and j['speed_ok']),gain_from_v37h=TAU-r['loss'],source='converged pass5; decisive post-search paired timing'))
 else:
  meta=json.loads(st.with_suffix('.json').read_text());meta['final_paired_judge_1e6']=j;dump(st.with_suffix('.json'),meta)
dump(R/'final_paired_timing.json',dict(host=socket.gethostname(),baseline_sha256=sha(C/'base'),baseline_median_seconds=bs,candidates=out,expected_key_recommendation=max(out,key=lambda r:r['expected_key_gain'])['name'],note='Exact loss selects finalists; expected-key approximation informs main-session promotion.'))
print(json.dumps(dict(event='final_timing_complete',ranking=[(r['name'],r['expected_key_gain'])for r in sorted(out,key=lambda r:-r['expected_key_gain'])])),flush=True)
