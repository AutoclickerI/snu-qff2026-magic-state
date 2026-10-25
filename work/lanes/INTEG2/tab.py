"""Table of priced stems vs a base: tab.py <base> <list file or names...> [--all]"""
import sys, json
from pathlib import Path
H = Path(__file__).resolve().parent


def res(n):
    p = H / 'res' / (n + '.json')
    return json.loads(p.read_text()) if p.exists() else None


def table(base, names):
    b = res(base)
    rows = []
    for n in names:
        r = res(n)
        if r is None:
            rows.append((n, None, None, 'pending')); continue
        if 'error' in r:
            rows.append((n, None, None, r['error'][:90])); continue
        rows.append((n, r['loss'] - b['loss'], r['acceptance'] - b['acceptance'], ''))
    return b, rows


if __name__ == '__main__':
    base = sys.argv[1]
    a = [x for x in sys.argv[2:] if x != '--all']
    names = []
    for x in a:
        names += (H / x).read_text().split() if (H / x).exists() else [x]
    b, rows = table(base, names)
    print(f"base {base} loss {b['loss']!r} acc {b['acceptance']:.6f}")
    ok = sorted([r for r in rows if r[1] is not None], key=lambda r: r[1])
    for n, dl, da, _ in ok:
        print(f"{dl:+.4e} {da:+.5f}  {n.split('__', 1)[-1]}")
    for n, _, _, e in rows:
        if e:
            print('   ', e, n.split('__', 1)[-1])
