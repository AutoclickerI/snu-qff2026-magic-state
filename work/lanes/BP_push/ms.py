"""Seeds 1000, 2000 for hashes in a dir. Usage: ms.py <dir> <hash>..."""
import json, os, sys
sys.path.insert(0, "/home/jihoon/competitions/quantumn/work")
import fast_check
d0 = sys.argv[1]
for h in sys.argv[2:]:
    d = json.load(open(f"{d0}/{h}.json")); text = open(f"{d0}/{h}.qasm").read()
    s = [d["score"]] + [fast_check.check(text, d["data_qubits"], shots=10**8, seed=k, procs=int(os.environ.get("PROCS", 20))).score for k in (1000, 2000)]
    d.update(s1000=s[1], s2000=s[2], mean=sum(s) / 3); json.dump(d, open(f"{d0}/{h}.json", "w"))
    print(f"{h} cm{int(d['commute'])} s{d['seed']} 2q {d['n_2q']} s0 {s[0]:.4e} s1000 {s[1]:.4e} s2000 {s[2]:.4e} mean {sum(s)/3:.4e}", flush=True)
