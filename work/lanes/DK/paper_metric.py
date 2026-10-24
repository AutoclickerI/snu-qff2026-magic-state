"""Reproduce the DK paper's no-idle uniform depolarizing benchmark.

The paper applies preparation/measurement flips and uniform D1/D2 channels,
omits all idle noise, postselects the source flags/syndromes, then performs
ideal Steane syndrome decoding for the tomography.  This is deliberately a
separate score from the contest STANDARD evaluator.
"""
import os
os.environ.update(OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1', PYTHONDONTWRITEBYTECODE='1')
import argparse, json, multiprocessing as mp, warnings
from pathlib import Path
import importlib
import numpy as np

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
import sys
sys.path.insert(0, str(ROOT / 'upstream' / 'snu-qff2026-problem'))
import tprep.qasm as tq
tp = importlib.import_module('tprep.parse')
from tprep.noise import NoiseModel, apply_noise
import xtim
tc = importlib.import_module('tprep.check')

tq.adjacent = tp.adjacent = lambda a, b: True
PAPER = NoiseModel(gate1=1.0, gate2=1.0, meas=1.0, reset=1.0,
                   idle=0.0, meas_after=0.0, initial=0.0,
                   native_x=False, gates=None)


def one(arg):
    text, data, shots, seed = arg
    frame, post = tp.declarations(text)
    plan = tc.Plan(data, frame, post, tp.count_measurements(text))
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        # DK's final destructive tomography is a noisy physical readout in the
        # paper model.  A D1 channel on each output wire immediately before
        # the ideal Steane decoder is the equivalent Pauli-frame representation
        # used for the X/Y average.
        output_noise = '\n'.join(f'DEPOLARIZE1(0.001) {q}' for q in data)
        return tc._sample(xtim.Circuit(apply_noise(text, 1e-3, PAPER) + '\n' +
                                      output_noise + '\n' + plan.tail),
                          shots, seed, plan)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('stem', nargs='?', default='dk_paper')
    ap.add_argument('--shots', type=int, default=10_000_000)
    ap.add_argument('--procs', type=int, default=8)
    args = ap.parse_args()
    qasm = (BASE / (args.stem + '.qasm')).read_text()
    text, _, err = tq.convert(qasm, noise=PAPER)
    assert not err, err
    data = json.loads((BASE / (args.stem + '.json')).read_text())['data_qubits']
    rows = []
    for seed in [0, 1000, 2000]:
        jobs = [(text, data, min(1_000_000, args.shots - i), seed + i // 1_000_000)
                for i in range(0, args.shots, 1_000_000)]
        with mp.get_context('fork').Pool(args.procs) as pool:
            rs = pool.map(one, jobs)
        acc = sum(r['acceptance'] * j[2] for r, j in zip(rs, jobs))
        loss = sum(r['score'] * r['acceptance'] * j[2] for r, j in zip(rs, jobs)) / acc
        sem = sum((r['sem'] * r['acceptance'] * j[2]) ** 2 for r, j in zip(rs, jobs)) ** .5 / acc
        row = dict(seed=seed, shots=args.shots, loss=loss, sem=sem,
                   acceptance=acc / args.shots)
        rows.append(row)
        print(row, flush=True)
    out = dict(stem=args.stem, noise='DK uniform depolarizing; no idle; ideal final EC',
               p=1e-3, rows=rows, mean=float(np.mean([r['loss'] for r in rows])),
               acceptance=float(np.mean([r['acceptance'] for r in rows])))
    (BASE / (args.stem + '_paper_metric.json')).write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps(out, indent=2), flush=True)


if __name__ == '__main__':
    main()
