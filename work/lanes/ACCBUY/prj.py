"""Apply several pre-role guards (h,q,t[,rt]) jointly to a base plan. usage: prj.py <base stem> <out name> h:q:t[:rt] ..."""
import sys
from elements import *
base, out = sys.argv[1], sys.argv[2]
c = read(base)
specs = [tuple(int(x) for x in s.split(':')) for s in sys.argv[3:]]
for sp in specs:
    h, q, t = sp[:3]
    rt = sp[3] if len(sp) > 3 else None
    s = seq(c, h)
    # helper kind from the next init op at or after t
    init = next(o for o in s if unit(o).name in ('RESET', 'RX') and o['t'] >= (rt if rt is not None else -1))
    kind = 'Z' if unit(init).name == 'RESET' else 'X'
    if rt is not None:
        init['t'] = rt
    line = f'cx q[{h}],q[{q}];' if kind == 'Z' else f'cx q[{q}],q[{h}];'
    c = add_ops(c, [(t, [line])])
print(save(c, out, desc=dict(prerole_joint=specs)))
