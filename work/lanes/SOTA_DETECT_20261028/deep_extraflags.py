import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import sys,json
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[2];sys.path[:0]=[str(R/'work/lanes/NATIVE20261027'),str(R/'work/lanes/CAT3_20261027')]
import rebuild,smallcat as s
folder=H/'deep_extra';folder.mkdir(exist_ok=True)
rows=[]
for idx,pair in enumerate([None,(1,2),(1,3),(3,2),(5,0),(6,4),(3,4)]):
 c,data=rebuild.build_joint_flags(19,14,((0,1),(2,5),(4,6)))
 for j,q in enumerate([6,4,1]):
  t=16+j;old=f'cx q[{7+j}],q[35];';new=f'cx q[{7+q}],q[35];';assert old in c.ops[t];c.ops[t][c.ops[t].index(old)]=new
 if pair:
  u,v=pair;c.reset(7,35);c.cx(8,21+u,35);c.cx(9,21+v,35);c.dets.append([c.read(10,35)])
  c.reset(11,35);c.cx(12,28+u,35);c.cx(13,28+v,35);c.dets.append([c.read(14,35)])
 text=c.text();ops,dets=s.f.parse_current(text);used=set();coll=[]
 for o in ops:
  q={(o.time,x)for x in o.qs}
  if used&q:coll.append((o.kind,o.time,o.qs))
  used|=q
 row={'pair':pair,'collisions':coll}
 if coll:print(json.dumps(row),flush=True);rows.append(row);continue
 raw=s.ideal_contract_check(text,data);row['raw']=raw['ok']
 if raw['ok']:
  stem=folder/f'extra_{idx}';stem.with_suffix('.qasm').write_text(text);stem.with_suffix('.json').write_text(json.dumps({'data_qubits':data,'abstract':True,'extra_pair':pair}))
  s.f.DATA=data;a=s.record_contract.singles(s.f.make_model(ops,dets));row['c1']=a['c1'];val=s.exact(stem);row.update(loss=val['loss'],acceptance=val['acceptance'],stem=str(stem))
 rows.append(row);(H/'deep_extra_results.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(row),flush=True)
