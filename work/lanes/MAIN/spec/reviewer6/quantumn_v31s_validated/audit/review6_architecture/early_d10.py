"""Two bounded timing refinements: earliest D10->A9 after A9's encoder ends."""
from pathlib import Path
import sys,json,hashlib
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'audit/reaudit_evaluation/portable'))
import frontend as f
from circuit_io import emit
for name,newtime in [('v30g',43),('v31s',41)]:
 source=HERE/(name+'_a_decode');ops,dets=f.parse_current(source.with_suffix('.qasm').read_text())
 meta=json.loads(source.with_suffix('.json').read_text());meta.pop('independent_verification',None)
 R=meta['R'];couple=next(o for o in ops if o.kind=='CX'and o.qs==(10,9)and o.time>=R-1)
 oldtime=couple.time;couple.time=newtime
 shifts=[dict(kind='CX',qubits=[10,9],old=oldtime,new=newtime)]
 prior=[o for o in ops if 10 in o.qs and o.kind=='TDG'and o.time<oldtime]
 assert len(prior)==1
 if prior[0].time>=newtime:
  old=prior[0].time;prior[0].time=newtime-1;shifts.append(dict(kind='TDG',qubits=[10],old=old,new=newtime-1))
 for t in range(meta['native_depth']):
  active=[q for o in ops if o.time==t for q in o.qs];assert len(active)==len(set(active)),(name,t,active)
 ops.sort(key=lambda o:o.time)
 stem=HERE/(name+'_a_decode_d10_early')
 meta.update(parent=str(source),timing_refinement=shifts,method=__doc__)
 emit(ops,dets,stem,meta)
 parsed,ds=f.parse_current(stem.with_suffix('.qasm').read_text());f.DATA=meta['data_qubits'];m=f.make_model(parsed,ds);e=f.Engine(m)
 A,N=e.ntable(0,0);phi=e.phi(0);stabs=[e.expect(phi,(e.B.express(x),e._w(z),c))for x,z,c in m.gen_m]
 c1p=0.;bad=[]
 for fault in m.faults:
  aa,nn=e.ntable(fault['s'],fault['d']);v=0. if nn is None else fault['p']*nn[fault['e']];c1p+=v
  if v>1e-15:bad.append(fault['label'])
 cert=dict(ideal_acceptance=A,ideal_loss=float(N[0]),output_stabilizers=stabs,first_order_loss=c1p,harmful_single_fault_count=len(bad),all_CX_nearest_neighbor=all(abs(o.qs[0]//6-o.qs[1]//6)+abs(o.qs[0]%6-o.qs[1]%6)==1 for o in parsed if o.kind=='CX'),all_layers_disjoint=True,native_schedule_matches=all(step==o.time for o,entries in zip(parsed,m.steps)for qs,step in entries),qasm_sha256=hashlib.sha256(stem.with_suffix('.qasm').read_bytes()).hexdigest())
 assert A>1-1e-10 and abs(N[0])<1e-10 and all(abs(s-1)<1e-10 for s in stabs)and not bad
 assert cert['all_CX_nearest_neighbor']and cert['native_schedule_matches']
 meta['independent_verification']=cert;stem.with_suffix('.json').write_text(json.dumps(meta,indent=2)+'\n')
 print(json.dumps(dict(stem=str(stem),timing=shifts,verification=cert)),flush=True)
