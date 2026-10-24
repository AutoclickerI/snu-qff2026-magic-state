"""Synthesized resource (syn/*.json) -> spliced v36c candidate (cand/<name>.qasm/.json) + proxy summary.
usage: mkcand.py <syn.json> <name> [policy]   policy: default | rzero (R for every |0> cell) | reuse"""
import sys, json
from pathlib import Path
from qcirc import parse
import splice
import proxy

B, C = splice.B, splice.C
CELLS = B + C
FRESH = {12, 25, 23, 27, 29, 26, 17, 28}           # never used before the resource
RELEASE = {4: 36, 5: 34, 6: 41, 11: 30, 13: 33, 19: 33}   # earliest init tick for reused cells
LITERAL0 = {5, 11, 13}                              # previous measurement is a literal-zero detector
PLUS_REUSE = {4: 36, 6: 41}                         # previous MX is a literal detector: |+> without an op


def spec_from(sol, policy='default', nonfresh=()):
    """nonfresh: fresh-set cells whose state before the resource is unknown (a base's gadget used them):
    a literal M init is invalid there -> R; an MX pivot init is valid on any state and stays MX."""
    T0 = sol['T0']
    cx = [[T0 + t, a, b] for t, layer in enumerate(sol['ops']) for a, b in layer]
    first = {}
    for t, a, b in cx:
        for q in (a, b):
            first[q] = min(first.get(q, 99), t)
    piv = set(int(q) for q in sol['pivots'])
    inits = {}
    extra = [[T0 + t, 'M', q] for t, q in sol.get('mids', [])]
    for q in sorted(first):
        if q in CELLS:
            continue
        last = max(t for t, a, b in cx if q in (a, b))
        extra.append([first[q] - 1, 'M' if policy != 'rzero' else 'R', q])
        extra.append([last + 1, 'M', q])
    for q in CELLS:
        f = first[q]
        t = f - 1
        rel = RELEASE.get(q, 0)
        assert t >= rel or (q in PLUS_REUSE and q in piv and f >= PLUS_REUSE[q]), (q, f, rel)
        if q in nonfresh and q not in piv:
            inits[str(q)] = ['R', t]
            continue
        if isinstance(policy, dict) and str(q) in policy:
            kind = policy[str(q)]
            if kind == 'none':
                continue
            inits[str(q)] = [kind, t]
            continue
        if q in piv:
            if q in PLUS_REUSE and policy in ('reuse',):
                continue  # no op: |+> left by the literal MX
            kind = 'MX' if q in FRESH else 'RX'
        else:
            if policy == 'rzero':
                kind = 'R'
            elif q in FRESH or q in LITERAL0:
                kind = 'M'
            else:
                kind = 'R'
        inits[str(q)] = [kind, t]
    return dict(inits=inits, cx=cx, extra=extra)


def starts_of(spec):
    st = {int(q): t for q, (k, t) in spec['inits'].items()}
    for t, k, q in spec['extra']:
        if q not in CELLS:
            st[q] = min(st.get(q, 99), t)
    return st


# v36d (INTEG gadgets on B/C cells): echo helpers q12 (MX@31) and q26 (MX@14) are not fresh -> R/RX inits;
# q25's echo ends with R@32 (kept), so its M init stays literal from tick 33; old prep found by v36c keys
BASE_NONFRESH = {'v36c': set(), 'v36d': {12, 26}}
BASE_ALSO = {'v36d': ([(37, 'R', (12,))], [(37, 'M', (12,))])}


def make(sol, name, policy='default', base='v36c'):
    here = Path(__file__).parent
    bu, bd = splice.load(here / base)
    spec = spec_from(sol, policy, BASE_NONFRESH[base])
    old = None
    if base != 'v36c':
        ru, _ = splice.load(here / 'v36c')
        also, absent = BASE_ALSO.get(base, ([], []))
        old = splice.prep_by_keys(bu, ru, also, absent)
    u, d, nb = splice.build(bu, bd, spec, old=old)
    stem = Path(__file__).parent / 'cand' / name
    splice.write(stem, u, d, nb, dict(source='BFLAG synth', policy=policy, syn=sol.get('tag')))
    flags = sorted({e[2] for e in spec['extra'] if e[2] not in CELLS})
    s, faults, groups = proxy.analyse(u, d, flags=flags, starts=starts_of(spec))
    return stem, s, spec


if __name__ == '__main__':
    sol = json.load(open(sys.argv[1]))
    sol['tag'] = sys.argv[1]
    pol = sys.argv[3] if len(sys.argv) > 3 else sol.get('policy', 'default')
    stem, s, spec = make(sol, sys.argv[2], pol, sys.argv[4] if len(sys.argv) > 4 else 'v36c')
    print(stem.name, json.dumps(s), 'cx', len(spec['cx']))
