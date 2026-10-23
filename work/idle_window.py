"""Diagnostic: 1-F with idle noise restricted to a time window and/or qubit set (all other noise
as in the official model). Patches tprep.noise.schedule's idle gaps in this process only."""
import sys
import tprep
import tprep.noise as tn

_orig = tn.schedule


def run(text, data, window=None, qubits=None, shots=10**7):
    def patched(t):
        prog, steps, gaps = _orig(t)
        keep = []
        for i, q, first, n in gaps:
            lo, hi = window if window else (0, 10**9)
            a, b = max(first, lo), min(first + n, hi)
            if b <= a or (qubits is not None and q not in qubits):
                continue
            keep.append((i, q, a, b - a))
        return prog, steps, keep
    tn.schedule = patched
    try:
        r = tprep.check(text, data, shots=shots)
    finally:
        tn.schedule = _orig
    return r


if __name__ == "__main__":
    import importlib
    mod = importlib.import_module(sys.argv[1])
    text, data = mod.c.text(), mod.DATA
    from tprep.qasm import to_stim
    prog, steps, gaps = _orig(to_stim(text)[0])
    end = max(s + 1 for g in steps for _, s in g)
    cuts = [int(x) for x in sys.argv[2].split(",")] if len(sys.argv) > 2 else [0, end // 3, 2 * end // 3, end]
    print("depth", end, "windows", cuts)
    r = run(text, data, window=(0, 0)); print(f"no idle            1-F={r.score:.4g} ± {r.sem:.1g}", flush=True)
    for lo, hi in zip(cuts, cuts[1:]):
        for name, qs in (("data", set(data)), ("ancilla", None if False else set(range(36)) - set(data))):
            r = run(text, data, window=(lo, hi), qubits=qs)
            print(f"idle {name:7s} [{lo:2d},{hi:2d})  1-F={r.score:.4g} ± {r.sem:.1g}  acc={r.acceptance:.3f}", flush=True)
    r = run(text, data); print(f"all idle           1-F={r.score:.4g} ± {r.sem:.1g}")
