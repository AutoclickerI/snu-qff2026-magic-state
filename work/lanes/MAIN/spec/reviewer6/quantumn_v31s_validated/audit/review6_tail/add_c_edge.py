"""Bounded final C readout refinement on the v31s A-decoder/SX candidate.

CX28->29 replaces two final C readout slots by one noisy CX; both readouts
move to the existing last tick and detector rows are changed invertibly.
"""
from pathlib import Path
import json,hashlib
import frontend as fa
from circuit_io import emit,certify
from judge_subset.noise import noise_blocks,schedule
HERE=Path(__file__).resolve().parent
source=HERE/'v31s_a_decode_sx';target=HERE/'v31s_a_decode_sx_c28_29'
text=source.with_suffix('.qasm').read_text();md=json.loads(source.with_suffix('.json').read_text())
ops,dets=fa.parse_current(text)
for q,bit in [(28,27),(29,26)]:
    mm=[o for o in ops if o.qs==(q,)and o.kind=='M'and o.time==46]
    assert len(mm)==1 and mm[0].bit==bit,(q,mm)
    mm[0].time=47
assert not any(o.time==46 and set(o.qs)&{28,29}for o in ops)
ops.append(fa.Op('CX',(28,29),46));ops.sort(key=lambda o:o.time)
for d in dets:
    if 26 in d:d.symmetric_difference_update({27})
emit(ops,dets,target,md['data_qubits'],metadata=dict(scope=__doc__,
     source_commit=md['source_commit'],input=source.name,
     input_qasm_sha256=hashlib.sha256(text.encode()).hexdigest()))
native,_=fa.native_text(ops);prog,blocks=noise_blocks(native,.001)
sxnoise=[];cxnoise=[]
for ins,block in zip(prog,blocks):
    if ins.name in ['SQRT_X','SQRT_X_DAG']:
        assert block[block.index(ins.text)+1]==f'DEPOLARIZE1(0.001) {ins.qubits[0]}'
        sxnoise.append(ins.text)
    if ins.name=='CX'and tuple(ins.qubits)==(28,29):
        assert block[block.index(ins.text)+1]=='DEPOLARIZE2(0.001) 28 29'
        cxnoise.append(ins.text)
assert len(sxnoise)==14 and cxnoise
_,steps,_=schedule(native);depth=max(t for groups in steps for _,t in groups)+1
assert depth==48
cert=dict(name=target.name,physical_gauge_noise_channels=14,native_depth=depth,
          added_CX_noisy=True,qasm_sha256=hashlib.sha256(target.with_suffix('.qasm').read_bytes()).hexdigest(),
          **certify(ops,dets,md['data_qubits'],fa))
target.with_name(target.name+'_certificate.json').write_text(json.dumps(cert,indent=2)+'\n')
print(json.dumps(cert),flush=True)
