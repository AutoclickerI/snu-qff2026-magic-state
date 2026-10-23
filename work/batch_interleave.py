"""Official-setting scores for the interleaved final-cycle orderings from cycle_search2.py."""
import json
import pickle
import sys
import time

import batch_score as bs

if __name__ == "__main__":
    pkl = sys.argv[1]
    lmax = int(sys.argv[2])
    shots = int(float(sys.argv[3])) if len(sys.argv) > 3 else 10**8
    n = len(pickle.load(open(pkl, "rb")))
    items = [(f"{pkl}#{i}", {"kind": "interleave", "pkl": pkl, "idx": i, "lmax": lmax, "lazy": True}, shots)
             for i in range(n)]
    res = bs.run(items, procs=60)
    json.dump(res, open(f"batch_il_{int(time.time())}.json", "w"), indent=1)
