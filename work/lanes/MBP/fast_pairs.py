"""Exact pair pruning by state-independent detector-parity constraints.

Skipped pairs have a_ab=0. At least one individual has a=0 as well, and any
nonzero individual acceptance has syndrome 0; therefore their numerator and
normalization loss terms both vanish. A2 is reconstructed analytically.
"""
import inspect,sys,numpy as np
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[3]/'work/lanes/EVAL'))
import exact2
from model import Basis

def make_pairs(ev):
    basis=Basis();indices=[];constraints=[]
    for i,(x,z,c) in enumerate(ev.e.projs):
        vec=x|(z<<ev.e.r);combo=basis.express(vec)
        if combo is None:basis.add(vec);indices.append(i)
        else:
            relation=1<<i
            for j,bi in enumerate(indices):
                if combo>>j&1:relation^=1<<bi
            constraints.append(relation)
    def syn(d):return sum(((d&h).bit_count()%2)<<i for i,h in enumerate(constraints))
    groups={}
    for i,(s,d) in enumerate(ev.gkeys):groups.setdefault(syn(d),[]).append(i)
    return [(a,b) for gs in groups.values() for j,a in enumerate(gs) for b in gs[j:]]

def pair_chunk(args):
    # Keep exact2's numerator arithmetic. Only the A2 correction differs:
    # return the accepted-pair mass, instead of its centered polynomial.
    return FAST_CHUNK(args)

src=inspect.getsource(exact2._pair_chunk)
assert 'Asum += float((pp * cross).sum() * (1 - aa - ab + a_ab))' in src
src=src.replace('Asum += float((pp * cross).sum() * (1 - aa - ab + a_ab))','Asum += float((pp * cross).sum() * a_ab)')
ns=dict(exact2.__dict__);exec(compile(src,__file__+':chunk','exec'),ns);FAST_CHUNK=ns['_pair_chunk']

src=inspect.getsource(exact2.run)
old='pairs = [(a, b) for a in range(ng) for b in range(a, ng)]'
assert old in src;src=src.replace(old,'pairs = _mbp_make_pairs(ev)')
src=src.replace('A2 = sum(r[1] for r in res)',"A2 = sum(r[1] for r in res)\n    Pch = np.bincount(ev.fch, weights=ev.fp)\n    Ach = np.bincount(ev.fch, weights=ev.fp * ev.a_single)\n    A2 += 0.5 * (ev.fp.sum() ** 2 - Pch @ Pch) - (ev.fp.sum() * Ach.sum() - Pch @ Ach)")
ns=dict(exact2.__dict__,_mbp_make_pairs=make_pairs,_pair_chunk=pair_chunk)
exec(compile(src,__file__+':run','exec'),ns);run=ns['run']
