"""Retain selector classes through latest-main buckets; diagnostic, not a repo patch.

Default: three-row ABBA component benchmark. --verify-all: one comparison per
acceptance/scored row for numerical equivalence, without repeated timing trials.
"""
from pathlib import Path
import os,sys,argparse,time,json
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[k]='1'
import numpy as np

ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('--repo',type=Path,default=os.environ.get('QUANTUMN_REPO'))
ap.add_argument('--stem',type=Path,default=None)
ap.add_argument('--output',type=Path,default=None)
ap.add_argument('--verify-all',action='store_true')
args=ap.parse_args()
if args.repo is None:ap.error('Pass --repo or QUANTUMN_REPO')
SP=Path(args.repo)/'work/lanes/MAIN/sparse'
sys.path.insert(0,str(SP))
import sparse_walsh as sw

def basis(vecs):
    piv={}
    for v in vecs:
        for h,w in sorted(piv.items(),reverse=True):
            if v>>h&1:v^=w
        if v:piv[v.bit_length()-1]=v
    for h in sorted(piv):
        for g in piv:
            if g!=h and piv[g]>>h&1:piv[g]^=piv[h]
    return tuple(piv[h] for h in sorted(piv))

def contract_quotient(compiled,states,emask,order):
    classes={}
    def cls(b):
        if b not in classes:
            rho=np.zeros(len(states),dtype=np.int64)
            for j,mask in enumerate(b):
                rho|=(np.bitwise_count(states&mask)&1).astype(np.int64)<<j
            _,first,inverse=np.unique(rho,return_index=True,return_inverse=True)
            classes[b]=(first,inverse)
        return classes[b]
    pos={v:i for i,v in enumerate(order)}
    grouped={}
    for entry in compiled:
        k=min((pos[v] for v in entry[0]),default=len(pos))
        grouped.setdefault(k,[]).append(entry)
    factors=[]
    for entries in grouped.values():
        scope=tuple(sorted(set().union(*(set(e[0]) for e in entries))))
        b=basis([km for e in entries for km,_,_ in e[2]])
        reps,_=cls(b)
        out=None
        for escope,chi,gens,_ in sorted(entries,key=lambda e:any(km for km,_,_ in e[2])):
            row,col=sw.patterns(escope,gens,states[reps],emask,{})
            out=sw.multiply(out,chi[np.arange(len(chi))[:,None]^col[sw.columns(escope,scope)][None,:]][row])
        factors.append((scope,b,out))
    peak=work=0
    for v in order:
        bucket=[f for f in factors if v in f[0]]
        factors=[f for f in factors if v not in f[0]]
        if not bucket:continue
        union=tuple(sorted(set().union(*(set(s) for s,_,_ in bucket))))
        b=basis([m for _,bb,_ in bucket for m in bb])
        reps,_=cls(b)
        result=np.empty((len(reps),1<<(len(union)-1)))
        for lo in range(0,len(reps),sw.CHUNK):
            here=reps[lo:lo+sw.CHUNK]
            out=None
            for scope,bb,a in sorted(bucket,key=lambda f:f[2].shape[0]):
                _,inverse=cls(bb)
                lift=a[inverse[here]]
                out=sw.multiply(out,np.take(lift,sw.columns(scope,union),axis=1))
            peak=max(peak,out.size);work+=out.size
            pairs=out.reshape(len(out),-1,2,1<<union.index(v))
            reduced=(pairs[:,:,0]+pairs[:,:,1]).reshape(len(out),-1)*.5
            result[lo:lo+len(here)]=reduced
        factors.append((tuple(q for q in union if q!=v),b,result))
    result=np.ones(len(states))
    for scope,b,a in factors:
        assert not scope
        _,inverse=cls(b)
        result*=a.reshape(-1)[inverse]
    return result,{'peak_bucket_elements':peak,'bucket_elements':work,'class_spaces':len(classes)}

stem=args.stem or SP.parent/'v36h'
m,e,g,nd,ks,psi,where,_=sw.prepare(stem,True)
compiled,elim=sw.compile_best(m,e,g,nd,ks)
rows=[]
for key in ([None]+e.keys if args.verify_all else [None,('X',0,0),('Y',0,0)]):
    states,weights,om=sw.sparse_kernel(e,ks,psi,where,key)
    emask=0 if key is None else sw.emask_for(key)
    timing={'latest_main':[],'retained_quotient':[]};vecs={}
    modes=['latest_main','retained_quotient'] if args.verify_all else ['latest_main','retained_quotient','retained_quotient','latest_main']
    for mode in modes:
        st=time.process_time()
        if mode=='latest_main':
            factors=sw.factors_for(compiled,states,emask,elim['order'])
            vec,peak=sw.contract_selector(factors,elim['order'],len(states))
        else:
            vec,counts=contract_quotient(compiled,states,emask,elim['order'])
        timing[mode].append(time.process_time()-st);vecs[mode]=vec
    a,b=vecs.values()
    rows.append({'key':key,'selector_states':len(states),'max_vector_difference':float(np.max(abs(a-b))),
                 'moment_difference':float(weights@(a-b)/(1<<len(ks))),
                 'latest_moment':float(weights@a/(1<<len(ks))),
                 'quotient_moment':float(weights@b/(1<<len(ks))),
                 'cpu_seconds':timing,'mean_cpu_seconds':{k:sum(v)/len(v) for k,v in timing.items()},
                 'quotient_counts':counts})
import hashlib
out={'implementation_reference_commit':'598ddad4c595ceb583e779a924d06749f950a997','source':str(stem),
     'qasm_sha256':hashlib.sha256(stem.with_suffix('.qasm').read_bytes()).hexdigest(),
     'evaluator_sha256':{p:hashlib.sha256((SP/p).read_bytes()).hexdigest() for p in ['sparse_walsh.py','frontend.py','fastfill.py','basis_warm.json']},
     'factors':len(compiled),'rows':rows,
     'novelty':'Latest main already uses first-bucket selector representatives then gathers back; this prototype preserves quotient indices through all subsequent buckets.',
     'limits':('All acceptance/scored rows compared once. Numerical equivalence check, not a performance benchmark.' if args.verify_all else 'Three representative v36h rows only. ABBA factor+contraction CPU component timing, not full latest-main end-to-end validation.')}
if args.verify_all:
    out['summary']={
        'max_vector_difference':max(r['max_vector_difference'] for r in rows),
        'max_moment_difference':max(abs(r['moment_difference']) for r in rows),
    }
    for name,field in [('latest_main','latest_moment'),('retained_quotient','quotient_moment')]:
        A=rows[0][field]
        obs=sum(w*b*r[field] for w,b,r in zip(e.W,e.beta,rows[1:]))
        out['summary'][name]={'acceptance':A,'loss':(A-obs)/(2*A)}
default=Path(__file__).with_name('selector_quotient_latest_all_keys.json') if args.verify_all else Path(__file__).with_suffix('.json')
(args.output or default).write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
