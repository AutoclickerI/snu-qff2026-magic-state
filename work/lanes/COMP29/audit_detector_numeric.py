"""Adversarial scalar/batch audit for the unchanged engine mask conversion."""
from common import *
import random,warnings,numpy as np
def audit(name):
    p=H/name;ev=C.exact2.Eval(p.with_suffix('.qasm').read_text(),json.loads(p.with_suffix('.json').read_text())['data_qubits']);e=ev.e
    active=[i for i,x in enumerate(e.projs) if x[:2]!=(0,0)];inactive=[i for i in range(len(e.projs)) if i not in active]
    ds=[]
    for mask in range(1<<len(active)):
        d=sum(((mask>>i)&1)<<b for i,b in enumerate(active));ds += [d,d^(1<<inactive[0]),d^(1<<inactive[-1])]
    ds += [2**63-1,2**63,2**63+1,2**64-1]
    rng=random.Random(3001);ss=[rng.randrange(1<<len(ev.m.rots)) for _ in ds]
    # Match exact2._triple_chunk's inferred array, including mixed large masks.
    D=np.array(ds);S=np.array(ss)
    with warnings.catch_warnings(record=True) as ww:
        warnings.simplefilter('always');A,N=e.batch_n(S,D)
    da=dn=0.;mismatches=0
    for i,(s,d) in enumerate(zip(ss,ds)):
        a,n=e.ntable(s,d);n=np.zeros(1024) if n is None else n
        aa=abs(a-A[i]);nn=float(np.max(np.abs(n-N[i])));da=max(da,aa);dn=max(dn,nn);mismatches+=max(aa,nn)>1e-12
    return dict(stem=name,detectors=len(e.projs),active=active,cases=len(ds),inferred_dtype=str(D.dtype),warnings=[str(w.message) for w in ww],max_acceptance_error=float(da),max_loss_table_error=float(dn),mismatches=int(mismatches))
if __name__=='__main__':
    rows=[audit('f_timing_mz_5_12'),audit('f_timing_mz_5_12_detorder')]
    assert rows[0]['mismatches']>0 and rows[1]['mismatches']==0,rows
    (H/'detector_numeric_audit.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows,indent=2))
