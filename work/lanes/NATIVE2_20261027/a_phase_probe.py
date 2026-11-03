"""Matched noisy SX_A and S_B tests on the strict old-line preparation.

All four variants use the same source, A preparation, 48-tick terminal, B
verification at45, and helper reads at46. Only the real noisy Clifford pulses
differ. SX on early A7/A8 is at43 and on the other A cells at44; no later A
encoder gate touches the early cells. S_B is transversal at44.
"""
import argparse
import copy
import json
import sys
from pathlib import Path
from measured_assemble import HERE, ROOT
sys.path.insert(0, str(ROOT / 'work/lanes/EXPAND2_20261027'))
import axis_echo
import measured_assemble
import assemble_48_solution
import idle_parking48
import pairs
import record_contract


def build(park=False):
    original_a = json.loads((HERE / 'strict_oldline47_solution.json').read_text())
    original_b = json.loads((HERE / 'strict_oldline47_b_module.json').read_text())
    A, B, C = (original_b['roles'][k] for k in ('A', 'B', 'C'))
    previous = measured_assemble.f, idle_parking48.f, pairs.fa, record_contract.fa
    results = []
    try:
        measured_assemble.f = idle_parking48.f = pairs.fa = record_contract.fa = axis_echo.f
        for ax, bz in [(False, False), (True, False), (False, True), (True, True)]:
            name = f'a_phase_a{int(ax)}_b{int(bz)}'
            adoc, bdoc = copy.deepcopy(original_a), copy.deepcopy(original_b)
            if ax:
                adoc['operations'] += [dict(kind='SX', qs=[q], time=43 if q in (7, 8) else 44) for q in A]
            bops = bdoc['candidates'][0]['operations']
            moved_cx = moved_m = 0
            for op in bops:
                if op['kind'] == 'CX' and op['time'] == 44 and op['qs'][0] in B and op['qs'][1] in C:
                    op['time'] = 45
                    moved_cx += 1
                elif op['kind'] == 'M' and op['time'] == 45 and op['qs'][0] in C:
                    op['time'] = 46
                    moved_m += 1
            assert moved_cx == moved_m == 7, (moved_cx, moved_m)
            if bz:
                bops += [dict(kind='S', qs=[q], time=44) for q in B]
            adoc['phase_probe'] = dict(SX_A=ax, S_B=bz, all_native_noise=True)
            apath = HERE / f'{name}_solution.json'
            bpath = HERE / f'{name}_factory_b_module.json'
            apath.write_text(json.dumps(adoc, indent=2) + '\n')
            bpath.write_text(json.dumps(bdoc, indent=2) + '\n')
            result = assemble_48_solution.build(apath, bpath, name, end=48)
            if park and result['raw']['ok'] and result['singles']['c1'] < 1e-12:
                result['parked'] = idle_parking48.build(result['stem'], 3, 0, name + '_park')
            results.append(result)
            (HERE / 'a_phase_probe.result.json').write_text(json.dumps(results, indent=2) + '\n')
    finally:
        measured_assemble.f, idle_parking48.f, pairs.fa, record_contract.fa = previous
    return results


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--park', action='store_true')
    args = ap.parse_args()
    build(args.park)
