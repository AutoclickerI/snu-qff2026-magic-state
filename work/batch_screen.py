"""Score a list of [gen2 json, index] at the official setting: python batch_screen.py list.json [shots]."""
import json
import sys
import time

import batch_score as bs

if __name__ == "__main__":
    lst = json.load(open(sys.argv[1]))
    shots = int(float(sys.argv[2])) if len(sys.argv) > 2 else 10**8
    done = set()
    import glob
    for f in glob.glob("batch_gen_*.json") + glob.glob("batch_scr_*.json"):
        for r in json.load(open(f)):
            done.add((r["spec"].get("file"), r["spec"].get("idx")))
    items = [(f"{f}#{i}", {"kind": "gen2" if f.startswith("gen2_") else "gen", "file": f, "idx": i, "lazy": True}, shots)
             for f, i in lst if (f, i) not in done]
    print(len(items), "to score", flush=True)
    out = bs.run(items, procs=min(len(items), 32))
    json.dump(out, open(f"batch_scr_{int(time.time())}.json", "w"), indent=1)
