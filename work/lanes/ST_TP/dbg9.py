import sys
src=open('layout2.py').read()
def run(tag, edits, idx=4):
    s=src
    for a,b in edits:
        assert a in s,a
        s=s.replace(a,b)
    ns={'__name__':'x'}; exec(compile(s,'l','exec'),ns)
    r=ns['solve'](ns['placements']()[idx],40,16)
    print(tag,r['status'],r.get('T'),r.get('staged'),r.get('s'),r.get('h'),flush=True)
    if 'o' in r: print(ns['show'](r))
CON=("m.Add(out - inn == 7 * r0[q] - absorb[q])","pass")
#run("noconn",[CON])
#run("noconn_nopairs",[CON,("m.Add(te[x] <= fs[y]).OnlyEnforceIf([tmp[(x, q)], fin[(y, q)]])","pass")])

ONLY0=("    for k in blocks:\n        rg = [B() for _ in range(N)]","    for k in [0]:\n        rg = [B() for _ in range(N)]")
NOCOL=("m.Add(n1 == (7 - ncol if k != 1 else ncol))","pass")
NOREL=("                m.Add(ts[k] >= rel[q]).OnlyEnforceIf(tmp[(k, q)])\n                m.Add(fs[k] >= rel[q]).OnlyEnforceIf(fin[(k, q)])","                pass")
NOPAIR=("                m.Add(te[x] <= fs[y]).OnlyEnforceIf([tmp[(x, q)], fin[(y, q)]])","                pass")



NOTIME=("    for x in blocks:\n        for y in blocks:\n            if x == y:\n                continue","    for x in []:\n        for y in blocks:\n            if x == y:\n                continue")

ST1=("    m.AddExactlyOne(s1)","    m.Add(st[0]==1)\n    m.AddExactlyOne(s1)")
CB=("for i in range(7):    # C_j ~ B_i if p3[i][j]","for i in []:")
BO=("for i in range(7):    # B_i ~ O_i","for i in []:")
run("A: no C chain",[ONLY0,NOTIME,ST1,CB])
run("B: no B chain",[ONLY0,NOTIME,ST1,BO])
run("C: no chain",[ONLY0,NOTIME,ST1,BO,CB])
run("D: no chain no col",[ONLY0,NOTIME,ST1,BO,CB,NOCOL])
