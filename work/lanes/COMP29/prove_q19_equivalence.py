"""Certify the q19 repeated-init check as a conditional-noise identity.

Before q19's first CX, an already checked native MX outputs the same post-MX
depolarized |+> in both versions. The inserted checked MX changes only the
independent acceptance factor, not any conditional downstream state/channel.
"""
from common import *
import math
from tprep.noise import STANDARD

def context_signature(c,strip):
    c=C.clone(c)
    assert c['meta']['data_qubits']==C.D
    seq=[(i,u,t) for i,(u,t) in enumerate(zip(c['u'],c['t'])) if 19 in u.qs and t<4]
    expected=[(1,'RX'),(2,'MX'),(3,'MX')] if strip else [(2,'RX'),(3,'MX')]
    assert [(t,u.name) for i,u,t in seq]==expected
    assert all(u.qs==(19,) for i,u,t in seq)
    lastbit=int(re.findall(r'c\[(\d+)\]',' '.join(seq[-1][1].lines))[0])
    assert f'// DETECTOR c[{lastbit}]' in c['tail']
    assert sum(lastbit in set(map(int,re.findall(r'c\[(\d+)\]',l))) for l in c['tail'])==1
    if strip:
        i,u,t=seq[1];b=int(re.findall(r'c\[(\d+)\]',' '.join(u.lines))[0])
        assert f'// DETECTOR c[{b}]' in c['tail']
        assert sum(b in set(map(int,re.findall(r'c\[(\d+)\]',l))) for l in c['tail'])==1
        c['t'][seq[0][0]]=2;del c['u'][i];del c['t'][i];c['tail'].remove(f'// DETECTOR c[{b}]')
    order=sorted(range(len(c['u'])),key=lambda i:(c['t'][i],c['u'][i].qs,c['u'][i].name))
    bitmap={}
    for i in order:
        for s in c['u'][i].lines:
            if s.startswith('measure'):
                b=int(re.search(r'c\[(\d+)\]',s)[1]);assert b not in bitmap;bitmap[b]=len(bitmap)
    rename=lambda s:re.sub(r'c\[(\d+)\]',lambda m:f'c[{bitmap[int(m[1])]}]',s)
    ops=[(c['t'][i],tuple(rename(s) for s in c['u'][i].lines)) for i in order]
    dets=[]
    for l in c['tail']:
        assert l.startswith('// DETECTOR'),l
        dets.append(tuple(sorted(bitmap[int(b)] for b in re.findall(r'c\[(\d+)\]',l))))
    return hashlib.sha256(json.dumps(dict(ops=ops,detectors=sorted(dets),data_qubits=c['meta']['data_qubits'])).encode()).hexdigest()

if __name__=='__main__':
    assert STANDARD.native_x and STANDARD.meas==1 and STANDARD.meas_after==1 and STANDARD.reset==1
    rows=json.loads((H/'v30_manifest.json').read_text());lookup={tuple(r['edits']):r for r in rows};proofs=[]
    for r in rows:
        if 'q19check' not in r['edits']:continue
        rep=lookup[tuple(k for k in r['edits'] if k!='q19check')]
        left=context_signature(C.read(H/r['stem']),True);right=context_signature(C.read(H/rep['stem']),False)
        assert left==right,(r['stem'],rep['stem'])
        a=json.loads((H/(r['stem']+'.screen.json')).read_text());b=json.loads((H/(rep['stem']+'.screen.json')).read_text())
        assert abs(a['total']-b['total'])<1e-14
        assert abs(math.log(b['exp_minus_A1']/a['exp_minus_A1'])-5/3*1e-3)<1e-12
        proofs.append(dict(stem=r['stem'],representative=rep['stem'],context_sha256=left,sha256=r['sha256'],representative_sha256=rep['sha256'],third_delta=a['total']-b['total'],A1_delta=math.log(b['exp_minus_A1']/a['exp_minus_A1'])))
    result=dict(pairs=len(proofs),proof='All other native operations, times and detector parities match after classical-record renaming and removal of the isolated q19 prep/check. The existing checked MX at t3 produces the same post-measurement-depolarized |+> density matrix in both circuits before the first CX at t4. Noise channels are independent. Thus A_new=alpha*A_old and N_new=alpha*N_old at all orders, and conditional N/A is identical.',alpha_at_p001=1-5/3*.001+4/3*.001**2,alpha_polynomial=[1,-5/3,4/3],noise_source='upstream/snu-qff2026-problem/tprep/noise.py STANDARD native RX/MX; before-MX Z_ERROR(p), after-MX DEPOLARIZE1(p)',cases=proofs)
    result['noise_parameters']={k:getattr(STANDARD,k) for k in ('native_x','meas','meas_after','reset')}
    result['data_qubits']=C.D
    (H/'q19_equivalence.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='cases'}))
