"""Find echo/guard readouts followed by a same-basis re-init of the same helper: scan_merge.py <stem>.
Prints helper, readout tick/kind, re-init tick/kind, the helper's last CX (tick, partner) and the partner's idle ticks
between that CX and the re-init (where the readout CX could move)."""
import sys, re
sys.path.insert(0, '/home/jihoon/competitions/quantumn/work/lanes/EARLY')
from qedit import load
QRE = re.compile(r"q\[(\d+)\]")
c = load(sys.argv[1])
ops = {}
for t, seg in enumerate(c.segs):
    for g in seg:
        j = ' '.join(g)
        qs = list(map(int, QRE.findall(j)))
        if g[0].startswith('cx'):
            k = 'CX'
        elif 'measure' in j:
            k = 'MX' if g[0].startswith('h') else 'M'
        elif g[0].startswith('reset'):
            k = 'RX' if len(g) > 1 else 'R'
        else:
            k = g[0].split()[0]
        for q in set(qs):
            ops.setdefault(q, []).append((t, k, qs))
busy = {(q, t) for q, l in ops.items() for t, _, _ in l}
for q, l in sorted(ops.items()):
    for a, b in zip(l, l[1:]):
        if a[1] in ('M', 'MX') and b[1] in ('R', 'RX') and (a[1] == 'M') == (b[1] == 'R'):
            prev = [x for x in l if x[0] < a[0]]
            cx = prev[-1] if prev and prev[-1][1] == 'CX' else None
            if not cx:
                continue
            d = [x for x in cx[2] if x != q][0]
            free = [t for t in range(cx[0] + 1, b[0]) if (d, t) not in busy]
            print(f'q{q}: CX t{cx[0]} with q{d}, {a[1]} t{a[0]}, {b[1]} t{b[0]}, partner idle at {free}')
