"""Unchanged sparse contractions with exact acceptance evaluated first."""
import sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));import directed as d
sw=d.sw

def run(stem,floor=.5005):
 start=time.monotonic();m,eng,groups,nd,ks,psi,where,dense=sw.prepare(Path(stem),True)
 compiled,elim=sw.compile_best(m,eng,groups,nd,ks);sw._CTX.update(eng=eng,ks=ks,psi=psi,where=where,compiled=compiled,elim=elim)
 first=sw._row(None);A=first['value'];out=dict(acceptance=A,conditioned_width=elim['width'],acceptance_screen_exact=True,eligible=A>=floor)
 if A<floor:return dict(out,seconds=time.monotonic()-start)
 rows=[sw._row(key)for key in eng.keys];obs=sum(w*b*r['value']for w,b,r in zip(eng.W,eng.beta,rows));eA=first['absolute_kernel_omission_bound'];eO=sum(abs(w*b)*r['absolute_kernel_omission_bound']for w,b,r in zip(eng.W,eng.beta,rows))
 out.update(loss=(A-obs)/(2*A),conditional_loss_kernel_omission_bound=eO/(2*(A-eA))+abs(obs)*eA/(2*A*(A-eA)),seconds=time.monotonic()-start)
 return out
