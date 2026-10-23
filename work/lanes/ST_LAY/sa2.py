"""SA over staging layouts. python sa2.py seed secs [wbusy] [pre json]"""
import random, math, sys, json, time
from lay3 import nbrs, PRE
NB = [nbrs(q) for q in range(36)]
CN = [[q]+NB[q] for q in range(36)]
F = set([5,11,12,16,17,18] + list(range(21,36)))
man = lambda a,b: abs(a//6-b//6)+abs(a%6-b%6)
def comps(S):
    S = set(S); n = 0
    while S:
        n += 1; st = [S.pop()]
        while st:
            u = st.pop()
            for v in NB[u]:
                if v in S: S.discard(v); st.append(v)
    return n
def evaluate(s, p, d, pre, wb):
    # s[X][i], p[X][i] (X=0,1,2 -> a,b,c), d[i]
    viol = 0
    for X in range(3): viol += comps(s[X]) - 1
    from collections import Counter
    sc = Counter(q for X in range(3) for q in s[X])
    viol += sum(v - 1 for v in sc.values())
    rc = Counter([p[X][i] for X in range(3) for i in range(7)] + list(d))
    viol += sum(v - 1 for v in rc.values())
    sset = set(sc)
    viol += sum(1 for X in range(3) for i in range(7) if p[X][i] != s[X][i] and p[X][i] in sset)
    for i in range(7):
        viol += max(0, man(d[i], p[0][i]) - 1) + max(0, man(d[i], p[1][i]) - 1) + max(0, man(p[1][i], p[2][i]) - 1)
    dist = [man(d[i], pre[i]) for i in range(7)]
    busy = sum(1 for X in range(3) for q in s[X] if q not in F)
    hops = sum(1 for X in range(3) for i in range(7) if p[X][i] != s[X][i])
    cost = 10 * viol + 1.0 * sum(dist) + 2.0 * max(dist) + 0.3 * hops + wb * busy
    return cost, viol, sum(dist), max(dist), busy, hops
def run(seed, secs, wb, pre):
    rng = random.Random(seed)
    cells = list(range(36))
    perm = rng.sample(cells, 21)
    s = [perm[0:7], perm[7:14], perm[14:21]]
    p = [[rng.choice(CN[q]) for q in s[X]] for X in range(3)]
    d = [rng.choice(cells) for _ in range(7)]
    cur = evaluate(s, p, d, pre, wb); best = None; t0 = time.time(); it = 0
    while time.time() - t0 < secs:
        it += 1; T = 4.0 * (1 - (time.time() - t0) / secs) + 0.05
        s2 = [list(r) for r in s]; p2 = [list(r) for r in p]; d2 = list(d)
        mv = rng.random(); X = rng.randrange(3); i = rng.randrange(7)
        if mv < 0.25: s2[X][i] = rng.choice(cells); p2[X][i] = rng.choice(CN[s2[X][i]])
        elif mv < 0.4: s2[X][i] = rng.choice(NB[s2[X][i]]); p2[X][i] = rng.choice(CN[s2[X][i]])
        elif mv < 0.6: p2[X][i] = rng.choice(CN[s2[X][i]])
        elif mv < 0.75: d2[i] = rng.choice(cells)
        elif mv < 0.88: d2[i] = rng.choice(NB[d2[i]])
        elif mv < 0.94:  # swap roles of two code indices within a block
            j = rng.randrange(7); s2[X][i], s2[X][j] = s2[X][j], s2[X][i]; p2[X][i], p2[X][j] = p2[X][j], p2[X][i]
        else:  # move whole code index i of all arrays
            j = rng.randrange(7)
            for Y in range(3): s2[Y][i], s2[Y][j] = s2[Y][j], s2[Y][i]; p2[Y][i], p2[Y][j] = p2[Y][j], p2[Y][i]
            d2[i], d2[j] = d2[j], d2[i]
        c = evaluate(s2, p2, d2, pre, wb)
        if c[0] <= cur[0] or rng.random() < math.exp((cur[0] - c[0]) / T):
            s, p, d, cur = s2, p2, d2, c
            if cur[1] == 0 and (best is None or cur[0] < best[0][0]):
                best = (cur, [list(r) for r in s], [list(r) for r in p], list(d))
    return best, cur, it
if __name__ == "__main__":
    seed = int(sys.argv[1]); secs = float(sys.argv[2]); wb = float(sys.argv[3]) if len(sys.argv) > 3 else 3
    pre = json.loads(sys.argv[4]) if len(sys.argv) > 4 else PRE
    b, cur, it = run(seed, secs, wb, pre)
    print(seed, cur, it, b and b[0], flush=True)
    if b:
        c, s, p, d = b
        json.dump({"seed": seed, "pre": pre, "score": c, "a": p[0], "b": p[1], "c": p[2], "d": d,
                   "stage": {"a": s[0], "b": s[1], "c": s[2]}, "helpers": {"a": [], "b": [], "c": []}},
                  open(f"sb_{seed}.json", "w"))
