"""Compare the sparse frontend with the actual judge-based EVAL model."""
from common import *
import collections,random
sys.path.insert(0,str(H/'sparse34'))
import sparse_walsh as w
for name in sys.argv[1:]:
    p=H/name;m,e,*_=w.prepare(p,False);ev=C.exact2.Eval(p.with_suffix('.qasm').read_text(),json.loads(p.with_suffix('.json').read_text())['data_qubits'])
    assert [r[:4] for r in m.rots]==[r[:4] for r in ev.m.rots]
    assert m.Q==ev.m.Q and m.cz==ev.m.cz and m.cxz==ev.m.cxz
    positions=collections.defaultdict(list)
    for j,pm in enumerate(m.proj_m):positions[pm].append(j)
    permutation=[positions[pm].pop() for pm in ev.m.proj_m]
    def convert(d):return sum(((d>>j)&1)<<i for i,j in enumerate(permutation))
    def channels(model,translate=False):
        groups=collections.defaultdict(list)
        for f in model.faults:groups[f['chan']].append((int(f['s']),convert(int(f['d'])) if translate else int(f['d']),int(f['e']),round(float(f['p']),17)))
        return collections.Counter(tuple(sorted(fs)) for fs in groups.values())
    assert channels(m,True)==channels(ev.m)
    rng=random.Random(34029);active=[i for i,pm in enumerate(e.projs) if pm[:2]!=(0,0)];maximum=0.
    for trial in range(32):
        s=0 if trial==0 else rng.randrange(1<<len(m.rots));d=sum(rng.randrange(2)<<i for i in active) if trial else 0
        a,n=e.ntable(s,d);b,nn=ev.e.ntable(s,convert(d))
        maximum=max(maximum,abs(a-b));assert abs(a-b)<1e-12
        if n is not None and nn is not None:
            err=float(abs(n-nn).max());maximum=max(maximum,err);assert err<1e-12
        else:assert (n is None)==(nn is None)
    out=dict(source_sha256=hashlib.sha256(p.with_suffix('.qasm').read_bytes()).hexdigest(),rotation_and_decoder_match=True,channel_multiset_match=True,detector_permutation=permutation,channels=len(m.chans),faults=len(m.faults),independent_quantum_table_cases=32,max_table_error=maximum)
    p.with_suffix('.model_validation.json').write_text(json.dumps(out,indent=2)+'\n');print(name,{k:v for k,v in out.items() if k!='detector_permutation'},flush=True)
