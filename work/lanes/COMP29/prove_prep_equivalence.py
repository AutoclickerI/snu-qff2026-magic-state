"""Certify both isolated repeated-preparation checks, without gain additivity."""
from common import *
from tprep.noise import STANDARD
import math

def signature(c,edits):
    c=C.clone(c)
    for q,start,end,kind,edit in [(19,1,3,'MX','q19check'),(13,37,40,'MEASURE','zero_13_39')]:
        seq=[(i,u,t) for i,(u,t) in enumerate(zip(c['u'],c['t'])) if q in u.qs and start<=t<=end]
        has=edit in edits
        expected=([(1,'RX'),(2,'MX'),(3,'MX')] if has else [(2,'RX'),(3,'MX')]) if q==19 else ([(37,'RESET'),(39,'MEASURE'),(40,'MEASURE')] if has else [(37,'RESET'),(40,'MEASURE')])
        assert [(t,u.name) for i,u,t in seq]==expected,(q,seq,expected)
        assert all(u.qs==(q,) for i,u,t in seq)
        for i,u,t in seq[1:]:
            b=int(re.search(r'c\[(\d+)\]',' '.join(u.lines))[1]);line=f'// DETECTOR c[{b}]'
            assert line in c['tail']
            assert sum(b in set(map(int,re.findall(r'c\[(\d+)\]',l))) for l in c['tail'])==1
        if has:
            i,u,t=seq[1];b=int(re.search(r'c\[(\d+)\]',' '.join(u.lines))[1])
            if q==19:c['t'][seq[0][0]]=2
            del c['u'][i];del c['t'][i];c['tail'].remove(f'// DETECTOR c[{b}]')
    order=sorted(range(len(c['u'])),key=lambda i:(c['t'][i],c['u'][i].qs,c['u'][i].name));bitmap={}
    for i in order:
        for line in c['u'][i].lines:
            if line.startswith('measure'):
                b=int(re.search(r'c\[(\d+)\]',line)[1]);assert b not in bitmap;bitmap[b]=len(bitmap)
    rename=lambda s:re.sub(r'c\[(\d+)\]',lambda m:f'c[{bitmap[int(m[1])]}]',s)
    ops=[(c['t'][i],tuple(rename(s) for s in c['u'][i].lines)) for i in order]
    assert all(l.startswith('// DETECTOR') for l in c['tail'])
    dets=[tuple(sorted(bitmap[int(b)] for b in re.findall(r'c\[(\d+)\]',l))) for l in c['tail']]
    return hashlib.sha256(json.dumps(dict(ops=ops,detectors=sorted(dets),data=c['meta']['data_qubits'])).encode()).hexdigest()

if __name__=='__main__':
    rows=json.loads((H/'v30_manifest.json').read_text());groups={};p=.001
    alpha19=1-5*p/3+4*p*p/3
    old13=(1+(1-2*p)**2*(1-4*p/3)**2)/2
    new13=(1+(1-2*p)**2*(1-4*p/3))/2*(1+(1-4*p/3)*(1-2*p))/2
    alpha13=new13/old13
    for row in rows:
        edits=row['edits'];key=tuple(e for e in edits if e not in ('q19check','zero_13_39'))
        r=dict(stem=row['stem'],sha256=row['sha256'],signature=signature(C.read(H/row['stem']),edits),alpha=(alpha19 if 'q19check' in edits else 1)*(alpha13 if 'zero_13_39' in edits else 1),A1_extra=(5/3 if 'q19check' in edits else 0)+(1 if 'zero_13_39' in edits else 0),canonical=len(edits)==len(key))
        groups.setdefault(key,[]).append(r)
    for group in groups.values():
        assert len(group)==4 and len({r['signature'] for r in group})==1
        base=next(r for r in group if r['canonical']);bs=json.loads((H/(base['stem']+'.screen.json')).read_text())
        for r in group:
            s=json.loads((H/(r['stem']+'.screen.json')).read_text())
            assert abs(s['total']-bs['total'])<1e-14
            assert abs(math.log(bs['exp_minus_A1']/s['exp_minus_A1'])-.001*r['A1_extra'])<1e-12
    result=dict(groups=list(groups.values()),classes=len(groups),circuits=len(rows),data_qubits=C.D,noise_parameters={k:getattr(STANDARD,k) for k in ('native_x','meas','meas_after','reset','idle')},alpha19=alpha19,alpha13=alpha13,proof='Both isolated segments start with a reset and end in a required zero measurement before any CX. The final measured state is exactly the same |+> (q19) or |0> (q13), followed by identical post-measurement depolarization. Earlier segment faults affect only an independent scalar acceptance. The rest of the native circuit and detector predicate is identical after deleting extra checks and renaming records. A and accepted N acquire the same scalar, leaving conditional N/A identical at every order.',q13_alpha_formula='[(1+(1-2p)^2(1-4p/3))/2]*[(1+(1-4p/3)(1-2p))/2] / [(1+(1-2p)^2(1-4p/3)^2)/2]')
    (H/'prep_equivalence.json').write_text(json.dumps(result,indent=2)+'\n');print(dict(classes=len(groups),circuits=len(rows),alpha19=alpha19,alpha13=alpha13))
