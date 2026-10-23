import json, sys, time
import tprep
name = sys.argv[1]
text = open(name + ".qasm").read(); data = json.load(open(name + ".json"))["data_qubits"]
t = time.time()
rep = tprep.check(text, data, shots=10**8, seed=0)
print(rep); print(repr(rep.score), rep.acceptance, rep.n_2q, f"{time.time()-t:.0f}s")
sc = tprep.fault_scan(text, data); print(sc)
