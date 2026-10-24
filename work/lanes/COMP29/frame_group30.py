"""Measured BC preparations with explicit constraints on output Pauli frames.

The fixed 57-CX FRESH resource, placement and R48 remain unchanged. Known X
frames are propagated through the native suffix. Four classical parity checks
constrain the final data frame to a Steane X stabilizer, which commutes with
every decoder syndrome/logical observable. No conditional quantum gate or
nonzero logical frame declaration is used.
"""
from build30 import *
from model import SUPPORTS

def build_group(base,qs):
    c=C.clone(base);chosen=set(qs);init={int(q):int(t) for q,t in c['meta']['init_times'].items()};nbit=C.bit(c);sources={};uu=[];tt=[];removed=[]
    for u,t in zip(c['u'],c['t']):
        q=u.qs[0]
        if len(u.qs)==1 and q in chosen and t==init[q]:
            assert u.name in ('RESET','MEASURE'),(q,u.lines)
            if u.name=='RESET':
                assert q in (6,13,19)
                assert not any(q in v.qs and vt==t-1 for v,vt in zip(c['u'],c['t'])),('no reset slot',q,t)
                uu.append(C.Unit([f'reset q[{q}];']));tt.append(t-1)
                b=nbit;nbit+=1;u=C.Unit([f'measure q[{q}] -> c[{b}];'])
            else:
                b=int(re.search(r'c\[(\d+)\]',u.lines[0])[1]);line=f'// DETECTOR c[{b}]';assert line in c['tail']
                assert sum(b in set(map(int,re.findall(r'c\[(\d+)\]',l))) for l in c['tail'])==1
                c['tail'].remove(line);removed.append(b)
            sources[b]=q
        uu.append(u);tt.append(t)
    assert set(sources.values())==chosen
    c['u']=uu;c['t']=tt;c=finish(c)
    frames={q:[set(),set()] for q in range(36)};corr={}
    for u in c['u']:
        b=int(re.search(r'c\[(\d+)\]',' '.join(u.lines))[1]) if u.name in ('MX','MEASURE') else None
        if b in sources:frames[sources[b]]=[{b},set()];continue
        if u.name in ('RESET','RX'):frames[u.qs[0]]=[set(),set()]
        elif u.name=='CX':
            a,z=map(int,C.S.QRE.findall(u.lines[0]));frames[z][0]^=frames[a][0];frames[a][1]^=frames[z][1]
        elif u.name in ('MX','MEASURE'):corr[b]=frames[u.qs[0]][u.name=='MX'].copy()
        elif u.name=='H':frames[u.qs[0]].reverse()
        elif u.name in ('S','SDG'):frames[u.qs[0]][1]^=frames[u.qs[0]][0]
        elif u.name in ('T','TDG'):assert not frames[u.qs[0]][0],('non-Clifford frame',u.lines)
        else:assert not any(any(frames[q]) for q in u.qs)
    data=c['meta']['data_qubits'];assert all(not frames[q][1] for q in data)
    constraints=[]
    for support in list(SUPPORTS)+[set(range(7))]:
        row=set()
        for i in support:row^=frames[data[i]][0]
        constraints.append(sum(1<<b for b in row))
    basis={}
    for row in constraints:
        for pivot,bv in sorted(basis.items(),reverse=True):
            if row>>pivot&1:row^=bv
        if row:basis[row.bit_length()-1]=row
    rows=list(basis.values())
    for i,line in enumerate(c['tail']):
        assert line.startswith('// DETECTOR')
        bs=set(map(int,re.findall(r'c\[(\d+)\]',line)));extra=set()
        for b in bs:extra^=corr.get(b,set())
        c['tail'][i]='// DETECTOR '+' '.join(f'c[{b}]' for b in sorted(bs^extra))
    for row in rows:c['tail'].append('// DETECTOR '+' '.join(f'c[{b}]' for b in sorted(sources) if row>>b&1))
    stab={0}
    for support in SUPPORTS:
        v=sum(1<<i for i in support);stab|={x^v for x in list(stab)}
    records=sorted(sources);accepted=0
    for assignment in range(1<<len(records)):
        bits=sum(((assignment>>i)&1)<<b for i,b in enumerate(records))
        if any((row&bits).bit_count()%2 for row in rows):continue
        mask=sum(((sum((bits>>b)&1 for b in frames[q][0]))%2)<<i for i,q in enumerate(data));assert mask in stab,(assignment,mask)
        accepted+=1
    c['meta']['frame_preparations']=dict(qubits=sorted(chosen),records=sources,removed_singleton_checks=removed,frame_constraints=[sorted(b for b in records if row>>b&1) for row in rows],data_x_frames=[sorted(frames[q][0]) for q in data],verified_record_assignments=1<<len(records),accepted_record_assignments=accepted,output_frame='Steane X stabilizer')
    return finish(c)

if __name__=='__main__':
    base=C.read(H/'f_timing_mz_5_12');qs=[6,13,11,23,27,12,25,19,5,29]
    c=build_group(base,qs);name='f_frame_group';r=save(c,name,['f_timing_mz_5_12','measured BC initializations with stabilizer-frame constraints']);r.update(screen(name));(H/'v30_frame_group.json').write_text(json.dumps([r],indent=2));print(json.dumps(r),flush=True)
