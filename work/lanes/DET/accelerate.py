"""Exact early rejection for exact2's triple loop, using joint eigenspaces.

For these circuits all pulled detector projectors are diagonal in Engine's
rotation basis. A requested detector outcome outside that diagonal spectrum
has rigorously zero acceptance, independently of rotation signs. Skip these
rows before constructing Engine's 1024-entry logical-loss table.
"""
from analyze import *
import numpy as np
import exact2

def prepare(ev):
    e=ev.e
    assert all(x==0 for x,z,c in e.projs)
    d=np.zeros(e.N,dtype=np.int64)
    for j,(x,z,c) in enumerate(e.projs):
        d |= (((c.real*e.sgn(z))<0).astype(np.int64)^int(e.v[j]))<<j
    e.valid_d=np.unique(d)
    exact2._triple_chunk=triple_chunk

def triple_chunk(jobs):
    ev=exact2.G['ev'];tot=0.0;big=[]
    gs=np.array([s for s,d in ev.gkeys],dtype=np.int64)
    gd=np.array([d for s,d in ev.gkeys],dtype=np.int64)
    for ga,gb in jobs:
        cs=np.arange(gb,len(ev.gkeys))
        S=gs[ga]^gs[gb]^gs[cs]
        D=gd[ga]^gd[gb]^gd[cs]
        possible=np.isin(D,ev.e.valid_d)
        if not possible.any():
            continue
        cs=cs[possible]
        A,N=ev.e.batch_n(S[possible],D[possible])
        live=np.nonzero(N.max(axis=1)>1e-15)[0]
        if not len(live):
            continue
        ia,ib=ev.gmem[ga],ev.gmem[gb]
        for u in live:
            gc=int(cs[u]);ic=ev.gmem[gc];nt=N[u]
            ea,eb,ec=ev.fe[ia],ev.fe[ib],ev.fe[ic]
            pa,pb,pc=ev.fp[ia],ev.fp[ib],ev.fp[ic]
            ca,cb,cc=ev.fch[ia],ev.fch[ib],ev.fch[ic]
            step=max(1,int(2_000_000//max(1,len(ib)*len(ic))))
            for lo in range(0,len(ia),step):
                sl=slice(lo,lo+step)
                e3=ea[sl,None,None]^eb[None,:,None]^ec[None,None,:]
                val=nt[e3]*(pa[sl,None,None]*pb[None,:,None]*pc[None,None,:])
                mask=(ca[sl,None,None]!=cb[None,:,None]) & (ca[sl,None,None]!=cc[None,None,:]) & (cb[None,:,None]!=cc[None,None,:])
                if ga==gb:
                    mask &= ia[sl,None,None]<ib[None,:,None]
                if gb==gc:
                    mask &= ib[None,:,None]<ic[None,None,:]
                val*=mask
                t=float(val.sum());tot+=t
                if t>1e-14:
                    x,y,z=np.nonzero(val>3e-13)
                    for xx,yy,zz in zip(x,y,z):
                        big.append((float(val[xx,yy,zz]),int(ia[sl][xx]),int(ib[yy]),int(ic[zz])))
    return tot,big

if __name__=='__main__':
    from analyze import *
    results={}
    for name,stem in TARGETS.items():
        ev=Eval(stem.with_suffix('.qasm').read_text(),json.loads(stem.with_suffix('.json').read_text())['data_qubits'])
        prepare(ev);t=time.time()
        value,_=third_order(ev,1)
        baseline=json.loads((HERE/f'{name}_baseline.json').read_text())
        assert abs(value-baseline['T3a'])<1e-15,(name,value,baseline['T3a'])
        results[name]=dict(T3a=value,abs_error=abs(value-baseline['T3a']),seconds=time.time()-t)
        print(name,results[name],flush=True)
        (HERE/'acceleration_audit.json').write_text(json.dumps(results,indent=2))
