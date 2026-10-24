"""Write the asearch stdin: kappa, alpha, params, per-position windows (v36c exterior)."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyze import Table
from bmodel import A, REL, DA
MR_OK = {1: 1, 14: 0, 8: 1, 9: 1, 2: 0, 16: 1, 15: 1}


def write(table, out, maxcx, K, pivmask=-1, tmin=36, tmax=43, rel=REL, da=DA):
    T = Table(table)
    lines = [' '.join(f'{x:.17g}' for x in T.kappa), ' '.join(f'{x:.17g}' for x in T.alpha),
             f'{maxcx} {K} {pivmask} {tmin} {tmax}']
    for q in A:
        lines.append(f'{rel[q]} {da[q]} {MR_OK[q]}')
    Path(out).write_text('\n'.join(lines) + '\n')


if __name__ == '__main__':
    write(sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]) if len(sys.argv) > 5 else -1)
