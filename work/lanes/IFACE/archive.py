"""Retain release diversity, independently of fixed-suffix loss."""
import copy,itertools,json,sys
from model import *
from completion import snapshots
from ideal import check
from price import price

def remove(c,t,a,b):c.segs[t].remove([f'cx q[{a}],q[{b}];'])
def movebit(c,b,t):
    at=[(j,k,g) for j,seg in enumerate(c.segs) for k,g in enumerate(seg) if classify(g)[2]==b]
    assert len(at)==1
    j,k,g=at[0];c.segs[j].pop(k);c.segs[t].append(g)

def strip(c,kind):
    if 'h' in kind:remove(c,33,15,16)
    if 'd' in kind:remove(c,34,10,4)
    if 'e' in kind:
        remove(c,32,13,14);remove(c,29,20,26);remove(c,30,20,26)
    if 'j' in kind:
        for t in (30,31,32):remove(c,t,11,10)
    if 'b' in kind:
        remove(c,32,6,7);remove(c,33,6,0)
    return c

def main():
    c=Circ((HERE/'builds/v36h.qasm').read_text());rows=[];seen=set()
    # Four useful release axes, each retained even when its fixed-suffix loss
    # loses. Bit 64's early/late choice doubles these 12 distinct guard cuts.
    cuts=['h','d','e','j','hd','he','hj','de','dj','ej','hde','hdej']
    for cut,blue in itertools.product(cuts,[False,True]):
        cc=strip(copy.deepcopy(c),cut)
        weights={54:1,55:1,56:1,57:2,8:1,12:1,274:1,280:1,45:1}
        if blue:weights[64]=1;weights[67]=1
        cc,info=retime(cc,weights,seconds=5,workers=3)
        if cc is None:raise RuntimeError(info)
        if not blue:movebit(cc,64,37)
        name='if_'+cut+('_blue' if blue else '')
        p=save(cc,name,dict(family='state_specific_completion',cut=cut,early_blue=blue),meta={'interface':info['profile']})
        ideal=check(p)
        if not ideal['ok']:raise RuntimeError((name,ideal))
        fp=hashlib.sha256(p.with_suffix('.qasm').read_bytes()).hexdigest()
        row=dict(name=name,sha256=fp,release=profile(cc),solver=info,ideal=ideal)
        if fp not in seen:
            seen.add(fp);rows.append(row)
            result=price(p,workers=3)
            if result:print('INTERFACE',name,result['loss'],result['acceptance'],profile(cc)['source_release'],flush=True)
        (HERE/'archive.json').write_text(json.dumps(rows,indent=2)+'\n')
    print('ARCHIVED',len(rows),flush=True)

if __name__=='__main__':main()
