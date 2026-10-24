"""Port the exact two-CX destructive A decoder to pinned v30g and v31s.
No inherited official verdicts. All current readout edges/bit IDs are preserved.
Only q10 TDG must move earlier for the R45 v31s port; every change is priced.
"""
from pathlib import Path
import sys,json,hashlib,dataclasses,shutil
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'audit/reaudit_evaluation/portable'))
import frontend as f
from circuit_io import emit
SHA='abf26aa98bede59bb07f7da838dd1b3a3fdf76f0'

def build(name,decoded):
 source=ROOT/f'quantumn_review6/work/lanes/MAIN/{name}'
 text=source.with_suffix('.qasm').read_text();ops,dets=f.parse_current(text)
 source_meta=json.loads(source.with_suffix('.json').read_text());data=source_meta['data_qubits']
 R=next(o.time for o in ops if o.kind=='CX'and o.qs==(0,1)and o.time>=40)
 depth=max(o.time for o in ops)+1
 stem=HERE/(name+'_a_decode'if decoded else name+'_control')
 edits=[]
 if decoded:
  for pair in [(10,9),(21,15)]:
   oo=[o for o in ops if o.kind=='CX'and o.qs==pair and o.time==R];assert len(oo)==1
   oo[0].time=R-1;edits.append(dict(kind='CX',qubits=pair,old=R,new=R-1))
  for q in [10,21]:
   clashing=[o for o in ops if q in o.qs and o.time==R-1 and not(o.kind=='CX'and o.qs in[(10,9),(21,15)])]
   for o in clashing:
    assert o.kind=='TDG'and o.qs==(10,),o
    assert not any(q in x.qs and x.time==R-2 for x in ops)
    o.time=R-2;edits.append(dict(kind='TDG',qubits=[q],old=R-1,new=R-2))
  measure={o.qs[0]:o for o in ops if o.kind=='M'and o.time>=R and o.qs[0]in[8,9,15]}
  assert set(measure)=={8,9,15}
  # Existing terminal readout edges in these sources commute with both inserted
  # decoder gates. The measured-Z row conjugation can therefore act directly.
  for c,t in[(9,15),(8,9)]:
   cb,tb=measure[c].bit,measure[t].bit
   for row in dets:
    if tb in row:row.symmetric_difference_update({cb})
  assert all(measure[8].bit not in row for row in dets)
  dets.append({measure[8].bit})
  measure[8].kind='MX';measure[8].time=R+2;measure[9].time=R+2
  ops.extend([f.Op('CX',(9,15),R),f.Op('CX',(8,9),R+1)])
  ops.sort(key=lambda o:o.time)
 meta=dict(data_qubits=data,source_commit=SHA,source_qasm=str(source.relative_to(ROOT))+'.qasm',source_qasm_sha256=hashlib.sha256(text.encode()).hexdigest(),R=R,native_depth=depth,CX=sum(o.kind=='CX'for o in ops),cx=sum(o.kind=='CX'for o in ops),method=__doc__,variant='two_CX_A_decoder'if decoded else'unmodified_control',changes=edits,official_class_tested=False,official_runtime_tested=False)
 if decoded:emit(ops,dets,stem,meta)
 else:
  stem.with_suffix('.qasm').write_text(text)
  stem.with_suffix('.json').write_text(json.dumps(meta,indent=2)+'\n')
 parsed,ds=f.parse_current(stem.with_suffix('.qasm').read_text())
 assert[(o.kind,o.qs,o.time,o.bit)for o in parsed]==[(o.kind,o.qs,o.time,o.bit)for o in ops]
 for t in range(depth):
  qubits=[q for o in parsed if o.time==t for q in o.qs];assert len(qubits)==len(set(qubits)),(t,qubits)
 assert all(abs(o.qs[0]//6-o.qs[1]//6)+abs(o.qs[0]%6-o.qs[1]%6)==1 for o in parsed if o.kind=='CX')
 f.DATA=data;m=f.make_model(parsed,ds);e=f.Engine(m);A,N=e.ntable(0,0)
 phi=e.phi(0);stabs=[e.expect(phi,(e.B.express(x),e._w(z),c))for x,z,c in m.gen_m]
 bad=[];c1p=0.
 for fault in m.faults:
  a,n=e.ntable(fault['s'],fault['d']);v=0. if n is None else fault['p']*n[fault['e']];c1p+=v
  if v>1e-15:bad.append(dict(contribution=v,label=fault['label'],pauli=fault['pauli'],qs=fault['qs']))
 cert=dict(ideal_acceptance=A,ideal_loss=float(N[0]),output_stabilizers=stabs,first_order_loss=c1p,harmful_single_fault_count=len(bad),harmful_single_examples=bad[:10],all_CX_nearest_neighbor=True,all_layers_disjoint=True,native_schedule_matches=all(step==o.time for o,entries in zip(parsed,m.steps)for qs,step in entries),qasm_sha256=hashlib.sha256(stem.with_suffix('.qasm').read_bytes()).hexdigest(),A_detector_rows=[sorted(row)for row in ds[14:17]],additional_flag=[16] if decoded else None)
 assert A>1-1e-10 and abs(N[0])<1e-10 and all(abs(s-1)<1e-10 for s in stabs)
 assert cert['native_schedule_matches']and not bad
 meta['independent_verification']=cert
 stem.with_suffix('.json').write_text(json.dumps(meta,indent=2)+'\n')
 print(json.dumps(dict(stem=str(stem),R=R,depth=depth,CX=meta['CX'],changes=edits,verification=cert)),flush=True)
 return stem
if __name__=='__main__':
 for name in sys.argv[1:]or['v30g','v31s']:
  for decoded in[False,True]:build(name,decoded)
