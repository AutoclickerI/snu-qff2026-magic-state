import os,sys,json,copy
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
R=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent;sys.path[:0]=[str(R/'work/lanes/CONTINUE_20261028'),str(R/'work/lanes/END2_20261027'),str(R/'work/lanes/REBUILD20261027'),str(R/'work/tools')]
from qtools.evaluator import frontend as f
from qtools.validity import raw_check
from qtools import write_stem,price
from joint import emit
import record_contract,instrument_probe
P=next((R/'work/lanes/NATIVE_CAT7_20261028/boundary').glob('cat7_opt_t11_m0_d21*.qasm'));base,det=f.parse_current(P.read_text());D=[6,20,19,10,2,22,16];ops=copy.deepcopy(base);assert not any(o.time==32 and 15 in o.qs for o in ops);ops.append(f.Op('R',(15,),32));ops.sort(key=lambda o:o.time)
f.DATA=D
for mode in ('preserve','complete'):
 ds=copy.deepcopy(det) if mode=='preserve' else []
 if mode=='complete':
  c=record_contract.complete(f.make_model(ops,ds),ds);ds += [set(x['bits']) for x in c['missing'] if not x['reference']]
 text=emit(ops,ds);raw=raw_check(text,D);print('RAW',mode,json.dumps(raw),flush=True)
 if not raw['ok']:continue
 stem=write_stem(text,D,H,'cat7_r15_'+mode,source={'parent':str(P),'addition':'R15@32, independent fresh input to A encoder','detector_mode':mode});model=f.make_model(*f.parse_current(text));c=record_contract.complete(model,ds);aud=record_contract.singles(model);pr=instrument_probe.probe(stem,32)
 row={'stem':str(stem),'raw':raw,'detectors':len(ds),'missing_deterministic':c['missing'],'singles':aud,'instrument':pr,'cx':sum(o.kind=='CX'for o in ops),'clocks':max(o.time for o in ops)+1}
 print('AUDIT',mode,'detectors',len(ds),'missing',len(c['missing']),'c1',aud['c1'],'harmful',len(aud['harmful_faults']),'instrument',json.dumps(pr['summary']),flush=True)
 p=price(stem,1);row['exact']=p;print('PRICE',mode,p['loss'],p['acceptance'],flush=True);stem.with_suffix('.receipt.json').write_text(json.dumps(row,indent=2)+'\n')
