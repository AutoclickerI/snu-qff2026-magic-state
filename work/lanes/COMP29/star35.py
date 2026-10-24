"""Exact finite menu for q16's three idle slots before its existing zero check.

The helper is noiselessly Z=+1 throughout this window. Single control-side CXs
are therefore allowed; target-side CX sequences must still pass ideal checks.
Every complete circuit is priced, including consecutive zero measurements.
"""
from core35 import *
SYMBOLS=['idle','16>10','16>22','10>16','22>16','M16']
def star(base,seq):
    c=C.clone(base);b=C.bit(c)
    for t,symbol in zip([37,38,39],seq):
        if symbol=='idle':continue
        if symbol=='M16':
            u=C.Unit([f'measure q[16] -> c[{b}];']);c['tail'].append(f'// DETECTOR c[{b}]');b+=1
        else:
            a,d=map(int,symbol.split('>'));u=C.Unit([f'cx q[{a}],q[{d}];'])
        assert not any(tt==t and set(u.qs)&set(v.qs) for v,tt in zip(c['u'],c['t']))
        c['u'].append(u);c['t'].append(t)
    order=sorted(range(len(c['u'])),key=lambda i:(c['t'][i],i));c['u']=[c['u'][i] for i in order];c['t']=[c['t'][i] for i in order];return c
if __name__=='__main__':
    base=C.read(H/'h_ST2_feedback_prep');rows=[]
    for indices in itertools.product(range(len(SYMBOLS)),repeat=3):
        if indices==(0,0,0):continue
        seq=[SYMBOLS[i] for i in indices];n='h_star_'+''.join(map(str,indices));r=save(star(base,seq),n,['h_ST2_feedback_prep','q16 terminal idle guard',dict(ticks=[37,38,39],sequence=seq)]);r.update(family='idle_star',sequence=seq);rows.append(r)
    (H/'v35_guard_exchange.json').write_text(json.dumps(rows,indent=2)+'\n');print(len(rows))
