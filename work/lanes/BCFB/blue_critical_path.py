import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import json
from build import H,S,native_times
D=H/'blue';rows=[]
for stem in ['v25k','v26n','neighbor_blue_d15_c105_s706_00405_check_11_19','neighbor_blue_d15_c90_s712_00074_check_19']:
 p=D/'finalists'/stem;md=json.loads(p.with_suffix('.json').read_text());text=p.with_suffix('.qasm').read_text();_,raw,_=S.qasm_ops(text);u=S.fold_units(raw);ts=native_times(text,u);pred,succ=S.build_dag(u);dist=[];parent=[]
 for i in range(len(u)):
  j=max(pred[i],key=lambda j:dist[j]) if pred[i] else None;parent.append(j);dist.append(dist[j]+1 if j is not None else 0)
 before=[i for i,t in enumerate(ts) if t<md['R']];at=[i for i,t in enumerate(ts) if t==md['R']];i=max(before,key=lambda j:dist[j]);bound_before=dist[i]+1;j=max(at,key=lambda j:dist[j]);bound_at=dist[j]
 end=i if bound_before>=bound_at else j;path=[]
 while end is not None:path.append(dict(index=end,earliest=dist[end],actual=ts[end],name=u[end].name,lines=u[end].lines));end=parent[end]
 row=dict(stem=stem,R=md['R'],minimum_R_for_fixed_wire_order=max(bound_before,bound_at),bound_before=bound_before,bound_at=bound_at,critical_path=path[::-1]);rows.append(row);print(stem,row['minimum_R_for_fixed_wire_order'],path[0]['lines'])
(D/'critical_path.json').write_text(json.dumps(rows,indent=2))
