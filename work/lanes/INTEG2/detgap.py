"""Record parities that are constant in the noiseless circuit but not in the span of the declared detectors.

T/TDG are replaced by identity (Clifford surrogate), the circuit is sampled noiselessly with stim, and the right kernel of
the record matrix (parities constant 0) is compared with the declared detectors. Candidates are verified later by the
all-orders evaluator, which rejects non-deterministic detectors.
usage: detgap.py <stem under c/> [surrogate: I|S|SDG] -> prints candidate parities (record bits) and writes detgap_<stem>.json
"""
import sys, re, json
from pathlib import Path
import numpy as np
import stim

H = Path(__file__).resolve().parent
stem = sys.argv[1]
sur = sys.argv[2] if len(sys.argv) > 2 else 'I'
txt = (H / 'c' / (stem + '.qasm')).read_text()
QRE = re.compile(r'q\[(\d+)\]'); CRE = re.compile(r'c\[(\d+)\]')
circ = stim.Circuit()
bits = []
for line in txt.splitlines():
    s = line.strip()
    if not s or s.startswith(('//', 'OPENQASM', 'include', 'qreg', 'creg', 'barrier')):
        continue
    name = s.split()[0]
    qs = [int(x) for x in QRE.findall(s)]
    if name == 'reset':
        circ.append('R', qs)
    elif name == 'h':
        circ.append('H', qs)
    elif name == 'cx':
        circ.append('CX', qs)
    elif name == 'measure':
        circ.append('M', qs); bits.append(int(CRE.findall(s)[0]))
    elif name in ('t', 'tdg'):
        g = {'I': None, 'S': 'S' if name == 't' else 'S_DAG', 'SDG': 'S_DAG' if name == 't' else 'S'}[sur]
        if g:
            circ.append(g, qs)
    elif name == 'id':
        pass
    else:
        raise ValueError(s)
dets = [sorted(set(map(int, CRE.findall(l)))) for l in txt.splitlines() if l.startswith('// DETECTOR')]
nm = len(bits)
col = {b: i for i, b in enumerate(bits)}
samp = circ.compile_sampler(seed=7).sample(20000)  # shots x nm (bool)
# right kernel {v : R v = 0} over GF(2): row-reduce the rows of R as bitmasks over measurement indices
rows = [int(''.join('1' if x else '0' for x in r[::-1]), 2) for r in np.unique(samp, axis=0)]
piv = {}
for v in rows:
    while v:
        h = v.bit_length() - 1
        if h in piv:
            v ^= piv[h]
        else:
            piv[h] = v; break
# reduced row echelon -> kernel basis
pivs = sorted(piv)
red = dict(piv)
for h in pivs:
    for k in pivs:
        if k != h and (red[k] >> h) & 1:
            red[k] ^= red[h]
free = [i for i in range(nm) if i not in red]
kernel = []
for f in free:
    v = 1 << f
    for h, r in red.items():
        if (r >> f) & 1:
            v |= 1 << h
    kernel.append(v)


def vec(bs):
    v = 0
    for b in bs:
        v ^= 1 << col[b]
    return v


D = [vec(d) for d in dets]
inker = [all(((r & d).bit_count() & 1) == 0 for r in rows) for d in D]
print('measurements', nm, 'kernel dim', len(kernel), 'detectors', len(D), 'not constant-0 under surrogate:',
      [dets[i] for i, ok in enumerate(inker) if not ok][:10])
# span of detectors, then extend by kernel vectors
span = {}


def reduce(v, sp):
    while v:
        h = v.bit_length() - 1
        if h in sp:
            v ^= sp[h]
        else:
            return v
    return 0


for d in D:
    r = reduce(d, span)
    if r:
        span[r.bit_length() - 1] = r
extra = []
for k in kernel:
    r = reduce(k, span)
    if r:
        span[r.bit_length() - 1] = r
        extra.append(r)
print('detector rank', len(span) - len(extra), 'extra deterministic parities', len(extra))
out = []
for v in extra:
    bs = [bits[i] for i in range(nm) if (v >> i) & 1]
    out.append(bs)
    print(bs)
(H / f'detgap_{stem}_{sur}.json').write_text(json.dumps(dict(extra=out, nondet_declared=[dets[i] for i, ok in enumerate(inker) if not ok])))
