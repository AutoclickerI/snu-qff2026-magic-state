"""Accepted-event gauge for measured initializers and an open interior flag.

XORing any function of rejected deterministic flags into other detector or
decoder signatures leaves every accepted-event numerator and denominator
unchanged. Normalize initializer X-error columns this way, then keep interior
measurement flags explicitly in the response boundary. No detector is dropped.
"""
from core35 import *
from boundary import audit,pack,unpack
import numpy as np

def gauge(ev,c):
    m=ev.m;e=ev.e;init=init_indices(c);lines=[s for s in c['tail'] if s.startswith('// DETECTOR')];assert m.n_post==0
    detmap={};ordinal=0
    for ins in m.prog:
        if ins.name=='DETECTOR':
            label=m.labels[ins.line_no-1];match=re.fullmatch(r'DETECTOR line (\d+)',label);assert match,label
            detmap[int(match[1])-1]=ordinal;ordinal+=1
    flags=[]
    for i,u in enumerate(c['us']):
        if u.name!='MEASURE' or u.qs[0] not in BC:continue
        q=u.qs[0];t=c['ts'][i]
        if not c['ts'][init[q]]<=t<c['md']['R']:continue
        b=bit(u);hits=[j for j,line in enumerate(lines) if list(map(int,re.findall(r'c\[(\d+)\]',line)))==[b]]
        if not hits:continue
        assert len(hits)==1;j=detmap[hits[0]]
        assert e.projs[j]==(0,0,1) and e.v[j]==0,('nonidentity flag',j,e.projs[j])
        anchors=[]
        for f in m.faults:
            ch=m.chans[f['chan']];st=m.steps[ch['ins']]
            if ch['kind']=='flip' and ch['qubits']==[q] and st and min(tt for qq,tt in st)==t and f['d']>>j&1:anchors.append(f)
        assert anchors and len({(f['s'],f['d'],f['e']) for f in anchors})==1,(q,t,j,[(f['pauli'],f['s'],f['d'],f['e']) for f in anchors])
        f=anchors[0];assert f['s']==0
        flags.append(dict(detector=j,q=q,time=t,interior=i!=init[q],d=f['d'],e=f['e']))
    mask=sum(1<<r['detector'] for r in flags);piv={}
    for row in flags:
        v=row['d']&mask;out=((row['d']&~mask)<<10)|row['e']
        while v:
            k=v.bit_length()-1
            if k not in piv:piv[k]=(v,out);break
            vv,oo=piv[k];v^=vv;out^=oo
        assert v or not out
    assert len(piv)==len(flags)
    for f in m.faults:
        v=f['d']&mask;out=0
        while v:
            k=v.bit_length()-1;vv,oo=piv[k];v^=vv;out^=oo
        f['d']^=out>>10;f['e']^=out&1023
    # The complete Engine is unchanged: all changed terms carry a flag whose
    # ideal projector is identity and whose accepted value must be zero.
    ev.fs=[f['s'] for f in m.faults];ev.fd=[f['d'] for f in m.faults];ev.fe=np.array([f['e'] for f in m.faults],dtype=np.int64)
    groups=collections.defaultdict(list)
    for i,f in enumerate(m.faults):groups[f['s'],f['d']].append(i)
    ev.gkeys=list(groups);ev.gmem=[np.array(groups[k]) for k in ev.gkeys];ev.ga=np.array([ev.a_single[ix[0]] for ix in ev.gmem])
    return flags

def setup(stem):
    ev,b,rec=audit(Path(stem));c=load(stem);flags=gauge(ev,c);m=ev.m;nd=rec['nd'];boundary=rec['boundary'];region=rec['region_qubits']
    for row in flags:
        if row['interior']:b.add(pack((0,1<<row['detector'],0),nd))
    assert len(b.vecs)<=16,('cache rank limit',len(b.vecs))
    ks=[(0,0,0)]
    for a in [unpack(v,nd) for v in b.vecs]:ks += [tuple(x^y for x,y in zip(k,a)) for k in ks[:]]
    init={int(q):int(t) for q,t in c['md']['init_times'].items()};members=collections.defaultdict(list)
    for i,f in enumerate(m.faults):members[f['chan']].append(i)
    prep={};external=[]
    for ch,ix in members.items():
        cc=m.chans[ch];st=m.steps[cc['ins']];tt=min(t for q,t in st) if st else -1
        eligible=set(cc['qubits'])<=set(region) and tt<boundary and all(tt>=init[q] for q in cc['qubits'])
        if cc['gap'] is not None:
            q,first,n=cc['gap'];eligible=eligible and first>init[q] and first+n<=boundary
        coords=[b.express(pack((m.faults[i]['s'],m.faults[i]['d'],m.faults[i]['e']),nd)) for i in ix]
        if eligible and all(k is not None for k in coords):prep[ch]=list(zip(ix,coords))
        else:external.extend(ix)
    extcanon=[sorted((m.faults[i]['s'],m.faults[i]['d'],m.faults[i]['e'],m.faults[i]['p']) for i in ix) for ch,ix in members.items() if ch not in prep]
    ideal=(ev.e.rot,ev.e.projs,ev.e.Qs,ev.e.v.tolist(),ev.e.beta.tolist(),ks)
    hh=hashlib.sha256(repr((sorted(extcanon),ideal)).encode()).hexdigest()
    ev.boundary35_flags=flags
    return ev,b,ks,prep,external,hh

def region(stem):
    ev,b,ks,prep,ext,hh=setup(Path(stem))
    return PreparedRegion(hh,tuple(tuple((int(k),float(ev.fp[i])) for i,k in items) for items in prep.values()),len(ks)),ev

def prepare_candidate(stem):
    """Extract a region for the v35 accepted-event gauge cache."""
    return region(stem)[0]
