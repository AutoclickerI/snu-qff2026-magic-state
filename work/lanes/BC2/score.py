"""Judge-validity, exact --third-equivalent screen, then required MC seeds."""
import argparse
import dataclasses
import json
import math
import os
from pathlib import Path
import sys
import time

ROOT = Path('/home/jihoon/competitions/quantumn')
sys.path[:0] = [str(ROOT/'work/lanes/EVAL'), str(ROOT/'work')]
import exact2
import fast_check
import tprep


def record(r):
    d = dataclasses.asdict(r)
    d['passed'] = r.passed
    return d


def score(stem, procs, force_mc=False):
    stem = Path(stem)
    out = stem.with_suffix('.score.json')
    text = stem.with_suffix('.qasm').read_text()
    data = json.loads(stem.with_suffix('.json').read_text())['data_qubits']
    r = json.loads(out.read_text()) if out.exists() else {}
    def save(): out.write_text(json.dumps(r, indent=2))
    if 'check_1e6' not in r:
        rep = tprep.check(text, data, shots=10**6, seed=0)
        r['check_1e6'] = record(rep); save()
        print(stem, rep, flush=True)
    if not r['check_1e6']['passed']:
        return r
    if 'exact' not in r:
        ev = exact2.Eval(text, data)
        x = exact2.run(ev, procs, third=True)
        x3 = exact2.third_order(ev, procs)[0] + x['t3bc'] if abs(x['loss1']) < 1e-12 else None
        r['exact'] = dict(c1=x['loss1'], second=x['loss2'], third=x3,
                          total=x['loss']+x3 if x3 is not None else None, exp_minus_A1=math.exp(-x['A1']))
        save(); print(stem, r['exact'], flush=True)
    x = r['exact']
    eligible = force_mc or (x['total'] is not None and x['total'] <= 1.03*1.01894e-4) or (1e-12 <= abs(x['c1']) <= 1.0382e-4)
    if eligible:
        r.setdefault('MC', {})
        for seed in (0,1000,2000):
            if str(seed) not in r['MC']:
                rep = fast_check.check(text, data, shots=10**8, seed=seed, procs=procs)
                r['MC'][str(seed)] = record(rep); save()
                print(stem, 'MC', seed, rep.score, rep.acceptance, flush=True)
        r['mean'] = sum(v['score'] for v in r['MC'].values())/3
        save()
    return r


if __name__ == '__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('stems',nargs='+')
    ap.add_argument('--procs',type=int,default=12)
    ap.add_argument('--force-mc',action='store_true')
    a=ap.parse_args()
    for stem in a.stems:
        print(json.dumps(score(stem,a.procs,a.force_mc)),flush=True)
