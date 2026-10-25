import sys
from elements import *
base = read(sys.argv[1])
def mk(name, items, det=True):
    c = copy.deepcopy(base)
    m = bit(c)
    its = [(t, [l.replace('BIT', str(m)) for l in lines]) for t, lines in items]
    c = add_ops(c, its)
    if det:
        c['tail'].append(f'// DETECTOR c[{m}]')
    print(save(c, name))
mk('rd19', [(35, ['measure q[19] -> c[BIT];'])])
