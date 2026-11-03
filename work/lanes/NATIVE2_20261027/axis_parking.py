"""Add plus-spare checks to a native S/Sdg circuit using the validated local frontend.

Only this process's lane-module references are changed. Shared qtools and the
official judge remain untouched. Exact pricing uses EXPAND2.axis_echo.exact,
which records the lane frontend hash and retains all native pulse noise.
"""
import argparse
import json
import sys
from pathlib import Path
from measured_assemble import HERE, ROOT
sys.path.insert(0, str(ROOT / 'work/lanes/EXPAND2_20261027'))
import axis_echo
import idle_parking48
import pairs
import record_contract


def build(stem, name='b_phase_s_park', do_price=False):
    previous = idle_parking48.f, pairs.fa, record_contract.fa
    try:
        idle_parking48.f = pairs.fa = record_contract.fa = axis_echo.f
        result = idle_parking48.build(stem, 3, 0, name)
    finally:
        idle_parking48.f, pairs.fa, record_contract.fa = previous
    result['audit_frontend'] = str(Path(axis_echo.f.__file__))
    if do_price and result['raw']['ok'] and result['singles']['c1'] < 1e-12:
        result['exact'] = axis_echo.exact(result['stem'])
        Path(result['stem']).with_suffix('.exact.json').write_text(json.dumps(result['exact'], indent=2) + '\n')
    (HERE / f'{name}.result.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2), flush=True)
    return result


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('stem')
    ap.add_argument('--name', default='b_phase_s_park')
    ap.add_argument('--price', action='store_true')
    args = ap.parse_args()
    build(args.stem, args.name, args.price)
