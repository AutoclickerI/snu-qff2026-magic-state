"""Map each creg bit of a QASM file to (qubit, native step, basis)."""
import sys, re
from tprep.qasm import to_stim
from tprep.noise import schedule
text = open(sys.argv[1]).read()
stim, err = to_stim(text)
prog, steps, gaps = schedule(stim)
# measurement order in stim == measure statements order in qasm
meas_bits = [int(m) for m in re.findall(r'^measure q\[\d+\] -> c\[(\d+)\];', text, re.M)]
k = 0
out = {}
for ins, groups in zip(prog, steps):
    if ins.name in ('M', 'MX', 'MZ'):
        for qs, st in groups:
            out.setdefault(meas_bits[k], []).append((qs[0], st, ins.name)); k += 1
for b in sorted(out):
    print(b, out[b])
