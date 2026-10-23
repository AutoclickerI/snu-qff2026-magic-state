"""Write a candidate's submission text + data_qubits and score it at the official setting.

    python save_sub.py <name> <module with c (Circ) and DATA> [shots]
"""
import importlib
import json
import sys
import time

import tprep

name, modname = sys.argv[1], sys.argv[2]
shots = int(float(sys.argv[3])) if len(sys.argv) > 3 else 10**8
mod = importlib.import_module(modname)
text, data = mod.c.text(), list(mod.DATA)
path = f"submissions/{name}.qasm"
open(path, "w", encoding="utf-8").write(text)
t = time.time()
rep = tprep.check(open(path, encoding="utf-8").read(), data, shots=shots, seed=0)
print(rep)
json.dump({"data_qubits": data, "score": rep.score, "sem": rep.sem, "acceptance": rep.acceptance,
           "n_2q": rep.n_2q, "shots": shots, "seed": 0, "passed": rep.passed, "module": modname,
           "seconds": time.time() - t}, open(f"submissions/{name}.json", "w"), indent=1)
print("saved", path, "elapsed", round(time.time() - t, 1), "s")
