"""Bounded interaction test: remove one entire Z-wait echo after A decoding."""
from pathlib import Path
import sys,json,hashlib,copy
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'audit/reaudit_evaluation/portable'))
import frontend as f
from circuit_io import emit
source=HERE/'v32p_a_decode';md=json.loads(source.with_suffix('.json').read_text())
ops,dets=f.parse_current(source.with_suffix('.qasm').read_text())
cases=[('remove_z6',6,0,34,35,40,41,267),('remove_z26',26,20,20,21,30,31,269)]
for name,h,d,init,t1,t2,meas,bit in cases:
 expected={('RX',(h,),init,None),('CX',(h,d),t1,None),('CX',(h,d),t2,None),('MX',(h,),meas,bit)}
 key=lambda o:(o.kind,o.qs,o.time,o.bit)
 assert expected.issubset({key(o)for o in ops})
 assert [row for row in dets if bit in row]==[{bit}]
 new=[copy.copy(o)for o in ops if key(o)not in expected]
 nd=[set(row)for row in dets if row!={bit}]
 target=HERE/('v32p_a_decode_'+name)
 meta=dict(data_qubits=md['data_qubits'],source_qasm_sha256=hashlib.sha256(source.with_suffix('.qasm').read_bytes()).hexdigest(),
           source_commit=md['source_commit'],method=__doc__,variant=name,CX=sum(o.kind=='CX'for o in new),
           native_depth=max(o.time for o in new)+1,removed_echo=dict(helper=h,data=d,init=init,cx_ticks=[t1,t2],measurement=meas,bit=bit),
           official_class_tested=False,official_runtime_tested=False)
 emit(new,nd,target,meta)
 parsed,rows=f.parse_current(target.with_suffix('.qasm').read_text());f.DATA=meta['data_qubits']
 m=f.make_model(parsed,rows);e=f.Engine(m);A,N=e.ntable(0,0)
 first=0.;harmful=0
 for fault in m.faults:
  a,n=e.ntable(fault['s'],fault['d']);v=0 if n is None else fault['p']*n[fault['e']]
  first+=v;harmful+=v>1e-15
 cert=dict(ideal_acceptance=A,ideal_loss=float(N[0]),first_order_loss=float(first),harmful_single_fault_count=int(harmful),
           native_schedule_matches=all(step==o.time for o,steps in zip(parsed,m.steps)for qs,step in steps),
           qasm_sha256=hashlib.sha256(target.with_suffix('.qasm').read_bytes()).hexdigest())
 assert A>1-1e-10 and abs(N[0])<1e-10 and not harmful and cert['native_schedule_matches']
 meta['independent_verification']=cert;target.with_suffix('.json').write_text(json.dumps(meta,indent=2)+'\n')
 print(json.dumps(dict(name=target.name,**cert)),flush=True)
