"""Memoize exact rotation/projector tables within one unchanged fault model."""
import numpy as np
def install(ev):
    engine=ev.e;original=engine.batch_n;cache={};stats={'requested':0,'computed':0}
    def batch(S,D):
        keys=list(zip(map(int,S),map(int,D)));stats['requested']+=len(keys)
        missing=list(dict.fromkeys(k for k in keys if k not in cache))
        if missing:
            a,n=original(np.array([k[0] for k in missing],dtype=np.int64),np.array([k[1] for k in missing],dtype=np.int64))
            for j,k in enumerate(missing):cache[k]=(a[j],n[j])
            stats['computed']+=len(missing)
        return np.array([cache[k][0] for k in keys]),np.array([cache[k][1] for k in keys])
    engine.batch_n=batch
    return stats
