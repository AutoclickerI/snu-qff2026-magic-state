import sys
sys.path.insert(0,'.')
import layout, re
src = open('layout.py').read()
def run(tag, edits):
    s = src
    for a,b in edits:
        assert a in s, a
        s = s.replace(a,b)
    ns = {'__name__':'x'}
    exec(compile(s,'l','exec'), ns)
    pl = ns['placements']()[0]
    r = ns['solve'](pl, 30, 16)
    print(tag, r['status'], r.get('T'), r.get('staged'), flush=True)
    if 'o' in r: print(ns['show'](r))

CC=("for i in range(7):    # C_j ~ B_i if p3[i][j]","for i in []:")
COL=("m.Add(n1 == (7 - ncol if k != 1 else ncol))","pass")
CON=("m.Add(out - inn == 7 * r0[q] - absorb[q])","pass")
run("noconn_nocol", [CON,COL])
run("noC_nocol", [CC,COL])
run("chain only", [CON,CC])
