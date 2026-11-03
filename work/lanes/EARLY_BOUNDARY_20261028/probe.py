import os,sys,json,itertools,time
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
R=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(R/'work/lanes/NATIVE2_20261027'))
from incumbent_a_sx import f,emit,to_stim,run
P=R/'work/lanes/NATIVE2_20261027/boundary/source_prefix_d828869d5031c029_d6_20_19_10_2_22_16.qasm'
ops,dets=f.parse_current(P.read_text()); data=[6,20,19,10,2,22,16]; targets=[7,13,15]; out=[]
for tick in range(34,41):
 prefix=[o for o in ops if o.time<tick]; bits={o.bit for o in prefix if o.bit is not None}
 native,errors=to_stim(emit(prefix,[r for r in dets if r<=bits]));assert not errors
 state,inv,records,_,wires=run(native,36)
 def ex(axis,qs):
  p=state.stim.PauliString(state.n)
  for q in qs:p[wires[q]]=axis
  return float(state.expectation(p,inv))
 singles={str(q):{a:ex(a,[q]) for a in 'XZ'} for q in range(29)}
 correlated=[]
 for q in targets:
  for a in 'XZ':
   if abs(singles[str(q)][a])>.999999:continue
   for n in [1,2]:
    for rest in itertools.combinations([i for i in range(29) if i!=q],n):
     val=ex(a,[q,*rest])
     if abs(val)>.999999 and all(abs(singles[str(j)][a])<.999999 for j in rest):correlated.append(dict(axis=a,support=[q,*rest],expectation=val))
 row=dict(cut=tick,singles=singles,correlations=correlated,conditioned_rows=[sorted(r) for r in dets if r<=bits]);out.append(row)
 print(json.dumps(dict(cut=tick,targets={q:singles[str(q)] for q in targets},correlations=correlated)),flush=True)
 (Path(__file__).parent/'probe.json').write_text(json.dumps(out,indent=2)+'\n')
