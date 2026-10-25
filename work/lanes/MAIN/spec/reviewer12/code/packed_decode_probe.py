import json,time,resource
from pathlib import Path
import numpy as np

rng=np.random.default_rng(20261025)
shots=10**6
n_meas=97
meas=rng.integers(0,256,(shots,(n_meas+7)//8),dtype=np.uint8)
keep=rng.random(shots)<.50164

def original():
    syn=np.unpackbits(meas[keep],axis=1,bitorder='little')[:,n_meas-6:n_meas].astype(bool)
    return syn[:,:3].any(axis=1),syn[:,3:].any(axis=1)

def masks(start,end):
    d={}
    for k in range(start,end):d[k>>3]=d.get(k>>3,0)|(1<<(k&7))
    return d

zmask=masks(n_meas-6,n_meas-3)
xmask=masks(n_meas-3,n_meas)
def packed():
    relevant={b:meas[:,b][keep] for b in zmask.keys()|xmask.keys()}
    z=np.zeros(int(keep.sum()),dtype=bool)
    x=z.copy()
    for b,m in zmask.items():z|=(relevant[b]&m)!=0
    for b,m in xmask.items():x|=(relevant[b]&m)!=0
    return z,x

a=original();b=packed()
assert all(np.array_equal(x,y) for x,y in zip(a,b))
timings={'original':[],'packed':[]}
for name in ['original','packed','packed','original']*8:
    start=time.process_time()
    (original if name=='original' else packed)()
    timings[name].append(time.process_time()-start)
out={'synthetic':True,'shots':shots,'n_meas':n_meas,'kept':int(keep.sum()),
     'same_fix_bits':True,'unpack_intermediate_bytes':int(keep.sum())*8*((n_meas+7)//8),
     'syndrome_byte_masks':{'z':zmask,'x':xmask},
     'median_cpu_seconds':{k:float(np.median(v)) for k,v in timings.items()},
     'timing_cpu_seconds':timings,
     'limits':'Synthetic packed arrays only, no xtim or whole race speedup claimed.'}
out['postprocess_ratio']=out['median_cpu_seconds']['original']/out['median_cpu_seconds']['packed']
Path(__file__).with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
