"""1-F with idle noise restricted to windows, 1e8 shots via fast_check (seed 0)."""
import json, sys
sys.path.insert(0, "/home/jihoon/competitions/quantumn/work")
import tprep.noise as tn
from tprep.qasm import to_stim
import fast_check
_orig = tn.schedule
name = sys.argv[1]; cut = int(sys.argv[2]) if len(sys.argv) > 2 else None
text = open(name + ".qasm").read(); data = json.load(open(name + ".json"))["data_qubits"]
prog, steps, gaps = _orig(to_stim(text)[0])
end = max(s for g in steps for _, s in g) + 1
# cycle start: first step where a final-cycle ancilla reset happens is hard to know generically; use arg
print("depth", end, "cut", cut)
def run(window, qubits=None):
    def patched(t):
        p, s, g = _orig(t)
        keep = []
        for i, q, first, n in g:
            lo, hi = window
            a, b = max(first, lo), min(first + n, hi)
            if b <= a or (qubits is not None and q not in qubits):
                continue
            keep.append((i, q, a, b - a))
        return p, s, keep
    tn.schedule = patched
    try:
        return fast_check.check(text, data, shots=10**8, procs=20)
    finally:
        tn.schedule = _orig
D = set(data); A = set(range(36)) - D
for lab, w, qs in [("no idle", (0, 0), None), ("pre all", (0, cut), None), ("pre data", (0, cut), D), ("pre anc", (0, cut), A),
                   ("cycle all", (cut, 10**9), None), ("cycle data", (cut, 10**9), D), ("all", (0, 10**9), None)]:
    r = run(w, qs)
    print(f"{lab:11s} 1-F {r.score:.4e} ± {r.sem:.1e} acc {r.acceptance:.4f}", flush=True)
