"""Finite-p distribution of nonidentity noise-channel counts.

This measures probability mass available to fault-order stratification.
It does not implement a new simulator or assert a measured wall-clock gain.
One aggregated idle channel counts once; its full finite-p probability is used.
"""
from pathlib import Path
import sys,json
import numpy as np
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'audit/review6_tail'))
import frontend as f

def run(rel):
    stem=ROOT/rel;md=json.loads(stem.with_suffix('.json').read_text())
    f.DATA=md['data_qubits'];ops,dets=f.parse_current(stem.with_suffix('.qasm').read_text())
    original=f.noise_blocks
    f.noise_blocks=lambda txt,p,first_order=True:original(txt,p,first_order=False)
    try:m=f.make_model(ops,dets)
    finally:f.noise_blocks=original
    dist=np.array([1.0])
    for c in m.chans:dist=np.convolve(dist,[1-c['p'],c['p']])
    assert abs(dist.sum()-1)<1e-12
    return dict(source=rel,channels=len(m.chans),mean_count=sum(c['p']for c in m.chans),
                count_probabilities_0_to_6=dist[:7].tolist(),
                probability_at_least_2=float(dist[2:].sum()),
                probability_at_least_3=float(dist[3:].sum()),
                probability_at_least_4=float(dist[4:].sum()),
                first_order_integrated_numerator_variance_ratio_upper_bound=float(dist[2:].sum()),
                numerical_note='Polynomial convolution uses double precision; no runtime/speedup benchmark implied.')

if __name__=='__main__':
    names=['quantumn_review8/work/lanes/MAIN/v35a']
    out=dict(scope=__doc__,results=[run(n)for n in names],
        variance_statement='For numerator contribution G and event E=K>=2, integrate E^c exactly and sample from E. Var(P(E)*mean(G|E))=P(E)^2*Var(G|E)/m <= P(E)*Var(G)/m by total variance. This is a fixed-sample variance bound for numerator estimation, not a wall-clock or finite-sample ratio-estimator guarantee.',
        ratio_note='Estimate acceptance with the same weighted samples and propagate joint covariance for N/A; do not report unweighted conditional scores or silently alter the noise distribution.',
        official_note='Final validation remains the unmodified official judge with its specified chunks/seeds.')
    (HERE/'fault_order_budget.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))
