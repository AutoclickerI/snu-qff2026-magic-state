"""Seeds 1000 and 2000 (1e8 each) for alapvar hashes; prints seed-0 (stored), the two others and the 3-seed mean.
Usage: python mseed.py <hash>... ; results appended to mseed.jsonl"""
import json, os, sys
sys.path.insert(0, "/home/jihoon/competitions/quantumn/work")
import fast_check
for h in sys.argv[1:]:
    d = json.load(open(f"alapvar/{h}.json")); text = open(f"alapvar/{h}.qasm").read()
    s = [d["score"]] + [fast_check.check(text, d["data_qubits"], shots=10**8, seed=k, procs=int(os.environ.get("PROCS", 20))).score
                        for k in (1000, 2000)]
    rec = {"hash": h, "s0": s[0], "s1000": s[1], "s2000": s[2], "mean": sum(s) / 3, "n_2q": d["n_2q"],
           "src": d.get("src"), "label": d.get("label"), "seed": d.get("seed"), "commute": d.get("commute")}
    open("mseed.jsonl", "a").write(json.dumps(rec) + "\n")
    print(f"{h} {d.get('label','')} 2q {d['n_2q']} s0 {s[0]:.4e} s1000 {s[1]:.4e} s2000 {s[2]:.4e} mean {rec['mean']:.4e}", flush=True)
