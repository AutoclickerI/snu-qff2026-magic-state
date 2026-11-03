import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import sys,json,concurrent.futures
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[2];sys.path[:0]=[str(R/'work/lanes/CAT3_20261027'),str(R/'work/lanes/END2_20261027')]
import smallcat as s
from joint import emit
s.f.DATA=list(range(7))
def one(name):
 stem=H/'deep_cand'/name;ops,dets=s.f.parse_current(stem.with_suffix('.qasm').read_text());m=s.f.make_model(ops,dets)
 comp=s.record_contract.complete(m,dets);missing=comp['missing'];print('MISSING',name,len(missing),flush=True)
 rows=[]
 for i in range(1<<len(missing)):
  dd=dets+[set(x['bits']) for j,x in enumerate(missing) if i>>j&1]
  if any(x['reference'] for j,x in enumerate(missing) if i>>j&1):continue
  text=emit(ops,dd);raw=s.ideal_contract_check(text,list(range(7)))
  if not raw['ok']:continue
  out=H/'deep_cand'/f'{name}_d{i:02}';out.with_suffix('.qasm').write_text(text);out.with_suffix('.json').write_text(json.dumps({'data_qubits':list(range(7)),'abstract':True,'added_detectors':[x for j,x in enumerate(missing) if i>>j&1]},indent=2))
  val=s.exact(out);rows.append({'name':out.name,'mask':i,'loss':val['loss'],'acceptance':val['acceptance']});print('PRICE',json.dumps(rows[-1]),flush=True)
 return {'name':name,'missing':missing,'rows':rows}
if __name__=='__main__':
 with concurrent.futures.ProcessPoolExecutor(max_workers=2) as e:out=list(e.map(one,['deep_007','deep_023']))
 (H/'deep_contract_results.json').write_text(json.dumps(out,indent=2)+'\n')
