import os,sys,json,itertools,copy
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
R=Path(__file__).resolve().parents[3];H=Path(__file__).parent;sys.path.insert(0,str(R/'work/lanes/NATIVE2_20261027'))
from incumbent_a_sx import f,emit
from qtools.validity import raw_check
P=H/'redesign_five_valid_5505afaaef422fe1_d6_20_19_10_2_22_16.qasm';ops,_=f.parse_current(P.read_text());D=[6,20,19,10,2,22,16];x=[(41,(14,13)),(42,(15,14)),(43,(14,13)),(44,(13,7)),(45,(13,12))];out=[]
for choice in itertools.product(range(3),repeat=5):
 a=[]
 for o in ops:
  j=next((i for i,v in enumerate(x) if o.kind=='CX' and (o.time,o.qs)==v),None)
  if j is not None:
   if choice[j]==0:continue
   if choice[j]==2:o=copy.deepcopy(o);o.qs=o.qs[::-1]
  a.append(o)
 r=raw_check(emit(a,[]),D);out.append({'choice':choice,'raw':r})
 if r['ok']:print('valid',choice,flush=True)
(H/'fanout_orient.json').write_text(json.dumps(out,indent=2)+'\n')
