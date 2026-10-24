from pathlib import Path
import sys,json,hashlib
import numpy as np
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'source/work/lanes/MAIN/sparse'))
import sparse_walsh as sw
m,e,g,nd,ks,psi,where,_=sw.prepare(ROOT/'source/work/lanes/MAIN/v36c',True)
comp=sw.compile_channels(m,g,nd,ks)
order=sw.minfill([set(s) for s,_,_ in comp])['order']
groups={}
for key in [None]+e.keys:
    states,w,om=sw.sparse_kernel(e,ks,psi,where,key)
    h=hashlib.sha256(states.tobytes()).hexdigest()
    groups.setdefault(h,{'states':states,'rows':[]})['rows'].append((key,w,om))
certificate=[]
for group in groups.values():
    states,rows=group['states'],group['rows']
    ids={};meta={};nextid=0;naivework=0;uniquework=0
    for key,weights,om in rows:
        emask=0 if key is None else sw.emask_for(key)
        active=[]
        for i,(scope,p0,terms) in enumerate(comp):
            sig=tuple((ee&emask).bit_count()%2 for _,_,ee,_ in terms)
            token=('leaf',i,sig)
            if token not in ids:
                ids[token]=nextid;nextid+=1
                meta[ids[token]]=(scope,len(states) if any(km for km,_,_,_ in terms) else 1)
            active.append(ids[token])
        for v in order:
            bucket=[i for i in active if v in meta[i][0]]
            active=[i for i in active if v not in meta[i][0]]
            if not bucket:continue
            union=tuple(sorted(set().union(*(set(meta[i][0]) for i in bucket))))
            ns=max(meta[i][1] for i in bucket)
            work=ns*2**len(union);naivework+=work
            token=('node',v,tuple(bucket))
            if token not in ids:
                ids[token]=nextid;nextid+=1
                meta[ids[token]]=(tuple(q for q in union if q!=v),ns)
                uniquework+=work
            active.append(ids[token])
    certificate.append({'group_size':len(rows),'states':len(states),'keys':[k for k,_,_ in rows],
                        'naive_bucket_entries':naivework,'unique_bucket_entries':uniquework,
                        'ratio':naivework/uniquework})
out={'groups':certificate,'naive_bucket_entries':sum(x['naive_bucket_entries'] for x in certificate),
     'shared_bucket_entries':sum(x['unique_bucket_entries'] for x in certificate)}
out['bucket_work_ratio']=out['naive_bucket_entries']/out['shared_bucket_entries']
(ROOT/'shared_contraction_probe.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
