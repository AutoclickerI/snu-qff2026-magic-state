"""Exact residual checks and historical trace audit; no invented tail-gain estimate.

Optional --traces directory: complete Journal files from a separately collected,
uncensored stream, in candidate order. A single selected winner is not held-out data.
"""
import argparse
import importlib.util
import json
import math
from pathlib import Path
import re
import sys
import numpy as np

LANE = Path(__file__).resolve().parents[1]
REPO = LANE.parents[2]
sys.path[:0] = [str(LANE/'patched/work'),str(REPO/'work')]
from race_checkpoint import Journal


def load(name,path):
    spec = importlib.util.spec_from_file_location(name,path)
    mod = importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    return mod


def replay_policy(mod, paths, exact, threshold, budget):
    mod._G.update(exact=exact,totals=[],kepts=[])
    used = hits = completed = 0
    for obj in paths:
        kept = 0; total = 0.
        for c,row in enumerate(obj['chunks']):
            if c in mod.CHECKS and mod._p_below(kept,total,c,threshold) < mod.KAPPA*mod._p_below(0,0.,0,threshold):
                break
            if used >= budget:
                return dict(chunks=used,hits=hits,completed=completed)
            s = float.fromhex(row['loss']); a = row['kept']
            kept += a;total += s;used += 1
            mod._G['totals'].append(s);mod._G['kepts'].append(a)
        else:
            completed += 1
            hits += total/kept < threshold and kept/(mod.N_CHUNKS*mod.tc.CHUNK) >= .5
    return dict(chunks=used,hits=hits,completed=completed)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--traces',type=Path)
    args = parser.parse_args()
    old = load('old_race',LANE/'baseline/work/race.py')
    new = load('exact_race',LANE/'stages/03/work/race.py')
    a,loss = .5016415049479505,3.815473322483099e-5
    numerator = a*loss
    rng = np.random.default_rng(62130)
    ks = rng.integers(499000,504000,200)
    ss = rng.normal(new.tc.CHUNK*numerator,4.,200)
    new._G.update(exact=(a,numerator),totals=list(ss),kepts=list(ks))
    checks = []
    for tau in (3.525e-5,3.535e-5,loss,4.2e-5):
        mu = new.tc.CHUNK*(numerator-tau*a)
        variance = sum((float(s)-tau*int(k)-mu)**2 for s,k in zip(ss,ks))/len(ss)
        for c in (0,1,3,30,80,99):
            kept,total = int(sum(ks[:c])),float(sum(ss[:c]))
            expected = .5*math.erfc(((total-tau*kept)+(100-c)*mu)/math.sqrt(2*(100-c)*variance))
            actual = new._p_below(kept,total,c,tau)
            assert abs(actual-expected) < 1e-14
            checks.append(dict(c=c,tau=tau,expected=expected,actual=actual))
    logs = sorted((REPO/'work/reorder').glob('*.log'))
    dropped = completed = 0
    for path in logs:
        text = path.read_text(errors='replace')
        dropped += len(re.findall(r'dropped after \d+ chunks',text))
        completed += len(re.findall(r' 1-F \S+ acc \S+ 2q \d+ pass (?:True|False)',text))
    # The logger source stores no S,K values; receipts have final aggregates only.
    candidates = list((REPO/'work/receipts').glob('**/*.jsonl')) + list((REPO/'work/reorder').glob('**/*.jsonl'))
    receipt = dict(status='PASS_FORMULA; REJECT_DEPLOYMENT_NO_HELD_OUT_TRACES',formula_checks=checks,
                   historical_inventory=dict(log_files=len(logs),drop_records=dropped,completion_records=completed,
                                             jsonl_files=len(candidates)),
                   historical_hits_per_chunk=None,equal_compute_improvement=None,
                   reason='Historical logs omit per-chunk loss sums and accepted counts; dropped paths are censored.')
    if args.traces:
        paths = [Journal.read(p) for p in sorted(args.traces.glob('*.json'))]
        assert paths and all(len(p['chunks']) == new.N_CHUNKS for p in paths),'need full uncensored paths'
        stem = REPO/'work/lanes/MAIN/v36h'
        reference = new.signature(stem.with_suffix('.qasm').read_text())
        data = json.loads(stem.with_suffix('.json').read_text())['data_qubits']
        for p in paths:
            assert new.signature(p['header']['qasm']) == reference,'replay expects v36h re-draws'
            assert p['header']['data_qubits'] == data
            assert p['header']['chunk_shots'] == new.tc.CHUNK
        tau = 3.525e-5
        results = [replay_policy(m,paths,(a,numerator),tau,10**12) for m in (old,new)]
        budget = min(r['chunks'] for r in results)
        equal = [replay_policy(m,paths,(a,numerator),tau,budget) for m in (old,new)]
        receipt['replay'] = dict(budget=budget,old=equal[0],exact=equal[1])
    (LANE/'receipts/03_policy.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:v for k,v in receipt.items() if k!='formula_checks'}))


if __name__ == '__main__':
    main()
