"""Two physics-identical final-tick orderings for an xtim timing diagnosis.

Only disjoint last-tick operations are reordered. Every per-wire operation,
measurement bit, gate direction and tick is identical to the scored source.
The numerical loss receipt of that source must not be treated as a new MC run.
"""
from pathlib import Path
import json,hashlib
import frontend as fa
from circuit_io import emit
from judge_subset.noise import noise_blocks,schedule
HERE=Path(__file__).resolve().parent
source=HERE/'v31s_a_decode_sx'
text=source.with_suffix('.qasm').read_text();md=json.loads(source.with_suffix('.json').read_text())
original,dets=fa.parse_current(text);end=max(o.time for o in original)
B={6,26,13,11,4,23,27};C={12,25,19,17,5,29,28}
def wire_ops(ops):
    return {q:[(o.kind,o.qs,o.time,o.bit)for o in ops if q in o.qs]for q in range(36)}
def noisy_wire_ops(ops):
    native,_=fa.native_text(ops);_,blocks=noise_blocks(native,.001)
    import re
    out={q:[]for q in range(36)}
    for bl in blocks:
        for line in bl:
            if line.startswith(('DETECTOR','TICK')):continue
            targets=[int(x)for x in line.split()[1:]if x.isdigit()]
            for q in targets:out[q].append(line)
    return out
reference_wire=wire_ops(original);reference_noise=noisy_wire_ops(original)
certs=[]
for name,first,second in [('c_b_a8',C,B),('b_c_a8',B,C)]:
    def priority(o):
        if o.kind=='SXDG':return 4
        if o.kind in ['M','MX']and o.qs[0]in first:return 0
        if o.kind in ['M','MX']and o.qs[0]in second:return 1
        if o.kind=='MX'and o.qs==(8,):return 3
        return 2
    oo=[o for o in original if o.time<end]+sorted([o for o in original if o.time==end],key=priority)
    assert wire_ops(oo)==reference_wire
    assert noisy_wire_ops(oo)==reference_noise
    stem=HERE/('v31s_a_decode_sx_order_'+name)
    emit(oo,dets,stem,md['data_qubits'],metadata=dict(scope=__doc__,source_commit=md['source_commit'],
         input=source.name,input_qasm_sha256=hashlib.sha256(text.encode()).hexdigest(),
         same_physical_channel=True,per_wire_noisy_instruction_streams_identical=True))
    cert=dict(name=stem.name,source=source.name,native_depth=end+1,
         per_wire_operations_identical=True,per_wire_noisy_instruction_streams_identical=True,
         final_order=[(o.kind,o.qs,o.bit)for o in oo if o.time==end],
         qasm_sha256=hashlib.sha256(stem.with_suffix('.qasm').read_bytes()).hexdigest())
    certs.append(cert);print(json.dumps(cert),flush=True)
(HERE/'terminal_order_certificate.json').write_text(json.dumps(certs,indent=2)+'\n')
