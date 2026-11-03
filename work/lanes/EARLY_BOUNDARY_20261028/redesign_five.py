import os,sys,json,copy
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
R=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent
sys.path[:0]=[str(R/'work/lanes/NATIVE2_20261027'),str(R/'work/lanes/REBUILD20261027'),str(R/'work/tools')]
from incumbent_a_sx import f,emit
from qtools.validity import raw_check
from qtools import write_stem
from axis_echo import exact
import record_contract
record_contract.fa=f
P=next((R/'work/lanes/SOTA_20261028/native_best').glob('*.qasm'));orig,dets=f.parse_current(P.read_text());D=[6,20,19,10,2,22,16];f.DATA=D
ops=[]
for o in orig:
 if o.bit==322 or (o.kind=='CX' and (o.time,o.qs) in [(39,(16,15)),(46,(16,15))]):continue
 o=copy.deepcopy(o)
 if o.time>=41:o.time+=5
 ops.append(o)
ops.extend(f.Op('CX',q,t) for t,q in [(41,(14,13)),(42,(15,14)),(43,(14,13)),(44,(13,7)),(45,(13,12))])
ops.sort(key=lambda o:(o.time,o.kind,o.qs));occupied={}
for o in ops:
 for q in o.qs:
  key=(q,o.time);assert key not in occupied,(o,occupied.get(key));occupied[key]=o
for mode in ['completed']:
 ds=[]
 if mode=='completed':
  contract=record_contract.complete(f.make_model(ops,ds),ds);ds=[set(x['bits']) for x in contract['missing'] if not x['reference']]
 text=emit(ops,ds);raw=raw_check(text,D);print(mode,json.dumps(raw),flush=True)
 name=H/f'redesign_five_{mode}';name.with_suffix('.qasm').write_text(text);name.with_suffix('.json').write_text(json.dumps({'data_qubits':D},indent=2)+'\n')
 if raw['ok']:
  stem=write_stem(text,D,H,'redesign_five_valid');p=exact(stem);print('PRICE',p['loss'],p['acceptance'],flush=True)
  stem.with_suffix('.result.json').write_text(json.dumps({'raw':raw,'exact':p},indent=2)+'\n')
