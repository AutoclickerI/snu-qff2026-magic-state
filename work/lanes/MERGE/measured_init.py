"""Replace reset preparations by measured preparations when byproducts never change logical data.

Propagate the recorded Pauli byproduct exactly, XOR it into later detector records,
and require the final data byproduct to be a Steane stabilizer (including identity).
No FRAME or POSTSELECT annotations are introduced.
"""
from lib import *

SPAN={0}
for row in [85,102,120]:SPAN|={x^row for x in list(SPAN)}

def convert_init(c,index):
    cc=copy.deepcopy(c);source=cc['ops'][index];u=unit(source)
    assert u.name in ('RESET','RX')
    q=u.qs[0];b=bit(cc);axis='X' if u.name=='RX' else 'Z'
    source['lines']=([f'h q[{q}];'] if axis=='X' else [])+[f'measure q[{q}] -> c[{b}];']+([f'h q[{q}];'] if axis=='X' else [])
    x=[0]*36;z=[0]*36;flips={}
    for i,o in sorted(enumerate(cc['ops']),key=lambda v:(v[1]['t'],v[0])):
        v=unit(o);qs=v.qs
        if i==index:
            x[q]=int(axis=='Z');z[q]=int(axis=='X');continue
        if v.name in ('RESET','RX'):x[qs[0]]=z[qs[0]]=0
        elif v.name=='CX':
            a,t=map(int,re.findall(r'q\[(\d+)\]',o['lines'][0]));x[t]^=x[a];z[a]^=z[t]
        elif v.name in ('MEASURE','MX'):
            qq=qs[0];bb=bits_of(o)[0];f=z[qq] if v.name=='MX' else x[qq]
            if f:flips[bb]=1
            if v.name=='MX':x[qq]=0
            else:z[qq]=0
        elif v.name=='H':x[qs[0]],z[qs[0]]=z[qs[0]],x[qs[0]]
        elif v.name in ('T','TDG'):
            if x[qs[0]]:return None
        elif v.name in ('I','ID'):pass
        else:raise ValueError(v.name)
    data=cc['meta']['data_qubits'];dx=sum(x[q]<<i for i,q in enumerate(data));dz=sum(z[q]<<i for i,q in enumerate(data))
    if dx not in SPAN or dz not in SPAN:return None
    tail=[]
    for line in cc['tail']:
        if not line.startswith('// DETECTOR'):tail.append(line);continue
        bits=list(map(int,BITRE.findall(line)))
        if sum(flips.get(bb,0) for bb in bits)%2:bits.append(b)
        tail.append('// DETECTOR '+' '.join(f'c[{bb}]' for bb in bits))
    cc['tail']=tail
    return fix(cc),dict(q=q,t=source['t'],axis=axis,bit=b,record_flips=sorted(flips),data_frame=[dx,dz])

def variants(c):
    for i,o in enumerate(c['ops']):
        if unit(o).name not in ('RESET','RX'):continue
        result=convert_init(c,i)
        if result is not None:yield result

def checked_variants(c):
    """A deterministic zero outcome needs no output-frame restriction: the new detector fixes its bit to zero."""
    for index,o in enumerate(c['ops']):
        v=unit(o)
        if v.name not in ('RESET','RX'):continue
        cc=copy.deepcopy(c);q=v.qs[0];b=bit(cc);axis='X' if v.name=='RX' else 'Z'
        cc['ops'][index]['lines']=([f'h q[{q}];'] if axis=='X' else [])+[f'measure q[{q}] -> c[{b}];']+([f'h q[{q}];'] if axis=='X' else [])
        cc['tail'].append(f'// DETECTOR c[{b}]')
        yield fix(cc),dict(q=q,t=o['t'],axis=axis,bit=b,postselected_zero=True)

def fused_variants(c):
    """Move a preceding same-basis measurement onto a redundant reset slot, retaining its checked record."""
    for index,o in enumerate(c['ops']):
        v=unit(o)
        if v.name not in ('RESET','RX'):continue
        q=v.qs[0];before=[(i,p) for i,p in enumerate(c['ops']) if q in unit(p).qs and p['t']<o['t']]
        if not before:continue
        j,p=max(before,key=lambda x:x[1]['t']);pv=unit(p)
        if pv.name!=('MX' if v.name=='RX' else 'MEASURE'):continue
        b=bits_of(p)[0];cc=copy.deepcopy(c);cc['ops'][j]['t']=o['t'];cc['ops'].pop(index)
        added=not in_span(c,b)
        if added:cc['tail'].append(f'// DETECTOR c[{b}]')
        yield fix(cc),dict(q=q,old_measure=p['t'],reset_t=o['t'],bit=b,axis='X' if v.name=='RX' else 'Z',added_detector=added)
