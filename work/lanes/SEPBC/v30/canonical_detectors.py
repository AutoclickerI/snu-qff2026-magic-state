"""Equivalent detector order that keeps all accepted masks exactly representable.

Unchanged exact2 constructs some D arrays with inferred NumPy dtype. At >=64
detectors, mixtures of small integers and 2**63 can become float64. Putting
the nontrivial quantum projectors first confines every possibly accepted D to
the low k bits (k<=5 here). Every higher bit is an identity-projector rejection.
The evaluator source and all gate/noise channels remain unchanged.
"""
import sys,json,hashlib,re
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[3]
sys.path.insert(0,str(ROOT/'work/lanes/EVAL'))
import exact2

def canonical(stem):
    text=stem.with_suffix('.qasm').read_text();md=json.loads(stem.with_suffix('.json').read_text())
    n=sum(l.startswith('// DETECTOR') for l in text.splitlines())
    if n<64:return stem,dict(required=False,detectors=n)
    if n>64:raise ValueError(f'{n} independent detector records exceed the unchanged engine int64 input scope; no reference score claimed')
    ev=exact2.Eval(text,md['data_qubits']);e=ev.e
    active=[i for i,p in enumerate(e.projs) if p[:2]!=(0,0)]
    inactive=[i for i in range(n) if i not in active]
    assert len(active)<53,'cannot bound accepted signatures in float64 exact-integer range'
    assert all(e.projs[i]==(0,0,1+0j) and e.v[i]==0 for i in inactive),'nontrivial deterministic sign'
    perm=active+inactive;lines=text.splitlines();positions=[i for i,l in enumerate(lines) if l.startswith('// DETECTOR')];dets=[lines[i] for i in positions]
    # convert() places each detector immediately after its latest measurement,
    # so merely sorting comments cannot reorder chronological detectors.
    # XOR each other row with one already-required, final identity check.
    # This invertible row operation gives every row the same final record.
    native_to_comment=[int(re.search(r'DETECTOR line (\d+)',label)[1])-1 for label in ev.m.labels if label.startswith('DETECTOR line ')]
    assert len(native_to_comment)==n
    bits=[set(map(int,re.findall(r'c\[(\d+)\]',line))) for line in dets]
    lastbit=int(re.findall(r'measure q\[\d+\] -> c\[(\d+)\];',text)[-1])
    contains=[i for i,bs in enumerate(bits) if lastbit in bs]
    assert len(contains)==1,'need a uniquely referenced last measurement as a detector-basis anchor'
    anchor=native_to_comment.index(contains[0]);assert anchor in inactive
    anchor_bits=bits[contains[0]]
    newrows=[]
    for i in perm:
        row=bits[native_to_comment[i]] if i==anchor else bits[native_to_comment[i]]^anchor_bits
        assert lastbit in row
        newrows.append('// DETECTOR '+' '.join(f'c[{b}]' for b in sorted(row)))
    for j,i in enumerate(positions):lines[i]=newrows[j]
    rewritten='\n'.join(lines)+'\n';other=exact2.Eval(rewritten,md['data_qubits'])
    assert newrows[perm.index(anchor)]==dets[contains[0]] or set(map(int,re.findall(r'c\[(\d+)\]',newrows[perm.index(anchor)])))==anchor_bits
    assert [r[:4] for r in ev.m.rots]==[r[:4] for r in other.m.rots] and ev.m.Q==other.m.Q and ev.m.cz==other.m.cz and ev.m.cxz==other.m.cxz
    assert len(ev.m.faults)==len(other.m.faults)
    for f,g in zip(ev.m.faults,other.m.faults):
        assert all(f[k]==g[k] for k in ('s','e','p','chan'))
        av=(f['d']>>anchor)&1
        assert g['d']==sum((((f['d']>>old)&1)^(av if old!=anchor else 0))<<new for new,old in enumerate(perm))
    assert all(p==(0,0,1+0j) and other.e.v[i]==0 for i,p in enumerate(other.e.projs) if i>=len(active))
    out=stem.with_name(stem.name+'_detorder')
    out.with_suffix('.qasm').write_text(rewritten);out.with_suffix('.json').write_text(json.dumps(md,indent=2)+'\n')
    proof=dict(required=True,detectors=n,active_projectors=len(active),accepted_mask_upper_bound=2**len(active)-1,permutation=perm,anchor_native_detector=anchor,anchor_record=lastbit,detector_conjunction_preserved=True,noise_signatures_matched=True,rotation_and_decoder_match=True,source_sha256=hashlib.sha256(text.encode()).hexdigest(),rewritten_sha256=hashlib.sha256(rewritten.encode()).hexdigest(),numeric_argument='Invertible detector-row XOR preserves the entire acceptance predicate. All accepted transformed masks are below 2**k and exactly representable. Every larger mask has a rejecting identity-projector bit; float rounding or signed overflow retains a high bit, so it still rejects.')
    stem.with_suffix('.detorder.validation.json').write_text(json.dumps(proof,indent=2)+'\n')
    return out,proof
