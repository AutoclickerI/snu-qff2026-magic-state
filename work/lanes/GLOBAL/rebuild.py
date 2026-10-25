"""Build the supplied R45/R46 layouts against the real retained-prefix releases."""
import copy,json,re,sys
from pathlib import Path
from qedit import load,QRE,CRE
from borrow import HERE,save

def prefix(label):
    lay=json.loads((HERE/'layouts'/f'{label}.json').read_text())
    route_label=label.split('_R')[0]
    fast=label=='r46fast44'
    if fast:route_label='r46_2'
    swap=label.startswith('r46swap')
    if swap:route_label='r46_2'
    orig=load(str(HERE/'builds/v36h'));c=copy.deepcopy(orig);c.segs=[[] for _ in range(lay['R']+3)]
    futurebits={295,298,299,301,303,304}
    for t,ss in enumerate(orig.segs):
        for g in ss:
            qs=tuple(map(int,QRE.findall(g[0])));bits=set(map(int,CRE.findall(' '.join(g))))
            keep=t<=32 and not bits&futurebits
            if t==32 and (g[0] in ['reset q[9];','reset q[21];','reset q[25];'] or qs in [(6,7),(13,14)]):keep=False
            if t==33 and (qs in [(1,7),(2,3),(4,10),(15,16),(13,),(5,),(11,)] or g[0]=='reset q[22];'):keep=True
            if t==34 and qs in [(10,4),(2,1),(15,),(22,16)]:keep=True
            if t==35 and qs in [(4,),(2,),(16,22)]:keep=True
            if t==36 and qs==(22,16):keep=True
            if t==37 and (55 in bits or g[0]=='tdg q[22];'):keep=True
            if keep:c.segs[t].append(g)
            if 64 in bits:c.segs[35].append(g)
            if 12 in bits:c.segs[33].append(g)
            if t==36 and qs==(14,20):c.segs[32].append(g)
    retained={int(b) for ss in c.segs for g in ss for b in CRE.findall(' '.join(g))}
    c.dets=[d for d in orig.dets if set(map(int,CRE.findall(d)))<=retained]
    if swap:
        for t,first in [(33,'reset q[22];'),(34,'cx q[22],q[16];'),(35,'cx q[16],q[22];'),(36,'cx q[22],q[16];'),(37,'tdg q[22];'),(34,'cx q[10],q[4];'),(31,'cx q[11],q[10];'),(32,'cx q[11],q[10];')]:
            g=next(g for g in c.segs[t] if g[0]==first);c.segs[t].remove(g)
        g=next(g for g in c.segs[37] if any('-> c[55];' in l for l in g));c.segs[37].remove(g);c.dets.remove('// DETECTOR c[55]')
        c.segs[34].append(['tdg q[16];'])
        for bit,old,new in [(8,35,34),(297,33,31)]:
            g=next(g for g in c.segs[old] if any(f'-> c[{bit}];' in l for l in g));c.segs[old].remove(g);c.segs[new].append(g)
    if fast:
        def rm(t,first):
            g=next(g for g in c.segs[t] if g[0]==first);c.segs[t].remove(g);return g
        def move(t,tt,first):c.segs[tt].append(rm(t,first))
        move(32,31,'cx q[4],q[5];')
        rm(32,'cx q[11],q[10];')
        move(33,32,'cx q[4],q[10];')
        rm(34,'cx q[10],q[4];')
        for bit,old,new in [(8,35,33),(297,33,32),(293,31,29),(312,30,28)]:
            g=next(g for g in c.segs[old] if any(f'-> c[{bit}];' in l for l in g));c.segs[old].remove(g);c.segs[new].append(g)
        move(30,28,'cx q[25],q[19];')
        for t in [29,30]:rm(t,'cx q[20],q[26];')
        for t in [28,29]:rm(t,'cx q[28],q[22];')
        g=next(g for g in c.segs[37] if any('-> c[55];' in l for l in g));c.segs[37].remove(g);c.dets.remove('// DETECTOR c[55]')
    bit=max(retained)+1
    def put(t,g):c.segs[t].append(g)
    def mz(t,q):
        nonlocal bit
        put(t,[f'measure q[{q}] -> c[{bit}];']);c.dets.append(f'// DETECTOR c[{bit}]');bit+=1
    routes={
        'r45_2':[(33,0,6),(33,20,19),(36,7,1),(38,1,2),(34,3,9),(36,9,15),(38,15,16),(35,8,14),(37,14,20)],
        'r46_2':[(33,0,6),(34,7,13),(36,13,19),(37,3,2),(33,8,9),(35,9,15),(38,15,16)],
    }[route_label]
    if fast:routes=[(37,a,b) if (a,b)==(15,16) else (t,a,b) for t,a,b in routes]
    if swap:routes=[(37,15,21) if (a,b)==(15,16) else (t,a,b) for t,a,b in routes]+[(39,21,22)]
    for t,a,b in routes:
        prev=[(tt,g) for tt,ss in enumerate(c.segs[:t]) for g in ss if b in map(int,QRE.findall(g[0]))]
        last,gg=max(prev,key=lambda z:z[0]) if prev else (-1,[])
        assert last<t,(t,a,b,last)
        if not (last==t-1 and gg[0].startswith('measure')) and not (fast and t==37 and b==16):put(t-1,[f'reset q[{b}];'])
        put(t,[f'cx q[{a}],q[{b}];']);put(t+1,[f'cx q[{b}],q[{a}];']);mz(t+2,a)
    put(42,['tdg q[10];'])
    put(35 if route_label=='r45_2' else 43,[f'tdg q[{lay["D"][1]}];'])
    if fast:
        for q in [3,15]:
            g=next(g for g in c.segs[39] if g[0].startswith(f'measure q[{q}]'))
            b=int(CRE.findall(' '.join(g))[0]);c.segs[39].remove(g);c.dets.remove(f'// DETECTOR c[{b}]')
    if swap and label.endswith('drop'):
        g=next(g for g in c.segs[41] if g[0].startswith('measure q[21]'))
        b=int(CRE.findall(' '.join(g))[0]);c.segs[41].remove(g);c.dets.remove(f'// DETECTOR c[{b}]')
    release={}
    for q in lay['A']+lay['B']+lay['C']:
        prev=[(t,g) for t,ss in enumerate(c.segs) for g in ss if q in map(int,QRE.findall(g[0]))]
        last,g=max(prev,key=lambda z:z[0]) if prev else (-1,[])
        basis='Z' if not g or g[0].startswith(('measure','reset')) and len(g)==1 else 'X' if g[0].startswith('h') and 'measure' in ' '.join(g) else 'unknown'
        release[q]=(last,basis)
    if fast:
        release[3]=(38,'Z');release[15]=(38,'Z') # coherent-hop sources are zero without a measurement
    if swap and label.endswith('drop'):release[21]=(40,'Z')
    c.header=[f'creg c[{bit}];' if h.startswith('creg') else h for h in c.header]
    for t,ss in enumerate(c.segs):
        seen=set()
        for g in ss:
            qs=set(map(int,QRE.findall(' '.join(g))));assert not seen&qs,(t,g,seen&qs);seen|=qs
    return c,lay,release

