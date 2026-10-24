"""Extend the zero-helper guard only when a 47-layer native retiming exists."""
from core35 import *
def extend(base,seq):
    c=C.clone(base);end=36+len(seq)
    mi=next(i for i,u in enumerate(c['u']) if 'measure q[16] -> c[55];' in u.lines)
    assert c['t'][mi]==40
    nxt=next(i for i in range(mi+1,len(c['u'])) if 16 in c['u'][i].qs)
    assert c['u'][nxt].lines==['cx q[15],q[16];']
    c['u'][mi].guard_measure=True;c['t'][mi]=end+1
    c['t'][nxt]=end+2
    for t,q in enumerate(seq,37):
        u=C.Unit([f'cx q[16],q[{q}];']);u.guard_time=t;c['u'].append(u);c['t'].append(t)
    order=sorted(range(len(c['u'])),key=lambda i:(c['t'][i],i));c['u']=[c['u'][i] for i in order];c['t']=[c['t'][i] for i in order]
    targets={i:t for i,t in enumerate(c['t']) if t<=35}
    for i,u in enumerate(c['u']):
        if hasattr(u,'guard_time'):targets[i]=u.guard_time
        if getattr(u,'guard_measure',False):targets[i]=end+1
    c=C.retime(c,targets=targets,horizon=46)
    assert c is not None,'no 47-layer retiming with prefix through t35 fixed'
    order=sorted(range(len(c['u'])),key=lambda i:(c['t'][i],i));c['u']=[c['u'][i] for i in order];c['t']=[c['t'][i] for i in order]
    return c
if __name__=='__main__':
    base=C.read(H/'h_ST2_feedback_prep');rows=[];errors=[]
    for seq in list(itertools.product([10,22],repeat=4))+[(10,)*5,(22,)*5]:
        n='h_long_'+''.join('1' if q==10 else '2' for q in seq)
        try:r=save(extend(base,seq),n,['h_ST2_feedback_prep','extend zero-helper guard; retime A preparation',list(seq)]);r['family']='extended_guard';rows.append(r)
        except Exception as e:errors.append(dict(stem=n,error=repr(e)))
    (H/'v35_tailguards.json').write_text(json.dumps(rows,indent=2)+'\n');(H/'v35_tailguard_errors.json').write_text(json.dumps(errors,indent=2)+'\n');print(dict(built=len(rows),errors=errors))
