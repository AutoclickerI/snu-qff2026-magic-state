import sys,json,collections,re
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'evaluator'))
import frontend as fa
BASE=ROOT.parents[2]/'quantumn_review10/work/lanes/MAIN/v36c'
text=BASE.with_suffix('.qasm').read_text()
meta=json.loads(BASE.with_suffix('.json').read_text())
fa.DATA=meta['data_qubits']
ops,dets=fa.parse_current(text)
m=fa.make_model(ops,dets)
eng=fa.Engine(m)
A0,N0=eng.ntable(0,0)
G=collections.defaultdict(lambda:{'P1_s0':0.,'N1_s0':0.,'channels':set(),'examples':[]})
for f in m.faults:
 if f['s'] or not f['d']:continue
 d=f['d'];g=G[d];g['P1_s0']+=f['p'];g['N1_s0']+=f['p']*N0[f['e']];g['channels'].add(f['chan'])
 if len(g['examples'])<3:g['examples'].append(f['label'])
rows=[]
for d,g in G.items():
 g.update(delta=str(d),detectors=[i for i in range(len(dets)) if d>>i&1],channel_count=len(g.pop('channels')))
 g['rows']=[sorted(dets[i]) for i in g['detectors']]
 g['single_fault_loss']=g['N1_s0']/g['P1_s0']
 rows.append(g)
rows.sort(key=lambda g:(round(g['single_fault_loss'],9),-g['P1_s0']))
(ROOT/'sector_shortlist.json').write_text(json.dumps({'note':'Diagnostic only: s=0 single-fault atoms, not a finite-p ranking or complete first order','detectors':len(dets),'faults':len(m.faults),'rows':rows},indent=2))
print(json.dumps(rows[:35],indent=2))