def build(label,af,bcf,name,helpers=True):
    c,lay,release=prefix(label);R=lay['R'];A,B,C,D=[lay[k] for k in ['A','B','C','D']];bit=c.max_creg()+1
    ae=json.loads(Path(af).read_text());bc=json.loads(Path(bcf).read_text())
    for i,(kind,t) in enumerate(ae['init']):
        if kind:c.segs[t].append([f'reset q[{A[i]}];']+([f'h q[{A[i]}];'] if kind==2 else []))
    for t,i,j in ae['layers']:c.segs[t].append([f'cx q[{A[i]}],q[{A[j]}];'])
    first={}
    for t,ss in enumerate(bc['ops']):
        for a,b in ss:
            for q in (a,b):first.setdefault(q,t+bc['T0'])
            c.segs[t+bc['T0']].append([f'cx q[{a}],q[{b}];'])
    piv=set(map(int,bc['pivots']))
    for q,t in first.items():
        if t-1==release[q][0]:
            assert release[q][1]==('X' if q in piv else 'Z'),(q,t,release[q])
        else:
            assert t-1>release[q][0],(q,t,release[q])
            c.segs[t-1].append([f'reset q[{q}];']+([f'h q[{q}];'] if q in piv else []))
    f=lay['flag'][0];mid,e1,e2=[f[k] for k in ['mid','end1','end2']]
    for i,(d,a,b,cc) in enumerate(zip(D,A,B,C)):
        c.segs[R-1 if i in lay['flagdata'] else R].append([f'cx q[{d}],q[{a}];'])
        c.segs[R].append([f'cx q[{b}],q[{cc}];'])
        c.segs[R+1].append([f'cx q[{b}],q[{d}];'])
    c.segs[R].append([f'cx q[{A[mid]}],q[{A[e2]}];']);c.segs[R+1].append([f'cx q[{A[e1]}],q[{A[mid]}];'])
    abit=[];bbit=[];cbit=[]
    for block,basis,t,records in [(A,'Z',R+2,abit),(B,'X',R+2,bbit),(C,'Z',R+1,cbit)]:
        for i,q in enumerate(block):
            xb=basis=='X' or (block is A and i==e1)
            records.append(bit);c.segs[t].append(([f'h q[{q}];'] if xb else [])+[f'measure q[{q}] -> c[{bit}];']);bit+=1
    hs=[85,102,120];span={0}
    for h in hs:span|={v^h for v in list(span)}
    rows=[];pivots={}
    for mask in range(1,128):
        if mask>>e1&1:continue
        z=mask
        for a,b in reversed([(mid,e2),(e1,mid)]):
            if z>>b&1:z^=1<<a
        if z not in span:continue
        v=mask
        while v:
            p=v.bit_length()-1
            if p in pivots:v^=pivots[p]
            else:pivots[p]=v;rows.append(mask);break
    assert len(rows)==3
    for bits,masks in [(abit,rows),(bbit,hs)]:
        for mask in masks:c.dets.append('// DETECTOR '+' '.join(f'c[{bits[i]}]' for i in range(7) if mask>>i&1))
    for b in cbit+[abit[e1]]:c.dets.append(f'// DETECTOR c[{b}]')
    if helpers:
        for h in lay['helpers']:
            q,d=h['helper'],h['cell'];c.segs[R-1].append([f'reset q[{q}];',f'h q[{q}];']);c.segs[R].append([f'cx q[{d}],q[{q}];']);c.segs[R+1].append([f'h q[{q}];',f'measure q[{q}] -> c[{bit}];']);c.dets.append(f'// DETECTOR c[{bit}]');bit+=1
    c.header=[f'creg c[{bit}];' if h.startswith('creg') else h for h in c.header]
    desc=dict(family=label,layout=lay,A_encoder=str(af),BC_encoder=str(bcf),helpers=helpers)
    st=save(c,name,desc);md=json.loads(st.with_suffix('.json').read_text());md['data_qubits']=D;st.with_suffix('.json').write_text(json.dumps(md,indent=2)+'\n')
    return st

if __name__=='__main__':
    if len(sys.argv)>2:print(build(*sys.argv[1:5],helpers=len(sys.argv)<6 or sys.argv[5]!='nohelpers'))
    else:
        label=sys.argv[1];c,lay,release=prefix(label)
        (HERE/'layouts'/f'{label}_release.json').write_text(json.dumps(release,indent=2));print(label,release)
