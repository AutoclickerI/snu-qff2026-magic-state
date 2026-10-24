"""Use existing final-layer slack for repeated native Z readout checks."""
from build30 import *

def repeated(c,qs):
    c=C.clone(c)
    for q in qs:
        ids=[i for i,(u,t) in enumerate(zip(c['u'],c['t'])) if u.qs==(q,) and u.name=='MEASURE' and t>=c['meta']['R']]
        assert ids,q
        i=ids[-1];u=c['u'][i];t=c['t'][i]
        assert not any(q in v.qs for v in c['u'][i+1:]),'readout not terminal'
        assert t+1<=max(c['t']),'would extend final layer'
        b=C.bit(c);old=int(re.search(r'c\[(\d+)\]',u.lines[0])[1])
        c['u'].append(C.Unit([f'measure q[{q}] -> c[{b}];']));c['t'].append(t+1);c['tail'].append(f'// DETECTOR c[{old}] c[{b}]')
    return finish(c)

if __name__=='__main__':
    base=C.read(H/'f_base');groups=[[q] for q in (1,14,8,9,2,15,12,5,29,28)]+[[1,14,8,9,2,15],[12,5,29,28],[1,14,8,9,2,15,12,5,29,28]]
    rows=[]
    for qs in groups:
        name='f_repeat_'+'_'.join(map(str,qs))
        try:
            row=save(repeated(base,qs),name,['repeat_Z_'+','.join(map(str,qs))]);row.update(screen(name));rows.append(row);print(name,row['total'],row['exp_minus_A1'],flush=True)
        except Exception as e:rows.append(dict(stem=name,error=repr(e)));print(name,repr(e),flush=True)
    (H/'v30_readout.json').write_text(json.dumps(rows,indent=2)+'\n')
