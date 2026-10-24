"""Exact pruning of impossible detector syndromes, retaining exact2's algebra."""
import itertools
import numpy as np

def allowed_detectors(e):
    # P = c X^x Z^z. Gaussian elimination tracks multiplication phases and
    # detector-outcome parity. Independent commuting rows have all eigenvalues.
    basis={}; constraints=[]; independent=[]
    r=e.r
    for k,(x,z,c) in enumerate(e.projs):
        bits=1<<k
        while x or z:
            pivot=(x|(z<<r)).bit_length()-1
            if pivot not in basis:
                basis[pivot]=(x,z,c,bits); independent.append(k); break
            xx,zz,cc,bb=basis[pivot]
            c=c*cc*((-1)**((z&xx).bit_count()&1))
            x^=xx; z^=zz; bits^=bb
        else:
            assert abs(c.imag)<1e-9 and abs(abs(c.real)-1)<1e-9
            # Product eigenvalue (-1)^sum(actual bits) = scalar c.
            want=int(c.real<0)
            ref=sum(int(e.v[j]) for j in range(len(e.v)) if bits>>j&1)&1
            constraints.append((bits,want^ref))
    independent_set=set(independent)
    dep=[k for k in range(len(e.projs)) if k not in independent_set]
    allowed=[]
    for v in range(1<<len(independent)):
        d=sum(((v>>j)&1)<<k for j,k in enumerate(independent))
        # Each dependent constraint's largest bit is its newly reduced row.
        for mask,want in constraints:
            k=mask.bit_length()-1
            d|=(((d&mask).bit_count()&1)^want)<<k
        assert all(((d&m).bit_count()&1)==v for m,v in constraints)
        allowed.append(d)
    return frozenset(allowed)

def prepare(ev):
    allowed=allowed_detectors(ev.e)
    original=ev.e.ntable
    cache={}
    def ntable(s,d):
        if d not in allowed: return 0.0,None
        key=(s,d)
        if key not in cache: cache[key]=original(s,d)
        return cache[key]
    ev.e.ntable=ntable
    return allowed

def third(ev,allowed):
    """Same distinct-channel weight-three sum as exact2.third_order, sparse join."""
    ds={}
    for g,(_,d) in enumerate(ev.gkeys): ds.setdefault(d,[]).append(g)
    total=0.0; combinations=0
    for ga,(sa,da) in enumerate(ev.gkeys):
        ia=ev.gmem[ga]
        for gb in range(ga,len(ev.gkeys)):
            sb,db=ev.gkeys[gb]; ib=ev.gmem[gb]
            for target in allowed:
                for gc in ds.get(da^db^target,[]):
                    if gc<gb: continue
                    sc,dc=ev.gkeys[gc]
                    _,nt=ev.e.ntable(sa^sb^sc,target)
                    if nt is None or np.max(nt)<1e-15: continue
                    ic=ev.gmem[gc]; combinations+=1
                    # Chunk exactly as the upstream evaluator to bound memory.
                    stride=max(1,2_000_000//max(1,len(ib)*len(ic)))
                    for lo in range(0,len(ia),stride):
                        aa=ia[lo:lo+stride]
                        ee=ev.fe[aa,None,None]^ev.fe[ib][None,:,None]^ev.fe[ic][None,None,:]
                        value=nt[ee]*(ev.fp[aa,None,None]*ev.fp[ib][None,:,None]*ev.fp[ic][None,None,:])
                        ca,cb,cc=ev.fch[aa,None,None],ev.fch[ib][None,:,None],ev.fch[ic][None,None,:]
                        mask=(ca!=cb)&(ca!=cc)&(cb!=cc)
                        if ga==gb: mask &= aa[:,None,None]<ib[None,:,None]
                        if gb==gc: mask &= ib[None,:,None]<ic[None,None,:]
                        total+=float((value*mask).sum())
    return total,combinations
