"""First-order joint detector/frame screen on actual v29c.

Independent integer-Pauli walker; no official judge/Monte Carlo claim.
For every complete detector syndrome supported by one fault, compute accepted
probability and logical loss under each of I, X_L, Z_L, Y_L frame choices.
"""
import json,sys
from pathlib import Path
from collections import defaultdict
import numpy as np

HERE=Path(__file__).resolve().parent
EVALUATOR=HERE.parent/'evaluator'
sys.path.insert(0,str(EVALUATOR))
import frontend as fa
from frontend import parse_current

stem=EVALUATOR/'examples/v29c'
fa.DATA=json.loads(stem.with_suffix('.json').read_text())['data_qubits']
ops,dets=parse_current(stem.with_suffix('.qasm').read_text())
m=fa.make_model(ops,dets);eng=fa.Engine(m)
assert all(x==0 for x,z,c in eng.projs)
a,n=eng.ntable(0,0);assert abs(a-1)<1e-10 and abs(n[0])<1e-10
sector=np.zeros(eng.N,dtype=np.int64)
for j,(x,z,c) in enumerate(eng.projs):
    sector |= ((c.real*eng.sgn(z)<0).astype(np.int64)^int(eng.v[j]))<<j
sectors=np.unique(sector)
frame_masks=[0,1<<7,1<<6,(1<<7)|(1<<6)]
hist=defaultdict(lambda:np.zeros(5))
examples=defaultdict(list)
by_s=defaultdict(list)
for f in m.faults:by_s[f['s']].append(f)
for s,fs in by_s.items():
    phi=eng.phi(s)
    for d in sectors:
        vec=phi*(sector==d);a=np.vdot(vec,vec).real/eng.A0
        if a<1e-15:continue
        E=np.array([eng.expect(vec,eng.Qs[k]) for k in eng.keys])/eng.A0
        nt=.5*(a-eng.SG@E)
        for f in fs:
            actual=int(d)^f['d']
            row=hist[actual];row[0]+=f['p']*a
            row[1:]+=f['p']*nt[[f['e']^z for z in frame_masks]]
            if len(examples[actual])<8:examples[actual].append(f['label'])
rows=[]
for d,row in hist.items():
    best=int(np.argmin(row[1:])); benefit=float(row[1]-row[1+best])
    rows.append(dict(syndrome=d,indices=[j for j in range(len(dets)) if d>>j&1],
                     single_probability_mass=float(row[0]),loss_by_frame={k:float(v) for k,v in zip(['I','X','Z','Y'],row[1:])},
                     best_frame=['I','X','Z','Y'][best],benefit_vs_I=benefit,
                     best_is_first_order_safe=bool(row[1+best]<1e-14),examples=examples[d]))
rows.sort(key=lambda r:-r['benefit_vs_I'])
safe_nonidentity=[r for r in rows if r['syndrome'] and r['best_frame']!='I' and r['best_is_first_order_safe'] and r['benefit_vs_I']>1e-14]
out=dict(source=str(stem),scope='Single-fault mass only, no finite-p/full-circuit gain claim',
         detector_count=len(dets),channels=len(m.chans),single_faults=len(m.faults),rank=eng.r,
         native_depth=max(t for row in m.steps for qs,t in row)+1,
         supported_single_syndromes=len(rows),first_order_safe_nonidentity_count=len(safe_nonidentity),
         safe_nonidentity=safe_nonidentity,top_frame_benefits=rows[:20])
Path(__file__).with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k not in ('safe_nonidentity','top_frame_benefits')},indent=2))
print(json.dumps({'top_safe_syndromes':safe_nonidentity[:5]},indent=2))
