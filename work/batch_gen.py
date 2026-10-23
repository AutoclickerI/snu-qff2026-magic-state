"""Official-setting scores for gen_cycle results: python batch_gen.py <gen json> [n] [shots]."""
import json
import sys
import time

import batch_score as bs

if __name__ == "__main__":
    f = sys.argv[1]
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    shots = int(float(sys.argv[3])) if len(sys.argv) > 3 else 10**8
    res = json.load(open(f))
    seen, items = set(), []
    for i, r in enumerate(res):
        if r[0] in seen:
            continue
        seen.add(r[0])
        items.append((f"{f}#{i} proxy {r[0]:.4g}", {"kind": "gen2" if f.startswith("gen2_") else "gen", "file": f, "idx": i, "lazy": True}, shots))
        if len(items) >= n:
            break
    out = bs.run(items, procs=len(items))
    json.dump(out, open(f"batch_gen_{int(time.time())}.json", "w"), indent=1)
