"""tprep.check at 1e6 shots, then 1e8-shot MC at seeds 0/1000/2000:  mc3.py <stem>... [--procs N]"""
import json, sys
sys.path.insert(0, "/home/jihoon/competitions/quantumn/work")
import fast_check, tprep
args = [a for a in sys.argv[1:] if not a.startswith("--")]
procs = int(sys.argv[sys.argv.index("--procs") + 1]) if "--procs" in sys.argv else 16
args = [a for a in args if not a.isdigit()]
for stem in args:
    text = open(stem + ".qasm").read(); data = json.load(open(stem + ".json"))["data_qubits"]
    r = tprep.check(text, data, shots=10**6, seed=0)
    print(stem, "check", r.passed, f"acc {r.acceptance:.4f}", flush=True)
    s = []
    for seed in (0, 1000, 2000):
        r = fast_check.check(text, data, shots=10**8, seed=seed, procs=procs)
        s.append(r.score)
        print(stem, seed, f"{r.score:.6e} ± {r.sem:.1e} acc {r.acceptance:.5f}", flush=True)
    print(stem, "mean", f"{sum(s) / 3:.6e}", flush=True)
