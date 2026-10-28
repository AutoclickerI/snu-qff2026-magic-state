import os,sys,copy,json,time
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
R=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent
sys.path[:0]=[str(R/'work/tools'),str(R/'work/lanes/END2_20261027'),str(R/'work/lanes/REBUILD20261027')]
from qtools.evaluator import frontend as f
from qtools import write_stem,price
from qtools.validity import raw_check
from joint import emit
import record_contract
P=next((R/'work/lanes/SOTA_RESOURCE_20261028/geometry_cand').glob('six_measured_baseline*.qasm'))
ops,dets=f.parse_current(P.read_text());data=[6,20,19,10,2,22,16];bit=max(o.bit for o in ops if o.bit is not None)+1
for o in ops:
 if o.time>=39:o.time+=4
ops += [f.Op('CX',(19,20),39),f.Op('CX',(15,21),39),f.Op('CX',(20,21),40),f.Op('CX',(19,20),41),f.Op('CX',(22,21),41),f.Op('M',(21,),42,bit)]
ops.sort(key=lambda x:(x.time,x.kind,x.qs));occupied={}
for o in ops:
 for q in o.qs:
  k=o.time,q
  assert k not in occupied,(o,occupied[k])
  occupied[k]=o
for mode in ('check','no_check'):
 ds=copy.deepcopy(dets)+([{bit}] if mode=='check' else [])
 text=emit(ops,ds);raw=raw_check(text,data);print(mode,'raw',raw,flush=True)
 stem=write_stem(text,data,H,'copied_parity_'+mode,source={'old_circuit':str(P),'measurement_record':bit,'physical_check':'Z19 Z20 Z22 Z16 through live q15 copy'});res={'stem':str(stem),'raw':raw,'bit':bit,'extra_ticks':4,'check':mode=='check'}
 if raw['ok']:
  f.DATA=data;res['singles']=record_contract.singles(f.make_model(*f.parse_current(text)));print('c1',res['singles']['c1'],flush=True)
  res['exact']=price(stem,processes=1);print('exact',res['exact']['loss'],res['exact']['acceptance'],flush=True)
 stem.with_suffix('.result.json').write_text(json.dumps(res,indent=2)+'\n')
