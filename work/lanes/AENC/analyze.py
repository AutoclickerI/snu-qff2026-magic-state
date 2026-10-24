"""Class costs from the in-situ table and the exact score of encoder specs.

kappa(c) = (N_c - L0 A_c) / A_0: first-order marginal loss per unit probability of a region fault of class c
(L0 = N_0 / A_0, the loss with a perfect A region). Exact score of a spec: loss = sum P~ N / sum P~ A.
"""
import sys, json
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from bmodel import rep, flag_bit, cls
import enc


class Table:
    def __init__(self, path):
        t = json.loads(Path(path).read_text())['table']
        self.A = np.array([t[str(c)]['A'] for c in range(128)])
        self.O = np.array([t[str(c)]['O'] for c in range(128)])
        self.N = (self.A - self.O) / 2
        self.L0 = self.N[0] / self.A[0]
        self.kappa = (self.N - self.L0 * self.A) / self.A[0]
        self.alpha = self.A / self.A[0] - 1          # first-order relative acceptance change per unit prob

    def exact(self, spec):
        Pt = enc.ptilde(spec)
        A = float(Pt @ self.A)
        return float(Pt @ self.N) / A, A

    def describe(self, c):
        sx, sz, l = c & 7, (c >> 3) & 7, c >> 6
        ex, ez = rep(c)
        if sx:
            kind = f'X syn{sx}'
        else:
            kind = ''
        if sz == 0 and l == 0:
            zk = ''
        elif sz == 0:
            zk = 'Z_L'
        else:
            w1 = (sum((ez >> i) & 1 for i in range(7)) == 1)
            zk = f'Z{sz - 1}' if w1 else f'Z_L.Z{sz - 1}'
        return (kind + (' + ' if kind and zk else '') + zk) or 'I', flag_bit(c)

    def breakdown(self, spec, top=40):
        rows = []
        for g, pr, pauli, t in enc.first_order(spec):
            if g >> 7: continue                  # caught by an in-region check
            c = g & 127
            rows.append((pr * self.kappa[c], pr, c, pauli, t))
        rows.sort(key=lambda r: -abs(r[0]))
        return rows[:top], sum(r[0] for r in rows)


if __name__ == '__main__':
    T = Table(sys.argv[1])
    print(f'L0 (perfect region) {T.L0:.6e}  A0 {T.A[0]:.6f}')
    order = np.argsort(-T.kappa)
    print('class  kappa        alpha      desc  flag')
    for c in order:
        d, fl = T.describe(int(c))
        print(f'{c:4d} {T.kappa[c]:+.4e} {T.alpha[c]:+.4f}  {d:22s} {fl}')
    L, Aacc = T.exact(enc.V36C)
    print('v36c encoder exact', L, Aacc)
    rows, tot = T.breakdown(enc.V36C)
    print('first-order region cost', tot, ' exact - L0', L - T.L0)
    for r in rows:
        print(f'{r[0]:+.3e} p={r[1]:.2e} class {r[2]:3d} {T.describe(r[2])[0]:20s} {r[3]} t={r[4]}')
