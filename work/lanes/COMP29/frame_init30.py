"""Replace a Z reset by measured preparation with a propagated X frame.

Only contexts whose complete frame vanishes on all output data are admitted.
All detector corrections are derived from the actual native Clifford suffix.
"""
from build30 import *
def build_frame(c,q):
    c=C.clone(c);ids=[i for i,u in enumerate(c['u']) if u.name=='RESET' and u.qs==(q,) and c['t'][i]>=30];assert len(ids)==1
    source=ids[0];bit=C.bit(c);c['u'][source]=C.Unit([f'measure q[{q}] -> c[{bit}];'])
    frames={j:[set(),set()] for j in range(36)};corr={}
    for i,u in enumerate(c['u']):
        if i==source:frames[q]=[{bit},set()];continue
        if u.name in ('RESET','RX'):frames[u.qs[0]]=[set(),set()]
        elif u.name=='CX':
            a,b=map(int,C.S.QRE.findall(u.lines[0]));frames[b][0]^=frames[a][0];frames[a][1]^=frames[b][1]
        elif u.name in ('MX','MEASURE'):
            b=int(re.search(r'c\[(\d+)\]',' '.join(u.lines))[1]);corr[b]=frames[u.qs[0]][u.name=='MX'].copy()
        elif u.name=='H':frames[u.qs[0]].reverse()
        elif u.name in ('S','SDG'):frames[u.qs[0]][1]^=frames[u.qs[0]][0]
        elif u.name in ('T','TDG'):assert not frames[u.qs[0]][0],('non-Clifford X frame',u.lines)
        else:assert not any(any(frames[j]) for j in u.qs),(u.name,u.lines)
    assert all(not any(frames[j]) for j in c['meta']['data_qubits']),frames
    for i,line in enumerate(c['tail']):
        if not line.startswith('// DETECTOR'):continue
        bs=set(map(int,re.findall(r'c\[(\d+)\]',line)));delta=set()
        for b in bs:delta^=corr.get(b,set())
        c['tail'][i]='// DETECTOR '+' '.join(f'c[{b}]' for b in sorted(bs^delta))
    c['meta']['virtual_x_preparations']=[dict(qubit=q,record=bit,corrected_records=sorted(b for b,v in corr.items() if v))]
    return finish(c)
if __name__=='__main__':
    base=C.read(H/'f_timing_mz_5_12');c=build_frame(base,13);name='f_frame13';r=save(c,name,['f_timing_mz_5_12','q13 measured Z initialization with propagated X frame']);r.update(screen(name));(H/'v30_frame_init.json').write_text(json.dumps([r],indent=2));print(json.dumps(r),flush=True)
