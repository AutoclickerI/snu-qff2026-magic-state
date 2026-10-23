"""Official-metric screen of every distinct full circuit in run_moves result files.
Usage: python screen.py <out.jsonl> <res json>... ; skips circuits already in out.jsonl (by text hash)."""
import hashlib
import json
import os
import sys

sys.path.insert(0, ".")
sys.path.insert(0, "/home/jihoon/competitions/quantumn/work")
import tprep  # noqa: E402
import fast_check  # noqa: E402
import run_moves as R  # noqa: E402
from verify import load_assign  # noqa: E402

PROCS = int(os.environ.get("PROCS", 24))

if __name__ == "__main__":
    out = sys.argv[1]
    done = set()
    if os.path.exists(out):
        done = {json.loads(l)["hash"] for l in open(out)}
    for f in sys.argv[2:]:
        for i, (cost, a, o, seed, name) in enumerate(json.load(open(f))):
            m = R.variant(name)
            c, data = m.full_circuit(load_assign(a), o)
            text = c.text()
            h = hashlib.sha1(text.encode()).hexdigest()[:12]
            if h in done:
                continue
            done.add(h)
            rep = fast_check.check(text, data, shots=10**8, procs=PROCS)
            c1 = tprep.fault_scan(text, data).c1 if rep.passed else None
            os.makedirs("screened", exist_ok=True)
            open(f"screened/{h}.qasm", "w").write(text)
            rec = {"hash": h, "src": f"{f}#{i}", "proxy": cost, "score": rep.score, "sem": rep.sem,
                   "acc": rep.acceptance, "n_2q": rep.n_2q, "passed": rep.passed, "c1": c1, "data": data}
            open(out, "a").write(json.dumps(rec) + "\n")
            print(f"{h} {f}#{i} proxy {cost:.4e} 1-F {rep.score:.5e} acc {rep.acceptance:.4f} 2q {rep.n_2q} "
                  f"pass {rep.passed} c1 {c1}", flush=True)
