import os,sys,itertools,json
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(R/'work/lanes/NATIVE2_20261027'))
from incumbent_a_sx import f,emit,to_stim,run
P=R/'work/lanes/NATIVE2_20261027/boundary/source_prefix_d828869d5031c029_d6_20_19_10_2_22_16.qasm'
ops,dets=f.parse_current(P.read_text());out=[]
for cut,q,partner in [(36,13,7),(38,13,19),(39,15,16)]:
 prefix=[o for o in ops if o.time<cut];bits={o.bit for o in prefix if o.bit is not None};native,err=to_stim(emit(prefix,[r for r in dets if r<=bits]));assert not err
 state,inv,rec,_,wires=run(native,36)
 def ex(terms):
  p=state.stim.PauliString(state.n)
  for i,a in terms:p[wires[i]]=a
  return float(state.expectation(p,inv))
 pool=sorted(set([6,20,19,10,2,22,16,7,13,15,9,3,1])-{q,partner});found=[]
 for axis in 'XY':
  for partneraxis in 'XY':
   for n in range(5):
    for qs in itertools.combinations(pool,n):
     for axes in itertools.product('XY',repeat=n):
      terms=[(q,axis),(partner,partneraxis),*zip(qs,axes)];v=ex(terms)
      if abs(v)>1e-7:found.append(dict(terms=terms,value=v))
  
 row=dict(cut=cut,q=q,partner=partner,single={a:ex([(q,a)]) for a in 'XYZ'},nonzero=sorted(found,key=lambda x:-abs(x['value']))[:40],count=len(found));out.append(row);print(json.dumps(row),flush=True)
(Path(__file__).parent/'coherence.json').write_text(json.dumps(out,indent=2)+'\n')
