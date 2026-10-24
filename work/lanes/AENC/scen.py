"""Exterior window scenarios for asearch (per A cell: REL, DA, ZMR tick or -1, PMR)."""
import sys, json, itertools
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyze import Table
from bmodel import A

BASE = {1: [37, 44, 37, 0], 14: [36, 44, -1, 0], 8: [35, 44, 35, 0], 9: [37, 43, 37, 0],
        2: [35, 44, -1, 0], 16: [37, 44, 37, 0], 15: [39, 43, 39, 0]}
MODS = {
    'mxreuse': {14: dict(pmr=1), 2: dict(pmr=1)},                       # q2/q14 pivots straight from their MX release
    'flag89': {15: dict(da=44), 8: dict(da=43)},                       # decoder CX9->8 @44, CX15->9 @45, MX15
    'dropchk': {8: dict(rel=34, zmr=34), 9: dict(rel=36, zmr=36), 15: dict(rel=38, zmr=38), 16: dict(rel=36, zmr=36)},
    'drop15': {15: dict(rel=38, zmr=38)},
    'drop15r': {15: dict(rel=38, zmr=-1)},     # M57 removed, q15 reset (R/RX) in region
    'drop9r': {9: dict(rel=36, zmr=-1)},
    'drop16r': {16: dict(rel=36, zmr=-1)},
    'drop8r': {8: dict(rel=34, zmr=-1)},
    'drop9': {9: dict(rel=36, zmr=36)},
    'drop16': {16: dict(rel=36, zmr=36)},
    'drop8': {8: dict(rel=34, zmr=34)},
}
for k in (1, 2, 3, 4):
    MODS[f'early{k}'] = {q: dict(rel=v[0] - k, zmr=(v[2] - k if v[2] >= 0 else -1)) for q, v in BASE.items()}


def params(names):
    P = {q: list(v) for q, v in BASE.items()}
    for n in names:
        for q, d in MODS[n].items():
            if 'rel' in d: P[q][0] = d['rel']
            if 'da' in d: P[q][1] = d['da']
            if 'zmr' in d: P[q][2] = d['zmr']
            if 'pmr' in d: P[q][3] = d['pmr']
    return P


def write(table, out, names, maxcx=16, K=200000):
    T = Table(table)
    P = params(names)
    lines = [' '.join(f'{x:.17g}' for x in T.kappa), ' '.join(f'{x:.17g}' for x in T.alpha),
             f'{maxcx} {K} -1 {min(P[q][0] for q in A) + 1} 43']
    for q in A:
        lines.append(' '.join(map(str, P[q])))
    Path(out).write_text('\n'.join(lines) + '\n')


if __name__ == '__main__':
    table = sys.argv[1]
    if len(sys.argv) > 2:
        for c in sys.argv[2:]:
            names = c.split('+'); write(table, f'scen_{c}.txt', names); print(c)
        sys.exit()
    combos = [[]] + [[n] for n in MODS] + [['mxreuse', 'flag89'], ['mxreuse', 'dropchk'], ['flag89', 'dropchk'],
                                          ['mxreuse', 'flag89', 'dropchk'], ['flag89', 'drop15'], ['mxreuse', 'flag89', 'drop15']]
    for c in combos:
        name = '+'.join(c) or 'base'
        write(table, f'scen_{name}.txt', c)
        print(name)
