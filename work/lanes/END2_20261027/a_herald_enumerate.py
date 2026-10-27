"""Enumerate distinct directed-CNOT multisets for the strong48 A resource.

The enumeration excludes timing-only variants and some alternative orders of
the same multiset. Its exhaustion is therefore not a bound on all encoders.
Each retained witness still receives the state and phase audit in the solver.
"""
import json
from pathlib import Path
from a_herald_cp import solve

HERE=Path(__file__).resolve().parent


def main():
    boundary=HERE/'prefix_native_m9_drop15.json'
    existing=json.loads((HERE/'sol/a_herald_R45_early7_8_no8_earlysource_native_m9_drop15.json').read_text())
    excluded=[existing['ops']]
    rows=[]
    for index in range(1,9):
        result=solve(45,(7,8),30,seed=index+1,cap=11,no8=True,
                     boundary=boundary,tag=f'native_m9_distinct{index}',excluded_multisets=excluded)
        rows.append(result)
        (HERE/'a_herald_enumerate.json').write_text(json.dumps(dict(
            scope='Bounded enumeration of distinct directed-CX multisets at11CX. Full source/noise pricing is separate.',
            base='sol/a_herald_R45_early7_8_no8_earlysource_native_m9_drop15.json',
            candidates=rows),indent=2)+'\n')
        if result['status'] not in ('FEASIBLE','OPTIMAL'):break
        excluded.append(result['ops'])


if __name__=='__main__':main()
