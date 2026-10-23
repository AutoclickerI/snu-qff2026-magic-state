"""Score the organizers' example circuit with the official judge."""
import sys
import time
from pathlib import Path

import tprep

shots = int(float(sys.argv[1])) if len(sys.argv) > 1 else 10**6
circuit = Path("../upstream/snu-qff2026-problem/examples/injection.qasm").read_text(encoding="utf-8")
data_qubits = [0, 6, 13, 2, 7, 8, 1]
t = time.time()
print(tprep.check(circuit, data_qubits, shots=shots, seed=0))
print(f"elapsed {time.time() - t:.1f}s")
if shots <= 10**6:
    t = time.time()
    print(tprep.fault_scan(circuit, data_qubits))
    print(f"fault_scan elapsed {time.time() - t:.1f}s")
