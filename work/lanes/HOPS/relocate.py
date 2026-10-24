"""Bounded, timed block-relocation model using FREELAY's full live intervals."""
from build import *
import types
src=(ROOT/'work/lanes/FREELAY/co_design.py').read_text()
src=src.replace("HERE/'inputs", "ROOT/'work/lanes/FREELAY/inputs")
src=src.replace("if k=='d':m.Add(pos[0]==mp[D0[i]]);m.Add(init==pts[per[D0[i]][0]])", "if k=='d':m.Add(pos[0]==mp[D0[i]]);m.Add(init==pts[per[D0[i]][0]])\n   else:m.Add(pos[0]=={'a':AC,'b':BCELLS,'c':CCELLS}[k][i])")
src=src.replace("m.Minimize(obj)", "m.Add(sum(sum(v['moves']) for k,v in T.items() if k[0]=='d')<=5)\n m.Minimize(obj)",1)
ns={'__file__':str(OUT/'relocate_model.py'),'__name__':'hops_relocation_model'}
exec(compile(src,str(OUT/'relocate_model.py'),'exec'),ns)
a=types.SimpleNamespace(horizon=55,early_a=False,sym=0,row=0,col=0,option='l5_11',joint=True,dhops=3,bhops=2,fixed_endpoints=False,automorphisms=True,hint=None,calibration=None,workers=1,seconds=180,seed=0,out='relocation5',alap_tie=True)
ns['solve'](a)
