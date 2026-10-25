import sys
from gadgets import *
c = read(sys.argv[1])
st = status(c)
T = depth(c)
D = c['meta']['data_qubits']
lo = int(sys.argv[2]) if len(sys.argv) > 2 else 28
for q in sorted(set(D) | {4, 8, 9, 15, 16}):
    row = []
    for t in range(lo, T):
        ops = ops_at(c, q, t)
        if ops:
            row.append(f"{t}:{' '.join(ops[0]['lines'])[:22]}")
        else:
            row.append(f"{t}:{st[q][t]}")
    print(f'q{q}', ' | '.join(row))
