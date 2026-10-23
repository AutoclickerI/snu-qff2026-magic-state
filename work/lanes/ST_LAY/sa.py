import random, math, sys, json, time
from lay3 import nbrs, PRE
import os
IGN = [int(c) for c in os.environ.get("IGN", "")]
BZ = {0,1,2,3,4,6,7,8,9,10,13,14,15,19,20}
WB = float(os.environ.get('WB', '3'))
NB = [nbrs(q) for q in range(36)]
def comps(S):
    S = set(S)
    if not S: return 0
    n = 0
    while S:
        n += 1; st = [S.pop()]
        while st:
            u = st.pop()
            for v in NB[u]:
                if v in S: S.discard(v); st.append(v)
    return n
def rand_walk(free, rng):
    s = rng.choice(free); w = [s]
    for _ in range(3):
        c = [v for v in NB[w[-1]] if v in free_set and v not in w]
        if not c: return None
        w.append(rng.choice(c))
    return w
def unreach(paths):
    bl = set(p[k] for p in paths for k in (0, 2, 3)); ds = [p[1] for p in paths]
    n = 0
    for i, p in enumerate(paths):
        src, dst = PRE[i], p[1]; seen = {src}; fr = [src]
        while fr and dst not in seen:
            fr = [v for u in fr for v in NB[u] if v not in seen and v not in bl and not seen.add(v)]
        n += dst not in seen
    return n
def run(seed, secs, pre, wd=0.3):
    global free_set
    rng = random.Random(seed)
    # init: random placement
    while True:
        paths = []; used = set(); ok = True
        for i in range(7):
            for _ in range(200):
                free_set = set(range(36)) - used
                w = rand_walk(list(free_set), rng)
                if w: break
            else: ok = False; break
            paths.append(w); used |= set(w)
        if ok: break
    lab = {q: rng.choice("ABCN") for q in range(36) if q not in used or q in [p[1] for p in paths]}
    def cost(paths, lab):
        a = [set() for _ in range(3)]
        for p in paths:
            a[0].add(p[0]); a[1].add(p[2]); a[2].add(p[3])
        for q, l in lab.items():
            if l != "N": a["ABC".index(l)].add(q)
        for p in paths:
            l = lab.get(p[1], "N")
            if l != "N": a["ABC".index(l)].add(p[1])
        pen = sum(comps(s) - 1 for k, s in enumerate(a) if k not in IGN)
        dist = sum(abs(p[1]//6 - pre[i]//6) + abs(p[1]%6 - pre[i]%6) for i, p in enumerate(paths))
        busy = sum(1 for s_ in a if s_ & BZ)
        if True:
            bl = set(p[k] for p in paths for k in (0, 2, 3)); ds = [p[1] for p in paths]
            dist = 0
            for i, p in enumerate(paths):
                src, dst = pre[i], p[1]; seen = {src: 0}; fr = [src]
                while fr and dst not in seen:
                    nf = []
                    for u in fr:
                        for v in NB[u]:
                            if v not in seen and v not in bl and True:
                                seen[v] = seen[u] + 1; nf.append(v)
                    fr = nf
                dist += seen.get(dst, 12)
        return pen * 10 + wd * dist + WB * busy, pen, dist, busy
    cur = cost(paths, lab); best = None; T0 = 3.0; t0 = time.time(); it = 0
    while time.time() - t0 < secs:
        it += 1
        T = T0 * (1 - (time.time() - t0) / secs) + 0.05
        mv = rng.random(); np_, nl = paths, lab
        if mv < 0.35:
            np_ = list(paths); i = rng.randrange(7)
            used = set(q for j, p in enumerate(paths) if j != i for q in p)
            free_set = set(range(36)) - used
            w = rand_walk(list(free_set), rng)
            if not w: continue
            nl = None
            np_[i] = w
            keep = (free_set - set(w)) | {p[1] for p in np_}
            nl = {q: lab.get(q, rng.choice("ABCN")) for q in keep}
        elif mv < 0.45:
            np_ = list(paths); i, j = rng.sample(range(7), 2); np_[i], np_[j] = paths[j], paths[i]
        else:
            nl = dict(lab); q = rng.choice(list(lab)); nl[q] = rng.choice("ABCN")
        c = cost(np_, nl)
        if c[0] <= cur[0] or rng.random() < math.exp((cur[0] - c[0]) / T):
            paths, lab, cur = np_, nl, c
            if cur[1] == 0 and cur[2] < 12 * 0 + 1000 and unreach(paths) == 0 and (best is None or cur[0] < best[0]):
                best = (cur[0], [list(p) for p in paths], dict(lab))
    return best, cur, it
if __name__ == "__main__":
    seed = int(sys.argv[1]); secs = float(sys.argv[2])
    pre = json.loads(sys.argv[3]) if len(sys.argv) > 3 else PRE
    b, cur, it = run(seed, secs, pre)
    print(seed, cur, it, b and b[0], flush=True)
    if b: json.dump({"seed": seed, "pre": pre, "cost": b[0], "paths": b[1], "lab": {str(k): v for k, v in b[2].items()}}, open(f"sa_{seed}.json", "w"))
