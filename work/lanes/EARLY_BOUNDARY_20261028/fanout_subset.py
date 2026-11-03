import os,sys,json,copy
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
R=Path(__file__).resolve().parents[3];H=Path(__file__).parent;sys.path.insert(0,str(R/'work/lanes/NATIVE2_20261027'))
from incumbent_a_sx import f,emit
from qtools.validity import raw_check
P=H/'redesign_valid_e50870ae31301cfd_d6_20_19_10_2_22_16.qasm';ops,_=f.parse_current(P.read_text());D=[6,20,19,10,2,22,16];x=[(41,(15,14)),(42,(14,13)),(43,(15,14)),(44,(14,13)),(45,(13,7)),(46,(13,12))];out=[]
for mask in range(64):
 a=[o for o in ops if not (o.kind=='CX' and any(mask>>i&1 and (o.time,o.qs)==v for i,v in enumerate(x)))]
 r=raw_check(emit(a,[]),D);out.append({'removed':mask,'raw':r});
 if r['ok']:print('valid removed',mask,flush=True)
(H/'fanout_subset.json').write_text(json.dumps(out,indent=2)+'\n')
