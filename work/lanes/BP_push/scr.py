import json, sys, os
sys.path.insert(0, "/home/jihoon/competitions/quantumn/work")
import fast_check
dq = json.load(open(sys.argv[1]))["data_qubits"]
for f in sys.argv[2:]:
    t = open(f).read(); r = fast_check.check(t, dq, shots=10**8, procs=int(os.environ.get("PROCS", 20)))
    print(f, f"{r.score:.5e} acc {r.acceptance:.4f} 2q {r.n_2q} pass {r.passed}", flush=True)
