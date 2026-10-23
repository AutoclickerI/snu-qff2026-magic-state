"""1-F of a circuit with one noise channel switched off at a time (diagnostic only)."""
import dataclasses
import sys
import tprep
from tprep.noise import STANDARD


def breakdown(text, data, shots=10**6):
    variants = {"standard": STANDARD}
    for f in ["gate1", "gate2", "meas", "reset", "idle", "meas_after", "initial"]:
        variants[f"no {f}"] = dataclasses.replace(STANDARD, **{f: 0.0})
    out = {}
    for name, nm in variants.items():
        r = tprep.check(text, data, shots=shots, noise=nm)
        out[name] = (r.score, r.sem, r.acceptance)
        print(f"{name:14s} 1-F={r.score:.3e} ± {r.sem:.1e}  acc={r.acceptance:.3f}", flush=True)
    return out


if __name__ == "__main__":
    import importlib
    mod = importlib.import_module(sys.argv[1])
    breakdown(mod.c.text(), mod.DATA)
