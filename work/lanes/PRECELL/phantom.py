"""Add single-helper gadgets to a full-barrier stem (one segment = one native tick); the helper may be a phantom.

usage: phantom.py <base stem> <out stem> spec ...
spec forms (h = helper qubit, d = data qubit, ticks a-b inclusive):
  eX:h:d:t1:t2      X-axis echo: RX h at t1-1, CX h->d at t1 and t2, MX h at t2+1 (detects Z/Y on d in between)
  eZ:h:d:t1:t2      Z-axis echo: R h at t1-1, CX d->h at t1 and t2, M h at t2+1 (detects X/Y on d)
  gX:h:d:a-b[,..]   guard, helper |+> as target: RX h before the first tick, CX d->h at every listed tick, MX after the last
  gZ:h:d:a-b[,..]   guard, helper |0> as control: R h, CX h->d at every listed tick, M after the last
  pX:h:d1,d2:t1:t2  X-type one-cell echo on two data: RX h at t1-1, CX h->d1 t1, h->d2 t1+1, h->d2 t2-1, h->d1 t2, MX t2+1
  pZ:h:d1,d2:t1:t2  Z-type version (CX d->h)
  gXm:h:t=d,t=d,..  multi-data guard (helper |+> target), one CX per listed tick; gZm likewise with |0> control
Every gadget's record is a singleton detector. Fails if a qubit is used twice in one tick or the helper is busy.
"""
import sys, re, json, shutil
sys.path.insert(0, '/home/jihoon/competitions/quantumn/work/lanes/EARLY')
from qedit import load

QRE = re.compile(r"q\[(\d+)\]")


def ticks(s):
    out = []
    for part in s.split(','):
        if '-' in part:
            a, b = map(int, part.split('-'))
            out += list(range(a, b + 1))
        else:
            out.append(int(part))
    return out


def build(base, out, specs):
    c = load(base)
    b0 = c.max_creg() + 1
    nb = 0
    adds = []  # (t, [lines])

    def rec():
        nonlocal nb
        nb += 1
        return b0 + nb - 1

    for s in specs:
        f = s.split(':')
        k, h = f[0], int(f[1])
        if k in ('eX', 'eZ'):
            d, t1, t2 = int(f[2]), int(f[3]), int(f[4])
            cx = f'cx q[{h}],q[{d}];' if k == 'eX' else f'cx q[{d}],q[{h}];'
            b = rec()
            adds += [(t1 - 1, [f'reset q[{h}];'] + ([f'h q[{h}];'] if k == 'eX' else [])), (t1, [cx]), (t2, [cx]),
                     (t2 + 1, ([f'h q[{h}];'] if k == 'eX' else []) + [f'measure q[{h}] -> c[{b}];'])]
        elif k in ('gX', 'gZ'):
            d, ts = int(f[2]), ticks(f[3])
            cx = f'cx q[{d}],q[{h}];' if k == 'gX' else f'cx q[{h}],q[{d}];'
            b = rec()
            adds += [(ts[0] - 1, [f'reset q[{h}];'] + ([f'h q[{h}];'] if k == 'gX' else []))]
            adds += [(t, [cx]) for t in ts]
            adds += [(ts[-1] + 1, ([f'h q[{h}];'] if k == 'gX' else []) + [f'measure q[{h}] -> c[{b}];'])]
        elif k in ('gXm', 'gZm'):
            seq = [tuple(map(int, x.split('='))) for x in f[2].split(',')]
            mk = (lambda d: f'cx q[{d}],q[{h}];') if k == 'gXm' else (lambda d: f'cx q[{h}],q[{d}];')
            b = rec()
            adds += [(seq[0][0] - 1, [f'reset q[{h}];'] + ([f'h q[{h}];'] if k == 'gXm' else []))]
            adds += [(t, [mk(d)]) for t, d in seq]
            adds += [(seq[-1][0] + 1, ([f'h q[{h}];'] if k == 'gXm' else []) + [f'measure q[{h}] -> c[{b}];'])]
        elif k in ('pX', 'pZ'):
            d1, d2 = map(int, f[2].split(','))
            t1, t2 = int(f[3]), int(f[4])
            mk = (lambda d: f'cx q[{h}],q[{d}];') if k == 'pX' else (lambda d: f'cx q[{d}],q[{h}];')
            b = rec()
            adds += [(t1 - 1, [f'reset q[{h}];'] + ([f'h q[{h}];'] if k == 'pX' else [])), (t1, [mk(d1)]), (t1 + 1, [mk(d2)]),
                     (t2 - 1, [mk(d2)]), (t2, [mk(d1)]),
                     (t2 + 1, ([f'h q[{h}];'] if k == 'pX' else []) + [f'measure q[{h}] -> c[{b}];'])]
        else:
            raise ValueError(s)
    for t, g in adds:
        c.segs[t].append(g)
    for t in range(len(c.segs)):
        seen = set()
        for g in c.segs[t]:
            qs = set()
            for ln in g:
                qs |= set(map(int, QRE.findall(ln)))
            assert not (qs & seen), (t, g, specs)
            seen |= qs
    c.header = [x if not x.startswith('creg') else f'creg c[{b0 + nb}];' for x in c.header]
    c.dets += [f'// DETECTOR c[{b0 + i}]' for i in range(nb)]
    open(out + '.qasm', 'w').write(c.text())
    meta = json.load(open(base + '.json'))
    meta['phantom'] = specs
    json.dump(meta, open(out + '.json', 'w'), indent=1)


if __name__ == '__main__':
    build(sys.argv[1], sys.argv[2], sys.argv[3:])
