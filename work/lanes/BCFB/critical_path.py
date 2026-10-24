import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import json
from build import H,S,native_times,B,C
rows=[]
for stem in ('inputs/v23h_c2c9','finalists/fast_d15_c105_s526_00356'):
 f=H/stem;md=json.loads(f.with_suffix('.json').read_text());text=f.with_suffix('.qasm').read_text();h,raw,tail=S.qasm_ops(text);u=S.fold_units(raw);ts=native_times(text,u);p,s=S.build_dag(u);earliest=[];prev=[]
 for i in range(len(u)):
  j=max(p[i],key=lambda j:earliest[j]) if p[i] else None;earliest.append(earliest[j]+1 if j is not None else 0);prev.append(j)
 rid=[i for i,x in enumerate(u) if ts[i]==md['R'] and x.name=='CX' and not(set(x.qs)<=set(B+C))];last=max(rid,key=lambda i:earliest[i]);path=[]
 while last is not None:path.append(dict(unit=last,earliest=earliest[last],native=ts[last],lines=u[last].lines));last=prev[last]
 path.reverse();out=dict(stem=stem,minimum_round_with_fixed_wire_order=max(earliest[i] for i in rid),native_round=md['R'],critical_path=path);rows.append(out);print(stem,out['minimum_round_with_fixed_wire_order'],path[-8:])
(H/'critical_path.json').write_text(json.dumps(rows,indent=2))
