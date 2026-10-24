from pathlib import Path
import sys, json, time, hashlib
import numpy as np
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'source/work/lanes/MAIN/sparse'))
import sparse_walsh as sw
start=time.perf_counter()
m,e,g,nd,ks,psi,where,de=sw.prepare(ROOT/'source/work/lanes/MAIN/v36c',True)
c=sw.compile_channels(m,g,nd,ks)
order=sw.minfill([set(s) for s,_,_ in c])['order']
statesets={}; counts=[]; leaf_patterns=[set() for _ in c]
for key in [None]+e.keys:
    states,w,om=sw.sparse_kernel(e,ks,psi,where,key)
    h=hashlib.sha256(states.tobytes()).hexdigest()
    statesets.setdefault(h,{'n':len(states),'keys':[]})['keys'].append(key)
    counts.append(len(states))
    emask=0 if key is None else sw.emask_for(key)
    for i,(scope,p0,terms) in enumerate(c):
        leaf_patterns[i].add(tuple((ee&emask).bit_count()%2 for _,_,ee,_ in terms))
out={'channels':len(c),'moments':len(counts),'kernel_bits':len(ks),'dense_width':de['width'],
     'conditioned_width':sw.minfill([set(s) for s,_,_ in c])['width'],
     'kernel_support_groups':list(statesets.values()),'kernel_nonzero':counts,
     'leaf_sign_patterns_total':sum(len(p) for p in leaf_patterns),
     'naive_leaf_sign_patterns_total':len(c)*len(counts),
     'leaf_sign_pattern_hist':{str(n):sum(len(p)==n for p in leaf_patterns) for n in sorted(set(map(len,leaf_patterns)))},
     'seconds':time.perf_counter()-start}
(ROOT/'kernel_reuse_probe.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k not in ('kernel_support_groups','kernel_nonzero')},indent=2))
print('support_groups',[(v['n'],len(v['keys'])) for v in statesets.values()])
