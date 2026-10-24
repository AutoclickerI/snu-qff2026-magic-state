"""Native-tick QASM emitter preserving reused MX states with H;M;H."""
import json

def emit(ops,dets,stem,meta):
    used=sorted({q for o in ops for q in o.qs})
    n=max(o.bit for o in ops if o.bit is not None)+1
    out=['OPENQASM 2.0;','include "qelib1.inc";','qreg q[36];',f'creg c[{n}];']
    bar='barrier '+','.join(f'q[{q}]'for q in used)+';'
    for t in range(max(o.time for o in ops)+1):
        active=set()
        layer=[o for o in ops if o.time==t]
        for o in layer:
            assert not active.intersection(o.qs),(t,o,active)
            active.update(o.qs)
            if o.kind=='CX':assert abs(o.qs[0]//6-o.qs[1]//6)+abs(o.qs[0]%6-o.qs[1]%6)==1,o
            qs=','.join(f'q[{q}]'for q in o.qs)
            if o.kind in ('M','MX'):
                if o.kind=='MX':out.append(f'h {qs};')
                out.append(f'measure {qs} -> c[{o.bit}];')
                if o.kind=='MX':out.append(f'h {qs};')
            elif o.kind in ('R','RX'):
                out.append(f'reset {qs};')
                if o.kind=='RX':out.append(f'h {qs};')
            else:out.append(f'{o.kind.lower()} {qs};')
        if t!=max(o.time for o in ops):out.append(bar)
    out.extend('// DETECTOR '+' '.join(f'c[{b}]'for b in sorted(row))for row in dets)
    stem.with_suffix('.qasm').write_text('\n'.join(out)+'\n')
    stem.with_suffix('.json').write_text(json.dumps(meta,indent=2)+'\n')
