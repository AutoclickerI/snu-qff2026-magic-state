"""X projections of prep faults; four-bit signature = syndrome | parity<<3."""
import itertools
import json
import sys
B = [6, 26, 13, 11, 4, 23, 27]
C = [12, 25, 19, 17, 5, 29, 28]
ROWS = [[0, 2, 4, 6], [1, 2, 5, 6], [3, 4, 5, 6]]
READ_FLIPS = {8 | (i + 1) for i in range(7)}
def sig(e, block):
    return sum((sum(block[i] in e for i in row) % 2) << j for j, row in enumerate(ROWS)) | ((sum(q in e for q in block) % 2) << 3)
def dangerous(s):
    return bool(s & 8) == (not bool(s & 7))
def violates(e, rule):
    sb, sc = sig(e, B), sig(e, C)
    diff = sb ^ sc
    if rule == "clean_literal": return diff == 0 and bool(set(B) & e)
    if rule == "clean": return diff == 0 and sb != 0
    if rule == "robust": return dangerous(sb) and diff in ({0} | READ_FLIPS)
    if rule in ("base", "pairs"): return dangerous(sb) and diff == 0
    raise ValueError(rule)
def sources(d, cells):
    # XX after an actual CX is a SINGLE physical depolarizing fault.
    return [(t, (q,)) for t in range(len(d["ops"]) + 1) for q in cells] + [(t + 1, tuple(e)) for t, layer in enumerate(d["ops"]) for e in layer]
def propagate(ops, source):
    t, qs = source
    e = set(qs)
    for layer in ops[t:]:
        for u, v in layer:
            if u in e: e.symmetric_difference_update([v])
    return e
def faults(d, cells=None, rule="base", limit=None):
    cells = cells or sorted(set(B + C + d["pivots"]) | {q for layer in d["ops"] for e in layer for q in e})
    ss = sources(d, cells)
    errors = [propagate(d["ops"], s) for s in ss]
    out = []
    single_rule = "robust" if rule == "pairs" else rule
    for s, e in zip(ss, errors):
        if violates(e, single_rule):
            out.append((s,))
            if limit and len(out) >= limit: return out
    if rule == "pairs":
        for i, j in itertools.combinations(range(len(ss)), 2):
            if ss[i][0] == ss[j][0] and set(ss[i][1]) & set(ss[j][1]): continue
            if violates(errors[i] ^ errors[j], "base"):
                out.append((ss[i], ss[j]))
                if limit and len(out) >= limit: return out
    return out
if __name__ == "__main__":
    d = json.load(open(sys.argv[1]))
    for rule in ("base", "clean_literal", "clean", "robust", "pairs"):
        f = faults(d, rule=rule)
        print(rule, len(f), "violations", f[:3])
