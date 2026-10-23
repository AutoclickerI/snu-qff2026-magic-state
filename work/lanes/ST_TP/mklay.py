"""python mklay.py <results.json> <idx> <out.json>: code-ordered layout (d'_i ~ o_i ~ b_i ~ c'_i), placement map,
data move paths, spare cells."""
import json
import sys
from collections import deque

import layout5 as L

res = [r for r in json.load(open(sys.argv[1])) if r["idx"] == int(sys.argv[2])][0]
f = L.SYMS[res["pl"]["sym"]]
dr, dc = res["pl"]["dr"], res["pl"]["dc"]
M = {}
for q in L.D0 + L.ANC0:
    r, c = f(*divmod(q, 6))
    M[q] = (r + dr) * 6 + c + dc
s1, s3 = res["s1"], res["s3"]
d0, dfin = res["d0"], res["d"]
assert [M[q] for q in L.D0] == d0
blocked = set(d0)
moves = []
for j in range(7):
    if d0[j] == dfin[j]:
        continue
    prev = {d0[j]: None}
    dq = deque([d0[j]])
    while dq:
        u = dq.popleft()
        for v in L.nbrs(u):
            if v not in prev and v not in blocked:
                prev[v] = u
                dq.append(v)
    path, u = [], dfin[j]
    while u is not None:
        path.append(u)
        u = prev[u]
    moves.append(path[::-1])
d = [dfin[s1[i]] for i in range(7)]
c = [res["c"][s3[i]] for i in range(7)]
for i in range(7):
    assert res["o"][i] in L.nbrs(d[i]) and res["b"][i] in L.nbrs(res["o"][i]) and c[i] in L.nbrs(res["b"][i])
used = set(d) | set(res["o"]) | set(res["b"]) | set(c)
spare = [q for q in range(36) if q not in used and q not in d0]
json.dump({"d": d, "o": res["o"], "b": res["b"], "c": c, "map": M, "spare": spare, "s": res["s"], "T": res["T"],
           "moves": moves, "o_stage": res["o_stage"], "o_help": res["o_help"], "bc_help": res["b_help"],
           "d0": d0}, open(sys.argv[3], "w"))
print(sys.argv[3], "T", res["T"], "moves", moves, "o", res["o"], "stage", res["o_stage"], "ohelp", res["o_help"],
      "b", res["b"], "c", c, "bchelp", res["b_help"], "spare", spare)
