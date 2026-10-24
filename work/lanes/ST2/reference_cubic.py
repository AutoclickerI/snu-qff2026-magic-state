"""Large-detector cubic diagnostic using an equivalent reference-only ordering.

Repeating the last record twice contributes zero parity and lets the parser
place all detector rows at the same record. Submission artifacts stay intact.
We verify every channel/rotation/decoder and the complete fault-mask permutation.
"""
import sys,json,re,time,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));import directed as d
import numpy as np

def main():
    p=Path(sys.argv[1]);text=p.with_suffix('.qasm').read_text();md=json.loads(p.with_suffix('.json').read_text());ev=d.C.exact2.Eval(text,md['data_qubits']);e=ev.e
    lines=text.splitlines();pos=[i for i,l in enumerate(lines) if l.startswith('// DETECTOR')];rows=[lines[i] for i in pos]
    native=[int(re.search(r'DETECTOR line (\d+)',lab)[1])-1 for lab in ev.m.labels if lab.startswith('DETECTOR line ')]
    active=[i for i,x in enumerate(e.projs) if x[:2]!=(0,0)];inactive=[i for i in range(len(rows)) if i not in active];early=min(16,len(inactive));perm=inactive[:early]+active+inactive[early:]
    assert early+len(active)<53
    last=int(re.findall(r'measure q\[\d+\] -> c\[(\d+)\];',text)[-1])
    for i,old in enumerate(perm):lines[pos[i]]=rows[native[old]]+f' c[{last}] c[{last}]'
    newtext='\n'.join(lines)+'\n';z=d.C.exact2.Eval(newtext,md['data_qubits'])
    assert len(ev.m.faults)==len(z.m.faults)
    assert [r[:4] for r in ev.m.rots]==[r[:4] for r in z.m.rots] and ev.m.Q==z.m.Q and ev.m.cz==z.m.cz and ev.m.cxz==z.m.cxz
    for a,b in zip(ev.m.faults,z.m.faults):
        assert all(a[k]==b[k] for k in ['s','e','p','chan'])
        assert b['d']==sum(((a['d']>>old)&1)<<new for new,old in enumerate(perm))
    assert z.e.projs==[e.projs[i] for i in perm]
    r=d.mom.evaluate(z);r['proof']=dict(detectors=len(rows),active=len(active),permutation=perm,last_record_paired=last,all_fault_signatures_verified=True,decoder_rotation_and_noise_unchanged=True,reference_only=True,original_sha256=hashlib.sha256(text.encode()).hexdigest())
    r['method']='categorical Fourier cubic with verified detector permutation'
    p.with_suffix('.cubic.json').write_text(json.dumps(r,indent=2));print('CUBIC',r['total'],flush=True)
    # Independent enumeration: only triples with impossible exact parity are
    # pruned; all surviving arithmetic is exact2._triple_chunk unchanged.
    sy=d.C.setup_syndromes(z);pairs=[(a,b) for a in range(len(sy)) for b in range(a,len(sy)) if sy[a]==sy[b]]
    d.C.exact2.G.update(ev=z,pairs=pairs,third=True,SA=float(z.fp@z.a_single),Pch=np.bincount(z.fch,weights=z.fp))
    t=time.monotonic();p2,_,_,_,bc=d.C.exact2._pair_chunk((0,len(pairs),1))
    tri,_=d.C.fast_third.third_order(z,1);r['pruned_exact2']=dict(second=p2,third=tri+bc,total=p2+tri+bc,seconds=time.monotonic()-t)
    assert abs(r['total']-r['pruned_exact2']['total'])<1e-14,(r['total'],r['pruned_exact2'])
    p.with_suffix('.cubic.json').write_text(json.dumps(r,indent=2));print(json.dumps(r),flush=True)
if __name__=='__main__':main()
