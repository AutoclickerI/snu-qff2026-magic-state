import sys
sys.path.insert(0,'.')
from layout import *
pls = placements()
CON=("m.Add(out - inn == 7 * r0[q] - absorb[q])","pass")
src=open('layout.py').read()
for a,b in [CON,("m.Add(n1 == (7 - ncol if k != 1 else ncol))","pass")]: src=src.replace(a,b)
ns={'__name__':'x'}; exec(compile(src,'l','exec'),ns)
for i,pl in enumerate(pls):
    r=ns['solve'](pl,20,16)
    print(i,pl['sym'],pl['dr'],pl['dc'],r['status'],r.get('T'),r.get('staged'),flush=True)
