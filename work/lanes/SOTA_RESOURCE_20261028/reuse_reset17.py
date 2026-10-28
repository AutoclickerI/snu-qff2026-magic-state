import os,sys,json,copy
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
R=Path.cwd();H=R/'work/lanes/SOTA_RESOURCE_20261028';sys.path[:0]=[str(R/'work/tools'),str(R/'work/lanes/END2_20261027'),str(R/'work/lanes/REBUILD20261027')]
from qtools.evaluator import frontend as f
from qtools.validity import raw_check
from qtools import write_stem,price
from joint import emit
from record_contract import complete
stem=R/'work/lanes/SOTA_RESOURCE_20261028/cand/resynth_safe_ed3fedc445723242_d6_20_19_10_2_22_16'
ops,dets=f.parse_current(stem.with_suffix('.qasm').read_text());data=json.loads(stem.with_suffix('.json').read_text())['data_qubits'];f.DATA=data
ops=[o for o in ops if not (o.kind=='R' and o.qs==(17,) and o.time==32)]
assert not any(17 in o.qs and o.time==30 for o in ops)
ops.append(f.Op('H',(17,),30));ops.sort(key=lambda o:o.time)
text=emit(ops,[]);model=f.make_model(*f.parse_current(text));record=complete(model,[]);zero=[set(x['bits']) for x in record['missing'] if x['reference']==0]
text=emit(ops,zero);raw=raw_check(text,data);s=write_stem(text,data,H/'cand','reuse_q17_xread',source={'parent':str(stem),'change':'Reuse MX result after H; regenerate deterministic zero-reference detector space.'})
r={'stem':str(s),'detector_rank':len(zero),'nonzero_reference':sum(x['reference'] for x in record['missing']),'raw':raw}
if raw['ok']:r['price']=price(s,1,use_cache=False)
(H/'reuse_q17.receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r),flush=True)
