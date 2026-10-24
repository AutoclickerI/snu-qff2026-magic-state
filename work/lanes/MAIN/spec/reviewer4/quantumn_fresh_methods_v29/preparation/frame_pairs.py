"""Second-order risk of first-order-correctable detector cosets on v29c.

The gate noise and rotation state are inherited from frame_syndrome_screen.
This is a screening calculation; no finite-p or official judge gain claim.
"""
import json,time
from pathlib import Path
import numpy as np
import frame_syndrome_screen as f

t0=time.perf_counter()
m,eng=f.m,f.eng
rows=sorted(f.safe_nonidentity,key=lambda r:r['syndrome'])
targets=np.array([0]+[r['syndrome'] for r in rows],dtype=np.int64)
best_masks=np.array([0]+[{'I':0,'X':128,'Z':64,'Y':192}[r['best_frame']] for r in rows],dtype=np.int64)
fs=np.array([x['s'] for x in m.faults],dtype=np.int64)
fd=np.array([x['d'] for x in m.faults],dtype=np.int64)
fe=np.array([x['e'] for x in m.faults],dtype=np.int64)
ch=np.array([x['chan'] for x in m.faults],dtype=np.int64)
pr=np.array([x['p'] for x in m.faults])
svals=sorted({int(x)^int(y) for x in set(fs) for y in set(fs)})
slut=np.full(max(svals)+1,-1,dtype=np.int64);slut[svals]=np.arange(len(svals))
A=np.zeros((len(svals),len(f.sectors)))
N=np.zeros((len(svals),len(f.sectors),1024))
for i,s in enumerate(svals):
    phi=eng.phi(s)
    for j,d in enumerate(f.sectors):
        vec=phi*(f.sector==d);a=np.vdot(vec,vec).real/eng.A0
        A[i,j]=a
        if a<1e-15:continue
        E=np.array([eng.expect(vec,eng.Qs[k]) for k in eng.keys])/eng.A0
        N[i,j]=.5*(a-eng.SG@E)
print('kernel_ready',len(svals),len(f.sectors),time.perf_counter()-t0,flush=True)
pair_loss=np.zeros(len(targets));pair_mass=np.zeros(len(targets))
for lo in range(0,len(fs),128):
    ia=np.arange(lo,min(lo+128,len(fs)))[:,None];ib=np.arange(len(fs))[None,:]
    ii,jj=np.nonzero((ia<ib)&(ch[ia]!=ch[ib]));ii+=lo
    ss=slut[fs[ii]^fs[jj]];dd=fd[ii]^fd[jj];ee=fe[ii]^fe[jj];pp=pr[ii]*pr[jj]
    for j,d in enumerate(f.sectors):
        live=A[ss,j]>1e-15
        actual=dd[live]^d
        indexes=np.searchsorted(targets,actual)
        indexes=np.minimum(indexes,len(targets)-1)
        valid=targets[indexes]==actual
        if not np.any(valid):continue
        indexes=indexes[valid];sss=ss[live][valid];eee=ee[live][valid];ppp=pp[live][valid]
        nn=N[sss,j,eee^best_masks[indexes]]
        pair_loss+=np.bincount(indexes,weights=ppp*nn,minlength=len(targets))
        pair_mass+=np.bincount(indexes,weights=ppp*A[sss,j],minlength=len(targets))
baseline=pair_loss[0]
for i,r in enumerate(rows,1):
    r['additional_pair_loss']=float(pair_loss[i])
    r['pair_probability_mass']=float(pair_mass[i])
    r['leading_conditional_loss_of_added_sector']=float(pair_loss[i]/r['single_probability_mass'])
    r['score_delta_proxy_at_baseline_6p3451e5']=float(pair_loss[i]-6.3451e-5*r['single_probability_mass'])
rows.sort(key=lambda r:r['score_delta_proxy_at_baseline_6p3451e5'])
out=dict(scope='All distinct-channel pairs; each candidate admits kernel {0,v} with its best first-order-safe logical frame',
         baseline_second_order_loss=float(baseline),candidate_count=len(rows),
         negative_delta_proxy_count=sum(r['score_delta_proxy_at_baseline_6p3451e5']<0 for r in rows),
         seconds=time.perf_counter()-t0,candidates=rows)
Path(__file__).with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({**{k:v for k,v in out.items() if k!='candidates'},'best':rows[:8]},indent=2))
