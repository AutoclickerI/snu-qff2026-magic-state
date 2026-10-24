"""Finite-p exact-channel-event screening, before an all-orders evaluation.

For independent modeled channels, all no-error and exactly-one-error events
have known probability. Their accepted loss is nonnegative. Therefore their
loss numerator divided by an upper bound on total acceptance lower-bounds
the full loss. Algebra is exact; this implementation uses floating arithmetic
and reports a numerical screen, not an interval-arithmetic certificate.
"""
from pathlib import Path
import sys,json,math
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'audit/review6_tail'));import frontend as f

def evaluate(stem):
    meta=json.loads(stem.with_suffix('.json').read_text());f.DATA=meta['data_qubits']
    ops,dets=f.parse_current(stem.with_suffix('.qasm').read_text())
    old=f.noise_blocks
    f.noise_blocks=lambda txt,p,first_order=True:old(txt,p,first_order=False)
    try:m=f.make_model(ops,dets)
    finally:f.noise_blocks=old
    e=f.Engine(m);A0=e.A0;P0=math.prod(1-c['p']for c in m.chans)
    cache={};N1=A1=P1=0.0
    for fault in m.faults:
        key=fault['s'],fault['d']
        if key not in cache:cache[key]=e.ntable(*key)
        aa,nn=cache[key]
        weight=P0*fault['p']/(1-m.chans[fault['chan']]['p'])
        P1+=weight;A1+=weight*A0*aa
        if nn is not None:N1+=weight*A0*float(nn[fault['e']])
    Aupper=P0*A0+A1+(1-P0-P1)
    return dict(source=str(stem.relative_to(ROOT)),channels=len(m.chans),
        no_channel_error_probability=P0,one_channel_error_probability=P1,
        ideal_acceptance=A0,one_channel_accepted_mass=A1,one_channel_loss_numerator=N1,
        total_acceptance_upper_bound=Aupper,loss_lower_bound_numerical=N1/Aupper,
        limitation='Numerical screen; exact algebra, floating arithmetic. Aggregated idle channels are evaluated at their exact finite-p probability, not n*p.')

if __name__=='__main__':
    names=['audit/review6_architecture/v31s_a_decode',
           'audit/review7_objective/v31s_a_decode_drop2_15',
           'audit/review7_objective/v31s_a_decode_no_detectors']
    rows=[evaluate(ROOT/n)for n in names]
    (HERE/'finite_p_guard.json').write_text(json.dumps(dict(scope=__doc__,results=rows),indent=2)+'\n')
    print(json.dumps(rows,indent=2))
