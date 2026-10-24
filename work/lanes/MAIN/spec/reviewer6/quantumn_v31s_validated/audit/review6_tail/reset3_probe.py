"""Bounded, fully repriced repair for a carried random-MX sampler path.

Change three first-use B/C pivot MXs at tick33 into native RX; delete only
their known byproduct terms from B detector rows. This changes preparation
noise and therefore is not claimed to preserve the noisy physical channel.
"""
from pathlib import Path
import json,hashlib
import frontend as fa
from circuit_io import emit,certify
from judge_subset.noise import noise_blocks,schedule
HERE=Path(__file__).resolve().parent
REMOVED={26:256,17:260,28:262}
for name,source in [('v31s_a_decode_reset3',HERE/'inputs/v31s_a_decode'),
                    ('v31s_a_decode_sx_reset3',HERE/'v31s_a_decode_sx')]:
    text=source.with_suffix('.qasm').read_text();md=json.loads(source.with_suffix('.json').read_text())
    ops,dets=fa.parse_current(text);before=[set(d)for d in dets]
    for q,bit in REMOVED.items():
        uses=[o for o in ops if q in o.qs]
        first=uses[0]
        assert first.kind=='MX'and first.qs==(q,)and first.time==33 and first.bit==bit,(q,first)
        first.kind='RX';first.bit=None
    for d in dets:d.difference_update(REMOVED.values())
    changes={i:sorted(before[i]-d)for i,d in enumerate(dets)if before[i]!=d}
    assert changes=={17:[260,262],18:[256],19:[260]},changes
    stem=HERE/name
    emit(ops,dets,stem,md['data_qubits'],metadata=dict(scope=__doc__,
         source_commit='abf26aa98bede59bb07f7da838dd1b3a3fdf76f0',input=source.name,
         input_qasm_sha256=hashlib.sha256(text.encode()).hexdigest(),
         reset3_at_tick=33,removed_frame_bits=REMOVED,changed_detector_rows=changes))
    native,_=fa.native_text(ops);prog,blocks=noise_blocks(native,.001)
    resets=[]
    for ins,block in zip(prog,blocks):
        if ins.name=='RX'and ins.qubits[0]in REMOVED:
            assert block[block.index(ins.text)+1]==f'Z_ERROR(0.001) {ins.qubits[0]}'
            resets.append(ins.qubits[0])
    assert sorted(resets)==sorted(REMOVED)
    _,steps,_=schedule(native);depth=max(t for groups in steps for _,t in groups)+1
    assert depth==48
    result=dict(name=name,native_depth=depth,native_RX_error_channels=resets,
         changed_detector_rows=changes,qasm_sha256=hashlib.sha256(stem.with_suffix('.qasm').read_bytes()).hexdigest(),
         **certify(ops,dets,md['data_qubits'],fa))
    stem.with_name(stem.name+'_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result),flush=True)
