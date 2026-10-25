"""Phantom gap fillers on a full-barrier base: helper a (off-grid) prepared |+> (RX) at t_r, CX d->a at t_cx, MX a at t_m
(a deterministic detector). spec: {"base": stem, "fill": [[a, d, t_r, t_cx, t_m], ...], "kind": "plus"|"zero"}
kind zero: R a at t_r, CX a->d (|0> control), M a at t_m (known-state guard, detector on a)."""
import sys, json, re, shutil
from qedit import load

def build(spec, out):
    c = load(spec['base'])
    nb = c.max_creg() + 1
    kind = spec.get('kind', 'plus')
    for a, d, tr, tcx, tm in spec['fill']:
        if kind == 'plus':
            c.segs[tr].append([f'reset q[{a}];', f'h q[{a}];'])
            c.segs[tcx].append([f'cx q[{d}],q[{a}];'])
            c.segs[tm].append([f'h q[{a}];', f'measure q[{a}] -> c[{nb}];'])
        else:
            c.segs[tr].append([f'reset q[{a}];'])
            c.segs[tcx].append([f'cx q[{a}],q[{d}];'])
            c.segs[tm].append([f'measure q[{a}] -> c[{nb}];'])
        c.dets.append(f'// DETECTOR c[{nb}]'); nb += 1
    c.header = [h if not h.startswith('creg') else f'creg c[{nb}];' for h in c.header]
    c.header = [h if not h.startswith('qreg') else 'qreg q[40];' for h in c.header]
    for t, seg in enumerate(c.segs):
        seen = set()
        for g in seg:
            qs = set()
            for ln in g:
                qs |= set(map(int, re.findall(r'q\[(\d+)\]', ln)))
            assert not (qs & seen), ('conflict', t, g)
            seen |= qs
    open(out + '.qasm', 'w').write(c.text())
    shutil.copy(spec['base'] + '.json', out + '.json')

if __name__ == '__main__':
    build(json.load(open(sys.argv[1])), sys.argv[2])
