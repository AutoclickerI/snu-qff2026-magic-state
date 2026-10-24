"""Equivalent final Bell readout representation, for a bounded sampler probe.

CX8->9; MX8,MZ9 and CX9->8; MZ8,MX9 measure the same XX/ZZ
observables with the two record labels exchanged. Depolarizing2 and equal
native measurement-error rates preserve this equality of noisy POVMs. Both
qubits are discarded after readout; their post-measurement states are unused.
This is a representation/speed experiment, not a new lower-loss circuit.
"""
from pathlib import Path
import sys,json,hashlib
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'audit/review5_tail'))
import frontend as f
from circuit_io import emit,certify

src=ROOT/'audit/review6_tail/v31s_a_decode_sx'
ops,dets=f.parse_current(src.with_suffix('.qasm').read_text())
data=json.loads(src.with_suffix('.json').read_text())['data_qubits']
gate=[o for o in ops if o.kind=='CX' and o.qs==(8,9) and o.time==46]
assert len(gate)==1
gate[0].qs=(9,8)
a=[o for o in ops if o.kind=='MX' and o.qs==(8,) and o.time==47]
b=[o for o in ops if o.kind=='M' and o.qs==(9,) and o.time==47]
assert len(a)==len(b)==1 and a[0].bit==16 and b[0].bit==17
a[0].kind='M';b[0].kind='MX'
def remap(bit):return 17 if bit==16 else 16 if bit==17 else bit
dets=[set(remap(bit)for bit in row)for row in dets]
stem=HERE/'v31s_a_decode_sx_bellflip'
emit(ops,dets,stem,data,metadata=dict(scope=__doc__,physical_noise_equivalent_to=str(src)))
check=certify(ops,dets,data,f)
check.update(qasm_sha256=hashlib.sha256(stem.with_suffix('.qasm').read_bytes()).hexdigest(),
             original_sha256=hashlib.sha256(src.with_suffix('.qasm').read_bytes()).hexdigest(),
             score_claim='Same noisy measurement instrument as source; not a measured new score')
stem.with_name(stem.name+'_certificate.json').write_text(json.dumps(check,indent=2)+'\n')
print(json.dumps(check,indent=2))
