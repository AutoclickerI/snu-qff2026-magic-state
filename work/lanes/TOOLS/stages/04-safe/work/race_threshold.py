"""Official 3-significant-digit comparator; threshold is the first losing double.

No credentials or network access. The controller supplies the confirmed board
incumbent in receipts/race_incumbent.json; passed sequential picks and completed
draws can only strengthen it. Candidates are always later than the incumbent.
"""
import argparse
import glob
import json
import math
import re
import struct
from pathlib import Path


def published(score):
    # tprep/check.py Report.__str__, official problem section 2.3.
    return float(format(score, '.3g'))


def wins(score, cx, incumbent_key, incumbent_cx, *, earlier=False):
    return (published(score), cx, 0 if earlier else 2) < (incumbent_key, incumbent_cx, 1)


def first_losing(incumbent_key, incumbent_cx, candidate_cx, *, earlier=False):
    if not math.isfinite(incumbent_key) or incumbent_key <= 0:
        raise ValueError('incumbent key must be positive and finite')
    if published(incumbent_key) != incumbent_key:
        raise ValueError('incumbent key must already be formatted')
    if min(incumbent_cx, candidate_cx) < 0:
        raise ValueError('negative gate count')
    # Nonnegative finite binary64 values have the same bit order as numeric order.
    lo, hi = 0, 0x7ff0000000000000  # +0 wins; +inf loses
    while hi - lo > 1:
        mid = (lo + hi) // 2
        x = struct.unpack('>d', struct.pack('>Q', mid))[0]
        if wins(x, candidate_cx, incumbent_key, incumbent_cx, earlier=earlier):
            lo = mid
        else:
            hi = mid
    return struct.unpack('>d', struct.pack('>Q', hi))[0]


def cx_count(path):
    text = re.sub(r'//[^\n]*', '', Path(path).read_text())
    return sum(bool(re.match(r'\s*cx\s', s)) for s in text.split(';'))


def controller_threshold(candidate, work, log_pattern=None):
    best = json.loads((work / 'receipts/race_incumbent.json').read_text())
    assert published(best['score']) == best['score_key']
    incumbents = [(best['score_key'], best['n_2q'])]
    for receipt in (work / 'receipts').glob('seq_*.txt'):
        if 'RESULT: PASS' not in receipt.read_text():
            continue
        path = work / 'submissions' / (receipt.stem[4:] + '.json')
        if not path.exists():
            raise ValueError(f'missing score for passed pick: {path}')
        pick = json.loads(path.read_text())
        incumbents.append((published(pick['score']), pick['n_2q']))
    if log_pattern:
        for path in glob.glob(log_pattern):
            for line in Path(path).read_text().splitlines():
                m = re.fullmatch(r'\S+ 1-F (\S+) acc \S+ 2q (\d+) pass True', line)
                if m:
                    incumbents.append((published(float(m[1])), int(m[2])))
    key, cx = min(incumbents)
    return first_losing(key, cx, cx_count(candidate))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('candidate')
    parser.add_argument('--work', type=Path, default=Path('.'))
    parser.add_argument('--logs')
    args = parser.parse_args()
    print(repr(controller_threshold(args.candidate, args.work, args.logs)))
