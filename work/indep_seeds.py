import json, sys
sys.path.insert(0, "/home/jihoon/competitions/quantumn/work")
import fast_check
for name in sys.argv[1:]:
    text = open(name + ".qasm").read(); data = json.load(open(name + ".json"))["data_qubits"]
    for seed in (1000, 2000):
        r = fast_check.check(text, data, shots=10**8, seed=seed, procs=20)
        print(name.split("/")[-1], seed, f"{r.score:.5e} ± {r.sem:.1e} acc {r.acceptance:.4f}", flush=True)
