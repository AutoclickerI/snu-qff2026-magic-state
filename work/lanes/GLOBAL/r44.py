"""Build R43's four-role-change R44 layout while carrying over the complete r3 encoder."""
import copy,json,re,sys
from pathlib import Path
from qedit import load,QRE,CRE
from borrow import HERE,save

LAY=json.loads((HERE/'layouts/r44_1.json').read_text())
DA,AA,BB,CC=[LAY[k] for k in ['D','A','B','C']]
OLD_A=[1,14,8,9,2,16,15]
A_CX=[(37,8,2),(38,2,1),(38,14,8),(39,1,2),(39,9,8),(40,8,2),(40,9,15),(41,8,9),(41,16,15),(42,9,8),(42,15,14),(43,14,8)]

def base(early=False):
    orig=load(str(HERE/'builds/v36h'));c=copy.deepcopy(orig);c.segs=[[] for _ in orig.segs]
    removedbits=set(range(14,21))|{278,296}
    removed=[]
    for t,seg in enumerate(orig.segs):
        for g in seg:
            k=g[0].split()[0];qs=tuple(map(int,QRE.findall(g[0])));bits=set(map(int,CRE.findall(' '.join(g))))
            drop=False
            if k=='cx' and (t,*qs) in A_CX:drop=True
            if k=='reset' and (t,qs[0]) in [(36,8),(36,2),(38,9),(38,16)]:drop=True
            if bits & set(range(14,21)):drop=True
            if k=='cx' and ((t==44 and qs==(9,15)) or (t==45 and qs==(8,9))):drop=True
            if k=='cx' and t in [43,44] and qs[0] in [0,20,7,10,3,22,21] and qs[1] in OLD_A:drop=True
            if k=='cx' and ((qs==(6,0) and 33<=t<=36) or (qs==(6,7) and 32<=t<=41) or (qs==(13,7) and 34<=t<=36)):drop=True
            if k=='cx' and (t,qs) in [(32,(13,14)),(34,(19,20)),(39,(10,16)),(41,(18,12))]:drop=True
            if k=='cx' and qs==(20,14) and t in [40,41]:drop=True
            if 278 in bits:drop=True
            if drop:
                removed.append([t,g]);continue
            tt=t;mapping={}
            if 64 in bits:tt=35
            if 12 in bits:tt=33
            if k=='cx' and t==36 and qs==(14,20):tt=32
            # B/C role lifetimes move as intact blocks; their prefix lives stay on old cells.
            if t>=33:
                if 19 in qs:mapping[19]=24
                if 13 in qs and t>=37:mapping[13]=18
                if 18 in qs:mapping[18]=30
                if 24 in qs:mapping[24]=31
            if t==45 and k=='cx':
                if qs==(6,0):mapping[0]=7
                if qs==(13,7):mapping[7]=19
            gg=[QRE.sub(lambda mt:f'q[{mapping.get(int(mt[1]),int(mt[1]))}]',ln) for ln in g]
            if 296 in bits:gg=['reset q[18];']
            c.segs[tt].append(gg)
    c.dets=[d for d in c.dets if not set(map(int,CRE.findall(d))) & removedbits]
    bit=c.max_creg()+1
    def put(t,g):c.segs[t].append(g)
    def mz(t,q):
        nonlocal bit
        put(t,[f'measure q[{q}] -> c[{bit}];']);c.dets.append(f'// DETECTOR c[{bit}]');bit+=1
    # D0: 0 -> 1 -> 7. D2: 7 -> 13 -> 19. Measured-zero hop sources retain checks.
    put(35,['reset q[19];']);put(37,['reset q[7];'])
    for t,a,b in [(34,7,13),(35,13,7),(36,13,19),(37,19,13),(36,0,1),(37,1,0),(38,1,7),(39,7,1)]:
        put(t,[f'cx q[{a}],q[{b}];'])
    for t,q in [(36,7),(38,13),(38,0),(40,1)]:mz(t,q)
    if early:
        # Two commuting blue-check controls exchange ticks, freeing D2 one tick sooner.
        moves=[(32,33,['cx q[1],q[0];']),(33,32,['cx q[1],q[7];']),
               (34,33,['cx q[7],q[13];']),(35,34,['cx q[13],q[7];']),
               (36,35,['cx q[13],q[19];']),(37,36,['cx q[19],q[13];']),
               (35,34,['reset q[19];']),(36,35,['cx q[0],q[1];']),
               (37,36,['cx q[1],q[0];']),(38,37,['cx q[1],q[7];']),
               (39,38,['cx q[7],q[1];']),(37,36,['reset q[7];'])]
        for t,tt,g in moves:c.segs[t].remove(g)
        for t,tt,g in moves:c.segs[tt].append(g)
        for q,t,tt in [(13,33,32),(7,36,35),(13,38,37),(0,38,37),(1,40,39)]:
            g=next(g for g in c.segs[t] if g[0].startswith(f'measure q[{q}]'))
            c.segs[t].remove(g);c.segs[tt].append(g)
        g=next(g for g in c.segs[35] if '-> c[64];' in ' '.join(g))
        c.segs[35].remove(g);c.dets.remove('// DETECTOR c[64]')
    c.header=[f'creg c[{bit}];' if h.startswith('creg') else h for h in c.header]
    # Retained release measurements are valid Z=0 or X=+ inputs on accepted shots.
    release={8:(35,'Z'),14:(33,'X'),13:(38,'Z'),9:(37,'Z'),2:(35,'X'),16:(37,'Z'),15:(39,'Z')}
    if early:release[13]=(37,'Z')
    for t,ss in enumerate(c.segs):
        seen=set()
        for g in ss:
            qs=set(map(int,QRE.findall(' '.join(g))));assert not seen&qs,(t,g,seen&qs);seen|=qs
            if g[0].startswith('cx'):
                a,b=map(int,QRE.findall(g[0]));assert abs(a//6-b//6)+abs(a%6-b%6)==1,(t,g)
    return c,release,removed

def aparities(flag,gates):
    # Pull final A readouts back across the A decoder and terminal Z-readout CX.
    stab=[0b1010101,0b1100110,0b1111000]
    allowed={0}
    for v in stab:allowed|={x^v for x in list(allowed)}
    rows=[];basis={}
    for mask in range(1,128):
        if mask>>flag&1:continue
        z=mask
        for a,b in reversed(gates):
            if z>>b&1:z^=1<<a
        if z not in allowed:continue
        vv=mask
        while vv:
            p=vv.bit_length()-1
            if p in basis:vv^=basis[p]
            else:basis[p]=vv;rows.append(mask);break
    assert len(rows)==3,rows
    return rows

def build(encfile,name,helper=True):
    enc=json.loads(Path(encfile).read_text());c,release,removed=base(enc.get('routing')=='early');bit=c.max_creg()+1
    f=enc.get('flag',LAY['flag'][0]);mid,e1,e2=[f[k] for k in ['mid','end1','end2']]
    fd={mid,e2};gates=[(mid,e2),(e1,mid)]
    if 1 in (e1,mid) or 6 in (e1,mid):
        c.segs[45].remove(['cx q[14],q[15];'])
    else:gates.append((1,6))
    for i,(kind,t) in enumerate(enc['init']):
        if kind:c.segs[t].append([f'reset q[{AA[i]}];']+([f'h q[{AA[i]}];'] if kind==2 else []))
    for t,i,j in enc['layers']:c.segs[t].append([f'cx q[{AA[i]}],q[{AA[j]}];'])
    for i,(d,a) in enumerate(zip(DA,AA)):c.segs[43 if i in fd else 44].append([f'cx q[{d}],q[{a}];'])
    c.segs[44].append([f'cx q[{AA[mid]}],q[{AA[e2]}];']);c.segs[45].append([f'cx q[{AA[e1]}],q[{AA[mid]}];'])
    abits=[]
    for i,q in enumerate(AA):
        abits.append(bit);c.segs[46].append(([f'h q[{q}];'] if i==e1 else [])+[f'measure q[{q}] -> c[{bit}];']);bit+=1
    for mask in aparities(e1,gates):c.dets.append('// DETECTOR '+' '.join(f'c[{abits[i]}]' for i in range(7) if mask>>i&1))
    c.dets.append(f'// DETECTOR c[{abits[e1]}]')
    if helper:
        c.segs[43].append(['reset q[1];','h q[1];']);c.segs[44].append(['cx q[7],q[1];']);c.segs[45].append(['h q[1];',f'measure q[1] -> c[{bit}];'])
        c.dets.append(f'// DETECTOR c[{bit}]');bit+=1
    c.header=[f'creg c[{bit}];' if h.startswith('creg') else h for h in c.header]
    desc=dict(family='R44 four-role layout',roles=LAY,flag=f,routing=enc.get('routing'),helper=helper,encoder=str(encfile),removed=removed,
              moved='D0 0->1->7; D2 7->13->19; A0/A2 and B2/C2 move; r3 gate sequence retained; echo14 closes at 32')
    stem=save(c,name,desc);meta=json.loads(stem.with_suffix('.json').read_text());meta['data_qubits']=DA
    stem.with_suffix('.json').write_text(json.dumps(meta,indent=2)+'\n')
    return stem

if __name__=='__main__':
    if len(sys.argv)>1:print(build(sys.argv[1],sys.argv[2],len(sys.argv)<4 or sys.argv[3]!='nohelper'))
    else:
        c,rel,removed=base();(HERE/'layouts/r44_prefix.json').write_text(json.dumps(dict(release=rel,removed=removed),indent=2));print(rel)
