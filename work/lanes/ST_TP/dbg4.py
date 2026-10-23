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
ST=("    st = [B() for _ in blocks]","    st = [m.NewConstant(1) for _ in blocks]")
run("allstaged_noconn",[CON,ST])
run("allstaged",[ST])
run("conn_O_only",[("    for k in blocks:\n        rg = [B() for _ in range(N)]","    for k in [0]:\n        rg = [B() for _ in range(N)]")])
run("conn_B_only",[("    for k in blocks:\n        rg = [B() for _ in range(N)]","    for k in [1]:\n        rg = [B() for _ in range(N)]")])
run("conn_C_only",[("    for k in blocks:\n        rg = [B() for _ in range(N)]","    for k in [2]:\n        rg = [B() for _ in range(N)]")])
