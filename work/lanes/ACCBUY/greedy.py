"""Greedy rounds over the pre-role (prerole2) and known-state (kstate) slot menus.
usage: greedy.py <base name in c/> <rounds> [accfloor]
Each round: regenerate menus on the base, evaluate all, add improving candidates in gain order (each joint re-evaluated,
kept only if it improves and acceptance >= floor)."""
import sys, subprocess, json, os
from concurrent.futures import ThreadPoolExecutor
H = os.path.dirname(os.path.abspath(__file__))
PY = '/home/jihoon/competitions/quantumn/.venv/bin/python'
def ev(name, procs=7):
    out = subprocess.run([f'{H}/ev.sh', f'{H}/c/{name}', str(procs)], capture_output=True, text=True).stdout.split()
    try:
        return float(out[1]), float(out[2])
    except Exception:
        return None
def menus(base, tag):
    names = []
    for script, pre in (('prerole2.py', f'{tag}p'), ('kstate.py', f'{tag}k')):
        subprocess.run([PY, f'{H}/{script}', f'{H}/c/{base}', pre], capture_output=True, text=True, cwd=H)
        names += open(f'{H}/c/{pre}.list').read().split()
    return names
base = sys.argv[1]; rounds = int(sys.argv[2]); floor = float(sys.argv[3]) if len(sys.argv) > 3 else 0.5005
L, A = ev(base, 16)
print('base', base, L, A, flush=True)
for r in range(rounds):
    tag = f'{base}r{r}'
    names = menus(base, tag)
    with ThreadPoolExecutor(3) as ex:
        res = dict(zip(names, ex.map(ev, names)))
    good = sorted([(v[0] - L, n, v[1]) for n, v in res.items() if v and v[0] < L - 2e-9], key=lambda x: x[0])
    print('round', r, len(names), 'candidates', len(good), 'improving', [(n, f'{d:.2e}', a) for d, n, a in good[:8]], flush=True)
    if not good:
        break
    cur, curL, curA, used = base, L, A, []
    for d, n, a in good:
        trial = f'{tag}_j{len(used) + 1}'
        p = subprocess.run([PY, f'{H}/jslot.py', f'{H}/c/{base}', trial] + used + [n], capture_output=True, text=True, cwd=H)
        if p.returncode:
            continue
        v = ev(trial, 16)
        if v and v[0] < curL - 1e-9 and v[1] >= floor:
            cur, curL, curA = trial, v[0], v[1]; used.append(n)
            print('  add', n, curL, curA, flush=True)
    if cur == base:
        break
    base, L, A = cur, curL, curA
    print('new base', base, L, A, flush=True)
print('final', base, L, A)
