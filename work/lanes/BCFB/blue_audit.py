import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import json,collections,hashlib
from pathlib import Path
from build import source,H,B,C,S,native_times
D=H/'blue';rows=[]
for f in sorted((D/'finalists').glob('*preserve*.json')):
 if f.name.endswith(('.screen.json','.verify.json','.exact.json','.mc.json')):continue
 md=json.loads(f.read_text());context=md['options']['context'];base,h,old,ots,tail,init,rem=source(context);text=f.with_suffix('.qasm').read_text();_,raw,ntail=S.qasm_ops(text);nu=S.fold_units(raw);nts=native_times(text,nu)
 # Old BC CX and every exterior CX, with multiplicity. Changes in non-CX
 # native folds are explicitly enumerated rather than normalized away.
 oldcx=collections.Counter(tuple(u.lines) for i,u in enumerate(old) if i not in rem and u.name=='CX');newcx=collections.Counter(tuple(u.lines) for u in nu if u.name=='CX');prep=collections.Counter((f'cx q[{a}],q[{b}];',) for layer in md['prep']['ops'] for a,b in layer)
 assert newcx-prep==oldcx,(f.name,'exterior CX difference')
 assert not prep-newcx
 # Every exterior native unit must occur with its source lines and planned
 # time. A retained final H on a previous MX is the builder's only allowed
 # exterior line extension; its noise/timing fold stays explicitly checked.
 required=collections.Counter()
 for i,u in enumerate(old):
  if i in rem:continue
  lines=u.lines[:]
  if u.qs and u.qs[0] in md['retained_previous_X_states'] and u.name=='MX' and u.last_is_measure and i<init.get(u.qs[0],-1):
   later=[j for j in range(i+1,init[u.qs[0]]) if j not in rem and u.qs[0] in old[j].qs]
   if not later:lines.append(f'h q[{u.qs[0]}];')
  t=md['non_BC_time_changes'].get(str(i),ots[i]);required[(tuple(lines),t)]+=1
 present=collections.Counter((tuple(u.lines),t) for u,t in zip(nu,nts));missing=required-present
 assert not missing,(f.name,'exterior native unit mismatch',missing)
 row=dict(stem=f.stem,context=context,source_removed=len(rem),old_prep_cx=sum(old[i].name=='CX' for i in rem),new_prep_cx=sum(prep.values()),exterior_cx_preserved=sum(oldcx.values()),exterior_native_units_preserved=sum(required.values()),R=md['R'],source_R=base['R'],non_BC_time_changes=[dict(index=int(i),lines=old[int(i)].lines,old=ots[int(i)],new=t) for i,t in md['non_BC_time_changes'].items()],retained_previous_X_states=md['retained_previous_X_states'],unfolded_previous_MX=md['unfolded_previous_MX'],qasm_sha256=hashlib.sha256(text.encode()).hexdigest())
 rows.append(row)
(D/'port_audit.json').write_text(json.dumps(rows,indent=2));print('audited',len(rows),'ports')
