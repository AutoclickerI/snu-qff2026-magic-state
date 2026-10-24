from pathlib import Path
import sys,json,time,random
from collections import defaultdict
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'source/work/lanes/MAIN/sparse'))
import sparse_walsh as sw
m,e,g,nd,ks,psi,where,_=sw.prepare(ROOT/'source/work/lanes/MAIN/v36c',True)
rows=[sum(((f['d']>>i)&1)<<j for j,f in enumerate(m.faults)) for i in range(nd)]
free=[i for i in range(nd) if i not in ks]
channel_masks=[]
for fs in g.values():
    channel_masks.append(sum(1<<j for j,f in enumerate(m.faults) if f['chan']==fs[0]['chan']))
incidence=[{j for j,cm in enumerate(channel_masks) if r&cm} for r in rows]
scopes=[{i for i in free if j in incidence[i]} for j in range(len(g))]
base=sw.minfill(scopes);best=dict(base);steps=[];rng=random.Random(80353)
start=time.perf_counter();accepted=0;trials=1500
bestrows=list(rows);beststeps=[]
for it in range(trials):
    i,j=rng.sample(free,2)
    newrow=rows[i]^rows[j]
    newinc={c for c,cm in enumerate(channel_masks) if newrow&cm}
    add=newinc-incidence[i];remove=incidence[i]-newinc
    if not add and not remove:continue
    for c in add:scopes[c].add(i)
    for c in remove:scopes[c].remove(i)
    ev=sw.minfill(scopes)
    # A deterministic hill-climb on the declared contraction work objective.
    if (ev['work_entries'],ev['width'])<(best['work_entries'],best['width']):
        rows[i]=newrow;incidence[i]=newinc;steps.append([i,j]);best=ev;accepted+=1
        print(json.dumps({'trial':it,'row_xor':[i,j],'width':ev['width'],'work_entries':ev['work_entries']}),flush=True)
    else:
        for c in add:scopes[c].remove(i)
        for c in remove:scopes[c].add(i)
out={'basis_type':'invertible elementary XOR on identity-projector detectors only','detectors':nd,
     'active_kernel_detectors':[x for x in ks if x<nd],'identity_projector_rows':free,
     'before':base,'after':best,'elementary_row_xors':steps,'trials':trials,'accepted_steps':accepted,
     'seconds':time.perf_counter()-start}
(ROOT/'basis_width_probe.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
