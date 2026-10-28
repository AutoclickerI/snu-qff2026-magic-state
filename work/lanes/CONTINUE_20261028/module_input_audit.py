"""Compare unreset module inputs on original and seven-cat source prefixes."""
import os,sys,json,hashlib
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
R=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent
sys.path[:0]=[str(R/'work/lanes/NATIVE2_20261027'),str(R/'work/lanes/REBUILD20261027'),str(R/'work/tools')]
from incumbent_a_sx import f,emit,to_stim,run
D={6,20,19,10,2,22,16}
OLD=R/'work/lanes/NATIVE2_20261027/boundary/source_prefix_d828869d5031c029_d6_20_19_10_2_22_16.qasm'
CAT=next((R/'work/lanes/NATIVE_CAT7_20261028').glob('source_opt_t11_m0_d21_*.qasm'))
MODULES={'A_original':R/'work/lanes/NATIVE2_20261027/compact_a_logical_read_a_module.json',
         'B_original':R/'work/lanes/NATIVE2_20261027/old_b_module.json',
         'A_cat_schedule':R/'work/lanes/NATIVE_CAT7_20261028/a_opt_t11_m0_d21.json',
         'B_cat_schedule':R/'work/lanes/NATIVE_CAT7_20261028/b_opt_t11_m0_d21.json'}

def inputs(path):
 doc=json.loads(path.read_text());ops=doc['candidates'][0]['operations'];result=[]
 for q in sorted({q for o in ops for q in o['qs'] if q not in D}):
  first=min((o for o in ops if q in o['qs']),key=lambda x:x['time'])
  result.append(dict(q=q,time=first['time'],kind=first['kind'],qubits=first['qs'],
                     initial_operation=first['kind'] in ('R','RX'),original_bit=first.get('original_bit')))
 return result

def examine(path,qs):
 text=path.read_text();ops,dets=f.parse_current(text);native,errors=to_stim(text);assert not errors,errors
 state,inverse,records,_,w=run(native,36);measured=[o for o in ops if o.bit is not None]
 assert len(measured)==len(records),(len(measured),len(records))
 recwire={o.bit:records[i] for i,o in enumerate(measured)}
 def exp(q,axis,bit=None):
  p=state.stim.PauliString(state.n);p[w[q]]=axis
  if bit is not None:p[recwire[bit]]='Z'
  return float(state.expectation(p,inverse))
 rows=[]
 for q in qs:
  hist=[o for o in ops if q in o.qs];last=hist[-1] if hist else None
  vals={a:exp(q,a) for a in 'XYZ'}
  row=dict(q=q,expectations=vals,fresh=not hist,
      last=None if last is None else dict(kind=last.kind,time=last.time,qubits=last.qs,bit=last.bit))
  if last and last.bit is not None:
   axis='X' if last.kind=='MX' else 'Z';row['last_read_correlation']=dict(axis=axis,bit=last.bit,expectation=exp(q,axis,last.bit))
  rows.append(row)
 return dict(path=str(path.relative_to(R)),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
   scope='Noiseless unconditioned physical source state with all prior measurement records retained; not a full fault or instrument equivalence proof.',rows=rows)

def q26_before_mx(path,module,t):
 source,_=f.parse_current(path.read_text());ops=[o for o in source if o.time<t]
 occ={(o.time,q) for o in ops for q in o.qs};bit=max((o.bit for o in source if o.bit is not None),default=-1)+1
 for row in json.loads(module.read_text())['candidates'][0]['operations']:
  if row['time']>=t:continue
  for q in row['qs']:assert (row['time'],q) not in occ,(row,q)
  occ.update((row['time'],q) for q in row['qs'])
  b=None
  if row['kind'] in ('M','MX'):b=bit;bit+=1
  ops.append(f.Op(row['kind'],tuple(row['qs']),row['time'],b))
 ops.sort(key=lambda o:o.time)
 native,err=to_stim(emit(ops,[]));assert not err,err
 s,inv,_,_,w=run(native,36);out={}
 for axis in 'XZ':
  p=s.stim.PauliString(s.n);p[w[26]]=axis;out[axis]=float(s.expectation(p,inv))
 return dict(before_clock=t,expectations=out,scope='Actual source plus B operations strictly before MX26, no detector conditioning; preserved q26 guards in original module.')

if __name__=='__main__':
 modules={n:inputs(p) for n,p in MODULES.items()}
 qs=sorted({x['q'] for k in ('A_cat_schedule','B_cat_schedule') for x in modules[k] if not x['initial_operation']})
 out=dict(modules=modules,probed_nonreset_inputs=qs,old_source=examine(OLD,qs),cat_source=examine(CAT,qs),
  q26_before_module_mx=dict(old=q26_before_mx(OLD,MODULES['B_original'],31),cat=q26_before_mx(CAT,MODULES['B_cat_schedule'],21)),
  qualification='First module operations are compared; values at source ends may not capture all interleaved module–source correlations. MX/M are physical preparations with record-dependent outcomes, not unconditional reset.')
 (H/'module_input_audit.json').write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps(out,indent=2))
