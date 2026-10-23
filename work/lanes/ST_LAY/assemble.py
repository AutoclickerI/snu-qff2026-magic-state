import json, sys, collections
from lay3 import nbrs, PRE
def moves_for(lay, pre=PRE):
    bc = set()
    for k in "abc": bc |= set(lay["stage"][k]) | set(lay["helpers"][k]) | set(lay[k])
    out = []
    for i in range(7):
        src, dst = pre[i], lay["d"][i]
        prev = {src: None}; dq = collections.deque([src])
        while dq:
            u = dq.popleft()
            for v in nbrs(u):
                if v in prev or (v in bc and v != dst) or (v in pre and v != dst): continue
                prev[v] = u; dq.append(v)
        if dst not in prev:   # allow through block cells
            prev = {src: None}; dq = collections.deque([src])
            while dq:
                u = dq.popleft()
                for v in nbrs(u):
                    if v not in prev: prev[v] = u; dq.append(v)
        p = [dst]
        while prev[p[-1]] is not None: p.append(prev[p[-1]])
        out.append(p[::-1])
    return out
if __name__ == "__main__":
    lay = json.load(open(sys.argv[1])); lay["moves"] = moves_for(lay)
    lay["preps"] = {k: {"ops": json.load(open(f))["ops"], "pivots": json.load(open(f))["pivots"]} for k, f in zip("abc", sys.argv[3:6])}
    json.dump(lay, open(sys.argv[2], "w")); print(lay["moves"])
