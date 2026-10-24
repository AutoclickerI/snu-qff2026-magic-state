"""Reproduce the rank-five phase-polynomial and its phase-axis fault checks."""
import os, sys, json, itertools, collections
sys.dont_write_bytecode = True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'): os.environ[k]='1'
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]; OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'work/lanes/EVAL'))
from model import Model,Basis,comm
from engine import Engine

def main():
    m=Model((ROOT/'work/lanes/MAIN/spec/v17a.qasm').read_text(),[0,20,7,10,3,22,21]); e=Engine(m)
    b=Basis(); full=Basis()
    for x,z,*_ in m.rots: b.add(x);full.add(x|(z<<m.n))
    axes=[dict(index=i,coordinate=b.express(x),x=hex(x),z=hex(z),coefficient=int(round(-theta/(3.141592653589793/8)))) for i,(x,z,c,theta,ii) in enumerate(m.rots)]
    assert all(comm(a[0],a[1],c[0],c[1])==0 for a,c in itertools.combinations(m.rots,2))
    assert all((z&v).bit_count()%2==0 for x,z,*_ in m.rots for v in b.vecs)
    supp={a['coordinate'] for a in axes}
    # Completeness: the degree <= 3 binary phase signature has rank 25 on
    # the 31 nonzero five-bit axes. Its six-dimensional kernel is exactly
    # the punctured affine functions enumerated below.
    signature=Basis();rows=[]
    for degree in (1,2,3):
        for subset in itertools.combinations(range(5),degree):
            mask=sum(1<<k for k in subset)
            row=sum(int(x&mask==mask)<<(x-1)for x in range(1,32));rows.append(row);signature.add(row)
    affine=Basis()
    for a in range(32):
        for c in range(2):
            word=sum((((a&x).bit_count()%2)^c)<<(x-1)for x in range(1,32))
            assert all((word&row).bit_count()%2==0 for row in rows)
            affine.add(word)
    assert len(signature.vecs)==25 and len(affine.vecs)==6
    phase=[sum(a['coefficient']*((a['coordinate']&y).bit_count()%2) for a in axes)%8 for y in range(32)]
    target=next(x for x in range(1,32) if phase==[(x&y).bit_count()%2 for y in range(32)])
    fault={}
    for c in range(32):
        x=0
        for j,v in enumerate(b.vecs):
            if c>>j&1:x^=v
        d=sum(comm(x,0,q[0],q[1])<<j for j,q in enumerate(m.proj_m))
        sig=sum(comm(x,0,q[0],q[1])<<j for j,q in enumerate(m.sig_e))
        acc,nt=e.ntable(0,d)
        fault[c]=dict(acceptance=acc,loss=0.0 if nt is None else float(nt[sig]))
    allforms=[]
    for a in range(32):
        for c in range(2):
            support=sorted(supp^{x for x in range(1,32) if ((a&x).bit_count()%2)^c})
            row=dict(id=f'f{a:02d}_{c}',affine=[a,c],support=support,T=len(support))
            row['bad_singles']=[x for x in support if fault[x]['loss']>1e-10]
            row['bad_pairs']=[(x,y) for x,y in itertools.combinations(support,2) if fault[x^y]['loss']>1e-10]
            if len(support)==15:
                candidates=[]
                for s in range(32):
                    coeff=[(-1)**((s&x).bit_count()%2) for x in support]
                    if [sum(k*((x&y).bit_count()%2) for x,k in zip(support,coeff))%8 for y in range(32)]==phase:
                        candidates.append(dict(sign_character=s,coefficients=coeff))
                assert candidates
                row['signed_representations']=candidates
                assert not row['bad_singles'] and not row['bad_pairs']
            if len(support)==14: assert len(row['bad_pairs'])==7
            if len(support)==1: assert len(row['bad_singles'])==1
            allforms.append(row)
    out=dict(source='work/lanes/MAIN/spec/v17a.qasm',rank_state=len(b.vecs),rank_pauli=len(full.vecs),commuting=True,
             axes=axes,target=target,phase_values=phase,phase_signature_rank=25,kernel_dimension=6,counts=dict(collections.Counter(f['T'] for f in allforms)),
             forms=allforms,phase_axis_faults=fault)
    (OUT/'enumeration.json').write_text(json.dumps(out,indent=2)+'\n')
    print('rank state/full',out['rank_state'],out['rank_pauli'],'target',target,'counts',out['counts'])
    for f in allforms:
        if f['T']<=15:print(f['id'],f['T'],f['support'],'bad singles/pairs',len(f['bad_singles']),len(f['bad_pairs']))

if __name__=='__main__':main()
