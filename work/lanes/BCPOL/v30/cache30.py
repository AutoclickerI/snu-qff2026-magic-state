"""All-orders boundary responses using sparse kernel selectors and open detectors."""
from evaluator import *
from cache import setup,fwht
from cache_allorders import minfill_keep,exact_prep

def open_selector(factors,order,keep,n):
    for v in order:
        bucket=[f for f in factors if v in f[0]];factors=[f for f in factors if v not in f[0]]
        if not bucket:continue
        union=tuple(sorted(set().union(*(set(s) for s,a in bucket))))
        rows=max(a.shape[0] for s,a in bucket)
        assert rows*(1<<len(union))<=2**27,('cache allocation guard',rows,len(union))
        out=np.ones((rows,)+(2,)*len(union))
        for scope,a in bucket:out*=a.reshape((a.shape[0],)+tuple(2 if u in scope else 1 for u in union))
        out=out.mean(axis=1+union.index(v));factors.append((tuple(u for u in union if u!=v),out))
    out=np.ones((n,)+(2,)*len(keep))
    for scope,a in factors:
        assert set(scope)<=set(keep)
        out*=a.reshape((a.shape[0],)+tuple(2 if u in scope else 1 for u in keep))
    # Flatten only detector axes in little-endian order; the selector is external.
    if keep:out=np.transpose(out,(0,)+tuple(range(len(keep),0,-1)))
    return out.reshape(n,-1)

def compile(stem):
    t=time.monotonic();ev,b,classes,prep,ext,hh=setup(stem)
    m,e,groups,nd,ks,psi,where,full=prepare_model(stem,True,ev)
    def canonical(d):
        original=d
        for i,mask in m.detector_row_changes.items():d=(d&~(1<<i))|(((original&mask).bit_count()%2)<<i)
        return d
    classes=[(s,canonical(d),ee) for s,d,ee in classes]
    assert all(s==0 for s,d,ee in classes),'boundary crosses a later non-Clifford rotation'
    outside={ch:fs for ch,fs in groups.items() if ch not in prep}
    compiled=sw.compile_channels(m,outside,nd,ks)
    union=0
    for s,d,ee in classes:union|=d
    keep=tuple(i for i in range(nd) if union>>i&1 and i not in ks)
    order,width=minfill_keep([set(sc) for sc,_,_ in compiled],keep)
    ridx=np.array([sum(((d>>q)&1)<<j for j,q in enumerate(keep)) for s,d,ee in classes])
    kidx=np.array([sum(((d>>q)&1)<<j for j,q in enumerate(ks) if q<nd) for s,d,ee in classes],dtype=np.uint32)
    es=np.array([ee for s,d,ee in classes],dtype=np.uint32);obs=np.zeros(len(classes));A=None;bounds=[]
    print(json.dumps(dict(event='cache_graph',rank=len(b.vecs),kept=len(keep),width=width,inside=len(prep),outside=len(outside))),flush=True)
    for j,key in enumerate([None]+e.keys):
        states,weights,bound=sw.sparse_kernel(e,ks,psi,where,key);emask=0 if key is None else sw.emask_for(key)
        factors=sw.factors_for(compiled,states,emask)
        ft=open_selector(factors,order,keep,len(states));resp=fwht(ft)/(1<<len(keep))
        signs=1-2*(np.bitwise_count(states[:,None]&kidx[None,:])%2).astype(float)
        values=np.sum(weights[:,None]*signs*resp[:,ridx],axis=0)/(1<<len(ks))
        if key is not None:values*=1-2*(np.bitwise_count(es&emask)%2).astype(float)
        if j==0:A=values
        else:obs+=e.W[j-1]*e.beta[j-1]*values
        bounds.append(bound)
        if j%8==0:print(json.dumps(dict(character=j,seconds=time.monotonic()-t)),flush=True)
    N=.5*(A-obs);p=exact_prep(ev,prep,len(classes));result=dict(loss=float(p@N/(p@A)),acceptance=float(p@A),numerator=float(p@N),seconds=time.monotonic()-t,width=width,exterior_hash=hh,boundary_rank=len(b.vecs),prep_channels=len(prep),all_orders=True,max_kernel_omission_bound=max(bounds))
    np.savez_compressed(stem.with_suffix('.boundary_allorders.npz'),N=N,A=A,exterior_hash=hh)
    stem.with_suffix('.boundary_allorders.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
    return result

if __name__=='__main__':compile(Path(sys.argv[1]))
