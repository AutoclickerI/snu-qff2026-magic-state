"""Per-qubit op sequences of a stem: dump.py <stem under c/> [qubits...]"""
from gadgets import *
c = read(C / sys.argv[1])
qs = [int(x) for x in sys.argv[2:]] or range(36)
S1 = {int(BITRE.findall(l)[0]) for l in c['tail'] if l.startswith('// DETECTOR') and len(BITRE.findall(l)) == 1}
for q in qs:
    out = []
    for o in seq(c, q):
        u = unit(o)
        if u.name == 'CX':
            a, b = cx_qs(o); out.append(f"{o['t']}:{'>' if a == q else '<'}{b if a == q else a}")
        else:
            bs = bits_of(o)
            out.append(f"{o['t']}:{u.name}" + (f"c{bs[0]}" + ('*' if bs[0] in S1 else '') if bs else ''))
    print(q, ' '.join(out))
