"""Joint builders on a base plan from priced singles (all orders, priced whole).

greedy.py prefix <base> <tag> <floor> [maxn]   prefixes of the gain-ranked menu (invalid ones skipped), all priced in parallel
greedy.py step <base> <tag> <floor> [K] [maxsteps]   true greedy: each step prices base+single for the K best valid singles in
                                     parallel and keeps the best gain with acceptance >= floor; stops when nothing gains
greedy.py loo <joint> <tag>           leave-one-out of the joint's applied specs (each removed, rest re-composed on its base)
Menu: every priced c/<menu_base>__S_* (singles.py) and __L_* (loo_build.py) of MENU_BASE (default i2_v36f): gain and acceptance
delta vs MENU_BASE. Results in res/, plans in c/, logs on stdout; joints record their spec list in json 'joint'.
"""
import os
from moves import *
import ev2

PROCS = int(os.environ.get('PROCS', '20'))
MB = os.environ.get('MENU_BASE', 'i2_v36f')
MINGAIN = float(os.environ.get('MINGAIN', '1e-10'))


def price(n):
    p = H / 'res' / (n + '.json')
    if not p.exists():
        return None
    r = json.loads(p.read_text())
    return r if 'loss' in r else None


def menu():
    b = price(MB)
    rows = []
    sp = json.loads((H / f'singles_{MB}.json').read_text())
    lo = json.loads((H / f'loo_{MB}.json').read_text()) if (H / f'loo_{MB}.json').exists() else {}
    for n, s in list(sp.items()) + list(lo.items()):
        r = price(n)
        if r is None:
            continue
        rows.append(dict(n=n, spec=s, gain=b['loss'] - r['loss'], dacc=r['acceptance'] - b['acceptance']))
    return rows


def compose(c, specs):
    used = []
    for s in specs:
        try:
            c = apply_spec(c, s)
            used.append(s)
        except Invalid:
            pass
    return c, used


def save_joint(c, name, base, specs):
    save(c, name, dict(kind='joint', base=base, joint=specs))
    return name


def run_prices(names):
    out = {}
    todo = [n for n in names if price(n) is None]
    if todo:
        for r in ev2.price([str(C / n) for n in todo], PROCS):
            pass
    for n in names:
        out[n] = price(n)
    return out


def ranked(rows, floor_gain=MINGAIN):
    rows = [r for r in rows if r['gain'] > floor_gain]
    rows.sort(key=lambda r: -r['gain'])
    return rows


if __name__ == '__main__':
    mode, base, tag = sys.argv[1], sys.argv[2], sys.argv[3]
    c0 = load_plan(base) if (C / (base + '.plan.json')).exists() else read(C / base)
    b0 = price(base)
    if mode == 'prefix':
        floor = float(sys.argv[4]); maxn = int(sys.argv[5]) if len(sys.argv) > 5 else 40
        rows = ranked(menu())
        c, used, names = c0, [], []
        for r in rows:
            try:
                c2 = apply_spec(c, r['spec'])
            except Invalid:
                continue
            c = c2; used.append(r)
            n = save_joint(c, f'{tag}_p{len(used)}', base, [u['spec'] for u in used])
            names.append(n)
            if len(used) >= maxn:
                break
        res = run_prices(names)
        for k, n in enumerate(names):
            r = res[n]
            u = used[k]
            print(f"{n} +{u['n'].split('__', 1)[1]} single {-u['gain']:+.3e} -> loss {r['loss']!r} ({r['loss'] - b0['loss']:+.4e}) acc {r['acceptance']:.5f}",
                  flush=True)
    elif mode == 'step':
        floor = float(sys.argv[4]); K = int(sys.argv[5]) if len(sys.argv) > 5 else PROCS
        maxsteps = int(sys.argv[6]) if len(sys.argv) > 6 else 60
        rows = ranked(menu())
        cur, curn, cur_r, used = c0, base, b0, []
        dead = set()
        for step in range(maxsteps):
            cands = []
            for r in rows:
                if r['n'] in dead or any(u is r for u in used):
                    continue
                try:
                    c2 = apply_spec(cur, r['spec'])
                except Invalid:
                    dead.add(r['n']); continue
                n = f"{tag}_s{step}_{len(cands)}"
                save_joint(c2, n, base, [u['spec'] for u in used] + [r['spec']])
                cands.append((n, r, c2))
                if len(cands) >= K:
                    break
            if not cands:
                break
            res = run_prices([n for n, _, _ in cands])
            best = None
            for n, r, c2 in cands:
                p = res[n]
                if p is None:
                    dead.add(r['n']); continue
                g = cur_r['loss'] - p['loss']
                print(f"  step {step} {r['n'].split('__', 1)[1]} single {-r['gain']:+.3e} joint {-g:+.3e} acc {p['acceptance']:.5f}", flush=True)
                if g <= 0:
                    dead.add(r['n'])
                if p['acceptance'] >= floor and g > 0 and (best is None or g > best[0]):
                    best = (g, n, r, c2, p)
            if best is None:
                break
            g, n, r, c2, p = best
            cur, curn, cur_r = c2, n, p
            used.append(r)
            print(f"STEP {step}: + {r['n'].split('__', 1)[1]} gain {g:.3e} -> {n} loss {p['loss']!r} acc {p['acceptance']:.5f}", flush=True)
        print('FINAL', curn, cur_r['loss'], cur_r['acceptance'])
    elif mode == 'loo':
        meta = json.loads((C / (base + '.json')).read_text())
        jb, specs = meta['integ']['base'], meta['integ']['joint']
        cb = load_plan(jb) if (C / (jb + '.plan.json')).exists() else read(C / jb)
        names, drops = [], []
        for k in range(len(specs)):
            c, used = compose(cb, [s for i, s in enumerate(specs) if i != k])
            if len(used) != len(specs) - 1:
                print('skip', k); continue
            n = save_joint(c, f'{tag}_loo{k}', jb, used)
            names.append(n); drops.append(specs[k])
        res = run_prices(names)
        for n, s in zip(names, drops):
            r = res[n]
            d = {kk: s[kk] for kk in s if kk not in ('edits',)}
            print(f"{n} drop {json.dumps(d)[:150]} -> {r['loss'] - b0['loss']:+.4e} acc {r['acceptance'] - b0['acceptance']:+.5f}", flush=True)
