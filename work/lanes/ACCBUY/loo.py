"""Leave-one-out of added CX slots in a final plan relative to its own builds: rebuild from v36g with all but one.
usage: loo.py <out prefix> spec ... where spec = h:q:t[:rt] (prerole, kind from init) or name of a saved slot candidate."""
import sys, json, subprocess
H = '/home/jihoon/competitions/quantumn/work/lanes/ACCBUY'
PY = '/home/jihoon/competitions/quantumn/.venv/bin/python'
G = '/home/jihoon/competitions/quantumn/work/lanes/MAIN/v36g'
pre = [s for s in sys.argv[2:] if ':' in s]
slots = [s for s in sys.argv[2:] if ':' not in s]
for i, s in enumerate(pre + slots):
    p2 = [x for x in pre if x != s]; s2 = [x for x in slots if x != s]
    n = f'{sys.argv[1]}_{i}'
    subprocess.run([PY, f'{H}/prj.py', G, n + 'a'] + p2, cwd=H, capture_output=True)
    r = subprocess.run([PY, f'{H}/jslot.py', f'{H}/c/{n}a', n] + s2, cwd=H, capture_output=True, text=True)
    print(n, 'without', s, r.stdout.strip().split('/')[-1], flush=True)
