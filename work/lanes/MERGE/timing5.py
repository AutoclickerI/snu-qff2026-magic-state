from pass5 import *
from judge5 import one
import statistics,math,socket
names=['merge5_live_ee3c93a6dab9','merge5_live_ea238a8c3052','merge5_live_1c4b23e89b48']
paths={'v37h':C/'base',**{n:H/'cand'/n for n in names}};runs={n:[]for n in paths};order=list(paths)
for k in range(3):
 for n in order[k:]+order[:k]:
  r=one(paths[n]);runs[n].append(r);print(json.dumps(dict(event='paired_timing',name=n,seconds=r['seconds'],gates_ok=r['gates_ok'])),flush=True)
base=statistics.median(r['seconds']for r in runs['v37h']);out=[]
for n in names:
 r=json.loads(paths[n].with_suffix('.json').read_text());sec=statistics.median(v['seconds']for v in runs[n]);j=dict(host=socket.gethostname(),gates_ok=all(v['gates_ok']for v in runs[n]),speed_ok=sec<=20,median_seconds=sec,baseline_median_seconds=base,ratio=sec/base,expected_key_penalty=1.1e-7*math.log2(sec/base),judge_runs=runs[n],baseline_runs=runs['v37h'])
 r['paired_judge_1e6']=j;dump(paths[n].with_suffix('.json'),r);out.append(dict(name=n,loss=r['loss'],acceptance=r['acceptance'],sha256=r['sha256'],**j,expected_key_gain=TAU-r['loss']-j['expected_key_penalty']))
dump(R/'finalist_timing_comparison.json',out)
print(json.dumps(dict(event='timing_comparison_complete',ranking=[r['name']for r in sorted(out,key=lambda r:-r['expected_key_gain'])])),flush=True)
