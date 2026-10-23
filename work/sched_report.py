"""Judge's ASAP schedule for a submission: depth, and per data qubit its last two-qubit gate
step and its idle steps (total, and after its last check interaction)."""
import sys
from tprep.qasm import to_stim
from tprep.noise import schedule


def report(text, data, quiet=False):
    stim, err = to_stim(text)
    assert not err, err
    prog, steps, gaps = schedule(stim)
    end = 0
    last2q, idle_total = {q: -1 for q in data}, {q: 0 for q in data}
    for ins, groups in zip(prog, steps):
        for qs, st in groups:
            end = max(end, st + 1)
            if len(qs) == 2:
                for q in qs:
                    if q in last2q:
                        last2q[q] = max(last2q[q], st)
    for i, q, first, n in gaps:
        if q in idle_total:
            idle_total[q] += n
    tail = {q: end - 1 - last2q[q] for q in data}
    if not quiet:
        print(f"depth {end}")
        for k, q in enumerate(data):
            print(f"  d{k} (q{q}): last 2q step {last2q[q]:3d}  idle total {idle_total[q]:3d}  tail after last 2q {tail[q]}")
    return end, last2q, idle_total, tail


if __name__ == "__main__":
    import importlib
    mod = importlib.import_module(sys.argv[1])
    report(mod.c.text(), mod.DATA)
