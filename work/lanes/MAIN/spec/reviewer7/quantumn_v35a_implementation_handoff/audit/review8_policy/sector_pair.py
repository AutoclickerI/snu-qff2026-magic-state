"""All-orders four-sector acceptance/frame oracle for A input/output flags on v35a.

All other original detectors stay zero. This diagnoses record information
and can price the legal XOR-merge policy without adding physical operations.
It is not a nonlinear policy implementation or a free-frame performance claim.
"""
from pathlib import Path
import sys,json,time
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'audit/reaudit_evaluation/portable'))
import sparse_walsh as sw

def contract(factors,order,keep,batch_size):
    peak=0
    for v in order:
        if v in keep:continue
        bucket=[f for f in factors if v in f[0]]
        factors=[f for f in factors if v not in f[0]]
        if not bucket:continue
        union=tuple(sorted({q for s,_ in bucket for q in s}))
        n=max(a.shape[0] for _,a in bucket)
        out=np.ones((n,)+(2,)*len(union));peak=max(peak,out.size)
        for scope,a in bucket:
            out*=a.reshape((a.shape[0],)+tuple(2 if u in scope else 1 for u in union))
        out=out.mean(axis=1+union.index(v))
        factors.append((tuple(q for q in union if q!=v),out))
    union=tuple(sorted(keep));out=np.ones((batch_size,)+(2,)*len(union))
    for scope,a in factors:
        assert set(scope)<=keep
        out*=a.reshape((a.shape[0],)+tuple(2 if u in scope else 1 for u in union))
    return out,peak

if __name__=='__main__':
    stem=ROOT/'quantumn_review8/work/lanes/MAIN/v35a'
    bits=list(map(int,sys.argv[1].split(','))) if len(sys.argv)>1 else [16,272]
    assert len(bits)==2
    m,e,groups,nd,ks,psi,where,elim=sw.prepare(stem,True)
    keep={next(i for i,row in enumerate(m.dets) if row=={b}) for b in bits}
    assert not keep&set(ks)
    mask=sum(1<<i for i in keep)
    assert all(not(v&mask) for v in m.detector_row_changes.values())
    c=sw.compile_channels(m,groups,nd,ks)
    scopes=[set(s) for s,_,_ in c]
    # Eliminate retained variables last, without actually summing them.
    scopes += [set(keep)]
    order=sw.minfill(scopes)['order']
    rows=[];start=time.perf_counter()
    for index,key in enumerate([None]+e.keys):
        states,weights,err=sw.sparse_kernel(e,ks,psi,where,key)
        a,peak=contract(sw.factors_for(c,states,0 if key is None else sw.emask_for(key)),
                        order,keep,len(states))
        coeff=np.tensordot(weights,a,axes=(0,0)).reshape(-1)/(1<<len(ks))
        mass=sw.fwht(coeff)/(1<<len(keep))
        rows.append(dict(key=key,sector_masses=mass.tolist(),peak_elements=peak,
                         kernel_omission_bound=err))
        if index%12==0:print(json.dumps(dict(index=index,seconds=time.perf_counter()-start)),flush=True)
    A=np.array(rows[0]['sector_masses']);X=np.zeros_like(A);Y=np.zeros_like(A)
    for k,w,b,row in zip(e.keys,e.W,e.beta,rows[1:]):
        if k[0]=='X':X+=w*b*np.array(row['sector_masses'])
        else:Y+=w*b*np.array(row['sector_masses'])
    sectors=[]
    for i,a in enumerate(A):
        risks={f:.5-(sx*X[i]+sy*Y[i])/(2*a) for f,sx,sy in
               [('I',1,1),('X',1,-1),('Y',-1,1),('Z',-1,-1)]}
        sectors.append(dict(sector=i,acceptance=float(a),loss=risks['I'],
                            best_frame=min(risks,key=risks.get),best_loss=min(risks.values())))
    policies=[]
    for name,selected in [('both_zero',[0]),('xor_zero',[0,3]),
                           ('accept_00_01',[0,1]),('accept_00_10',[0,2]),('drop_both',[0,1,2,3])]:
        ac=float(sum(A[i] for i in selected))
        loss=float(sum(A[i]*sectors[i]['loss'] for i in selected)/ac)
        optimistic=float(sum(A[i]*sectors[i]['best_loss'] for i in selected)/ac)
        policies.append(dict(name=name,sectors=selected,acceptance=ac,loss=loss,
                             optimistic_sectorwise_frame_loss=optimistic))
    out=dict(scope=__doc__,bits=bits,detector_indices=sorted(keep),sectors=sectors,
             policies=policies,rows=rows,seconds=time.perf_counter()-start,
             sector_bit_order_note='Binary labels use ascending retained detector indices in C-order: c272 then c16. Last axis is the least significant bit.')
    path=HERE/('sector_pair_'+'_'.join(map(str,bits))+'.json')
    path.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k!='rows'},indent=2))
