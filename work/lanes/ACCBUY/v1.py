import sys
from elements import *
base = read(sys.argv[1])
def mk(name, rm, add):
    c = copy.deepcopy(base)
    for t, pair in rm:
        c['ops'].remove(find(c, t, pair, 'CX'))
    c = add_ops(c, add)
    print(save(c, name))
mk('v1a', [(35, (6, 0)), (36, (6, 0))], [(35, ['cx q[1],q[0];']), (36, ['cx q[1],q[0];'])])
mk('v1b', [(36, (6, 0))], [(36, ['cx q[1],q[0];'])])
mk('v1c', [(35, (13, 7)), (36, (13, 7))], [(35, ['cx q[1],q[7];']), (36, ['cx q[1],q[7];'])])
