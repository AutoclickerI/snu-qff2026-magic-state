"""Lane-local repair: keep arbitrary-width detector masks in batch evaluation."""
import numpy as np
import engine

def batch_tables(self,S,D):
    if not hasattr(self,'phi_cache'):
        self.phi_cache={};self.idx_i=self.idx.astype(np.int64)
    S=np.asarray(S,dtype=np.int64);D=tuple(map(int,D));acc=engine._phi_all(self,S)
    for k,(mj,wj,coef) in enumerate(self.projs):
        bits=np.fromiter(((d>>k)&1 for d in D),dtype=np.int8,count=len(D))
        sg=(1-2*(int(self.v[k])^bits)).astype(float);perm=self.idx_i^mj
        acc=(acc+sg[:,None]*coef*(self.sgn(wj)[None,:]*acc)[:,perm])/2
    A=(np.abs(acc)**2).sum(axis=1);E=np.zeros((len(S),len(self.keys)));live=A>1e-18
    if live.any():
        a=acc[live]
        for q,key in enumerate(self.keys):
            mj,wj,coef=self.Qs[key];perm=self.idx_i^mj
            E[live,q]=(np.conj(a[:,perm])*coef*self.sgn(wj)[None,:]*a).sum(axis=1).real
    return A/self.A0,E/self.A0

engine.batch_tables=batch_tables
engine.Engine.batch_tables=batch_tables
