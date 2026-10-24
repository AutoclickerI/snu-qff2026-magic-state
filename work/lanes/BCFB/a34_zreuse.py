"""Early q8 Z flag plus native Z-state reuse on q9/q15 of the X8-pivot encoder."""
from a34_search import *
from a34_dedup import physical_key
stems=[];seen=set()
for base in ('encoders_00004','checks_00042','checks_00038','checks_00013'):
 source=read(D/'candidates'/base);text,md,h,original,ts,original_tail=source
 for mask in range(4):
  us=list(original);times=list(ts);tail=list(original_tail);changes=[]
  # Retain both the old Z readout's information and the later RX preparation.
  us.append(U(['measure q[8] -> c[380];']));times.append(36);tail.append('// DETECTOR c[380]');changes.append(dict(q=8,time=36,kind='MZ_flag'))
  for j,q in enumerate((9,15)):
   if not (mask>>j&1):continue
   i=next(i for i,(u,t) in enumerate(zip(us,times)) if u.name=='RESET' and u.qs==(q,) and t>=38)
   bit=381+j;us[i]=U([f'measure q[{q}] -> c[{bit}];']);tail.append(f'// DETECTOR c[{bit}]');changes.append(dict(q=q,time=times[i],kind='RESET_to_MZ_flag'))
  text,meta=emit(h,us,times,tail,dict(kind='early_q8_and_Z_reuse',source=base,parent_options=md['options'],changes=changes),True)
  stem=D/'candidates'/f'zreuse_{len(stems):05}';stem.with_suffix('.qasm').write_text(text);stem.with_suffix('.json').write_text(json.dumps(meta,indent=2));key=physical_key(stem)
  if key in seen:stem.with_suffix('.qasm').unlink();stem.with_suffix('.json').unlink();continue
  seen.add(key);stems.append(str(stem.relative_to(H)))
(D/'zreuse.json').write_text(json.dumps(dict(stems=stems),indent=2));print('generated',len(stems),flush=True)
