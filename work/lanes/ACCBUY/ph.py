"""Phantom check builder on a full-barrier base (one segment = one native tick).
spec JSON: {"base": stem, "tmoves": [[q, t_new], ...], "checks": [...]}
check kinds:
  {"k": "Z", "a": anc, "r": t_reset, "cx": [[t, d], ...], "m": t_meas}        R a; CX d->a; M a
  {"k": "X", "a": anc, "r": t, "cx": [[t, d], ...], "m": t}                     RX a; CX a->d; MX a
  {"k": "XZ", "a1": z_anc, "a2": x_anc, "s": s, "f": [f1, f2], "sd": [s1, s2]}  blue-style (EARLY screen2check)
Conflicts (two ops on one qubit in a tick) raise.
"""
import sys, json, re
from qedit import load

def build(spec, out):
    c = load(spec['base'])
    for q, t2 in spec.get('tmoves', []):
        (t, j), = c.find(lambda g: g[0] == f"tdg q[{q}];")
        c.move(t, j, t2)
    b = c.max_creg() + 1
    nb = b
    def put(t, g):
        c.segs[t].append(g)
    for ch in spec['checks']:
        k = ch['k']
        if k in ('Z', 'X'):
            a = ch['a']
            put(ch['r'], [f'reset q[{a}];'] + ([f'h q[{a}];'] if k == 'X' else []))
            for t, d in ch['cx']:
                put(t, [f'cx q[{d}],q[{a}];'] if k == 'Z' else [f'cx q[{a}],q[{d}];'])
            put(ch['m'], ([f'h q[{a}];'] if k == 'X' else []) + [f'measure q[{a}] -> c[{nb}];'])
            c.dets.append(f'// DETECTOR c[{nb}]'); nb += 1
        elif k == 'XZ':
            a1, a2, s = ch['a1'], ch['a2'], ch['s']
            f1, f2 = ch['f']; s1, s2 = ch['sd']
            put(s, [f'reset q[{a1}];']); put(s, [f'reset q[{a2}];', f'h q[{a2}];'])
            put(s + 1, [f'cx q[{a2}],q[{a1}];'])
            put(s + 2, [f'cx q[{f1}],q[{a1}];']); put(s + 2, [f'cx q[{f2}],q[{a2}];'])
            put(s + 3, [f'cx q[{s1}],q[{a1}];']); put(s + 3, [f'cx q[{s2}],q[{a2}];'])
            put(s + 4, [f'cx q[{a1}],q[{s1}];']); put(s + 4, [f'cx q[{a2}],q[{s2}];'])
            put(s + 5, [f'cx q[{a1}],q[{f1}];']); put(s + 5, [f'cx q[{a2}],q[{f2}];'])
            put(s + 6, [f'cx q[{a2}],q[{a1}];'])
            put(s + 7, [f'h q[{a2}];', f'measure q[{a2}] -> c[{nb}];']); put(s + 7, [f'measure q[{a1}] -> c[{nb+1}];'])
            c.dets.append(f'// DETECTOR c[{nb}]'); c.dets.append(f'// DETECTOR c[{nb+1}]'); nb += 2
        else:
            raise ValueError(k)
    c.header = [h if not h.startswith('creg') else f'creg c[{nb}];' for h in c.header]
    c.header = [h if not h.startswith('qreg') else 'qreg q[38];' for h in c.header]
    for t in range(len(c.segs)):
        seen = set()
        for g in c.segs[t]:
            qs = set()
            for ln in g:
                qs |= set(map(int, re.findall(r'q\[(\d+)\]', ln)))
            if qs & seen:
                raise ValueError(('conflict', t, g))
            seen |= qs
    open(out + '.qasm', 'w').write(c.text())
    import shutil; shutil.copy(spec['base'] + '.json', out + '.json')

if __name__ == '__main__':
    spec = json.load(open(sys.argv[1]))
    build(spec, sys.argv[2])
