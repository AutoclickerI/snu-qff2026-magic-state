"""Print the judge's native schedule of a QASM file per qubit: step:op."""
import sys
from tprep.qasm import to_stim
from tprep.noise import schedule
def timeline(text):
    stim, err = to_stim(text)
    assert stim is not None, err
    prog, steps, gaps = schedule(stim)
    per = {}
    for ins, groups in zip(prog, steps):
        for qs, st in groups:
            for q in qs:
                tag = ins.name
                if ins.name == 'CX':
                    tag = ('C>' + str(qs[1])) if q == qs[0] else ('T<' + str(qs[0]))
                per.setdefault(q, []).append((st, tag))
    return per, gaps
if __name__ == '__main__':
    text = open(sys.argv[1]).read()
    per, gaps = timeline(text)
    end = max(st for v in per.values() for st, _ in v) + 1
    print('depth', end)
    for q in sorted(per):
        print(f'q{q:2d}', ' '.join(f'{s}:{t}' for s, t in per[q]))
