"""Exhaustively screen all 128 choices of X-repetition-protected Steane sites.

Uses the noisy gadget and ideal output postselection toy in fano_storage.py.
Full-circuit performance and grid feasibility remain unproved.
"""
import json,runpy,contextlib,io,itertools
from pathlib import Path
with contextlib.redirect_stdout(io.StringIO()):
    g=runpy.run_path(str(Path(__file__).with_name('fano_storage.py')))
np=g['np'];lines=g['lines'];p=g['P']
rows=[]
for wait in (6,12):
    q=g['repeated'](p,wait);bare=np.array([1-q,q/3,q/3,q/3])
    prot,Ah=g['protected_channel'](wait)
    L0,A0=g['ideal_postselected_readout']([bare]*7)
    for mask in range(128):
        sites={i for i in range(7)if mask>>i&1}
        xs=sum(2**len(set(L)&sites)for L in lines)/2
        zy=1.5*sum(not(set(L)&sites)for L in lines)
        LL,AA=g['ideal_postselected_readout']([prot if i in sites else bare for i in range(7)])
        rows.append(dict(wait_ticks=wait,sites=sorted(sites),n=len(sites),
                         ideal_wrapper_cubic_coefficient=xs+zy,
                         conditional_loss=LL,relative_loss_change=LL/L0-1,
                         acceptance_relative_to_bare=AA*Ah**len(sites)/A0))
best=[]
for wait in (6,12):
    for k in range(8):
        cand=[r for r in rows if r['wait_ticks']==wait and r['n']==k]
        best.append(min(cand,key=lambda r:r['conditional_loss']))
out=dict(scope=__doc__,summary=best)
Path(__file__).with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
