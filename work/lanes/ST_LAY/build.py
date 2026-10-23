import json, glob, collections
from lay3 import nbrs, PRE
BZ = {0,1,2,3,4,6,7,8,9,10,13,14,15,19,20}
def mk(d):
    P = d["paths"]; lab = d["lab"]
    lay = {"a": [p[0] for p in P], "d": [p[1] for p in P], "b": [p[2] for p in P], "c": [p[3] for p in P]}
    for k in "ABC": lay["h"+k] = sorted(int(q) for q, l in lab.items() if l == k)
    # moves
    blocked = set(lay["a"]+lay["b"]+lay["c"])
    moves = []
    for i in range(7):
        src, dst = PRE[i], lay["d"][i]
        other = set(lay["d"]) - {dst}
        prev = {src: None}; dq = collections.deque([src])
        while dq:
            u = dq.popleft()
            for v in nbrs(u):
                if v in prev or v in blocked: continue
                prev[v] = u; dq.append(v)
        if dst not in prev: moves.append(None); continue
        p = [dst]
        while prev[p[-1]] is not None: p.append(prev[p[-1]])
        moves.append(p[::-1])
    lay["moves"] = moves
    lay["hops"] = sum(len(m)-1 for m in moves if m)
    regions = {k: set(lay[r]) | set(lay["h"+k.upper()]) for k, r in (("a","a"),("b","b"),("c","c"))}
    lay["busy_regions"] = [k for k, s in regions.items() if s & BZ]
    lay["prefix_map"] = None
    return lay
if __name__ == "__main__":
    res = sorted((json.load(open(f))["cost"], f) for f in glob.glob("sa_*.json"))
    seen = set(); out = []
    for c, f in res:
        d = json.load(open(f)); key = json.dumps(d["paths"])
        if key in seen: continue
        seen.add(key); l = mk(d); l["src"] = f; out.append(l)
        if len(out) >= 8: break
    for i, l in enumerate(out):
        json.dump(l, open(f"cand_{i}.json", "w"))
        print(i, l["src"], "hops", l["hops"], l["busy_regions"], l["moves"])
