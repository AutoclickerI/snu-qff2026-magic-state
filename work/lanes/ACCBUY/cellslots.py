import sys
from gadgets import *
c = read(sys.argv[1])
st = status(c)
T = depth(c)
lo, hi = int(sys.argv[2]), int(sys.argv[3])
qs = [int(x) for x in sys.argv[4].split(',')]
for q in qs:
    row = []
    for t in range(lo, min(hi, T - 1) + 1):
        ops = ops_at(c, q, t)
        if ops:
            l = ' '.join(ops[0]['lines'])
            l = l.replace('measure', 'M').replace('reset', 'R').replace(' -> ', '>').replace('cx ', '').replace('q[', '').replace(']', '').replace(';', '')
            row.append(f"{t}:{l[:14]}")
        else:
            row.append(f"{t}:{st[q][t][:4]}")
    print(f'q{q:<2}', ' '.join(f'{x:<17}' for x in row))
