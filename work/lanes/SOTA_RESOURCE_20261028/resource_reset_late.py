import os,sys,json,copy,itertools
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
R=Path.cwd();H=R/'work/lanes/SOTA_RESOURCE_20261028'
sys.path[:0]=[str(R/'work/tools'),str(R/'work/lanes/END2_20261027')]
from qtools.evaluator import frontend as f
from qtools.validity import raw_check
from qtools import write_stem,price
from joint import emit
stem=R/'work/lanes/SOTA_RESOURCE_20261028/cand/resynth_safe_ed3fedc445723242_d6_20_19_10_2_22_16'
base,det=f.parse_current(stem.with_suffix('.qasm').read_text());data=json.loads(stem.with_suffix('.json').read_text())['data_qubits']; f.DATA=data
choices={17:(32,31,32),11:(36,35,36),23:(32,31,32)}
for group in [(17,), (23,), (17,11), (17,23), (17,11,23)]:
 ops=copy.deepcopy(base);dets=copy.deepcopy(det);nextbit=max(o.bit for o in ops if o.bit is not None)+1
 try:
  for q in group:
   old,new,read=choices[q];o=next(o for o in ops if o.kind=='R' and o.qs==(q,) and o.time==old);o.time=new
   assert not any(q in v.qs and v.time in (new,read) and v is not o for v in ops),(q,new,read)
   ops.append(f.Op('M',(q,),read,nextbit));dets.append({nextbit});nextbit+=1
  ops.sort(key=lambda o:o.time);text=emit(ops,dets);raw=raw_check(text,data)
  s=write_stem(text,data,H/'cand','lateherald_'+'_'.join(map(str,group)),source=dict(parent=str(stem),changes=group,noise_scope='All real reset, measurement, gate and wait noise.'))
  row=dict(group=group,stem=str(s),raw=raw)
  if raw['ok']:row['price']=price(s,1,use_cache=False)
 except Exception as e:row=dict(group=group,error=str(e))
 print(json.dumps(row),flush=True)
 (H/('lateherald_'+'_'.join(map(str,group))+'.receipt.json')).write_text(json.dumps(row,indent=2)+'\n')
