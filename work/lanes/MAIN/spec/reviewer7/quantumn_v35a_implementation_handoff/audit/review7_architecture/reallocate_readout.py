"""Use part of the reclaimed q20-echo acceptance budget on C readout encoding.

One bounded variant only: actual noisy CX28->29 at46; move both MZ to47;
invertibly rewrite every detector containing c26 by XOR c27.
"""
from pathlib import Path
import json,hashlib,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'audit/reaudit_evaluation/portable'))
import frontend as f
from circuit_io import emit
from judge_subset.noise import noise_blocks,schedule
src=HERE/'v32p_a_decode_remove_z26';target=HERE/'v32p_a_decode_budget_c'
md=json.loads(src.with_suffix('.json').read_text());text=src.with_suffix('.qasm').read_text()
ops,ds=f.parse_current(text)
for q,bit in[(28,27),(29,26)]:
 ms=[o for o in ops if o.kind=='M'and o.qs==(q,)and o.time==46]
 assert len(ms)==1 and ms[0].bit==bit
 ms[0].time=47
assert not any(o.time==46 and set(o.qs)&{28,29}for o in ops)
ops.append(f.Op('CX',(28,29),46));ops.sort(key=lambda o:o.time)
for row in ds:
 if 26 in row:row.symmetric_difference_update({27})
meta=dict(data_qubits=md['data_qubits'],source_commit=md['source_commit'],method=__doc__,
          input_qasm=src.name+'.qasm',input_qasm_sha256=hashlib.sha256(text.encode()).hexdigest(),
          CX=sum(o.kind=='CX'for o in ops),native_depth=max(o.time for o in ops)+1,
          official_class_tested=False,official_runtime_tested=False)
emit(ops,ds,target,meta)
native,_=f.native_text(ops);prog,blocks=noise_blocks(native,.001)
for ins,block in zip(prog,blocks):
 if ins.name=='CX'and tuple(ins.qubits)==(28,29):
  assert block[block.index(ins.text)+1]=='DEPOLARIZE2(0.001) 28 29'
f.DATA=md['data_qubits'];m=f.make_model(ops,ds);e=f.Engine(m);A,N=e.ntable(0,0)
first=0.;bad=0
for fault in m.faults:
 a,n=e.ntable(fault['s'],fault['d']);v=0 if n is None else fault['p']*n[fault['e']]
 first+=v;bad+=v>1e-15
cert=dict(ideal_acceptance=A,ideal_loss=float(N[0]),first_order_loss=float(first),harmful_single_fault_count=int(bad),
          native_schedule_matches=all(step==o.time for o,steps in zip(ops,m.steps)for qs,step in steps),
          noisy_added_CX=True,qasm_sha256=hashlib.sha256(target.with_suffix('.qasm').read_bytes()).hexdigest())
assert A>1-1e-10 and abs(N[0])<1e-10 and not bad and cert['native_schedule_matches']
meta['independent_verification']=cert
target.with_suffix('.json').write_text(json.dumps(meta,indent=2)+'\n')
print(json.dumps(dict(name=target.name,**cert)),flush=True)
