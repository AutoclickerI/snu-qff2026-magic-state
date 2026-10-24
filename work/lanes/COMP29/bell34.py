"""Move terminal B/C parity checking after B->data, pricing both Bell forms."""
from decoder34 import *

def remove_edges(base,edges):
    c=base
    for edge in edges:
        c=cancel_added(build(c,[edge]));assert c['meta']['terminal_cancellations'],edge
    return c

def move_check(base,k,kind):
    b,cc,d=C.B[k],C.C[k],C.D[k]
    base=C.clone(base)
    data_gate=next(i for i,u in enumerate(base['u']) if u.lines==[f'cx q[{b}],q[{d}];'] and base['t'][i]==46)
    base['u'][data_gate].late_BD=True
    if kind=='reverse':
        c=cancel_added(build(base,[(b,cc),(cc,b)]))
        assert c['meta']['terminal_cancellations'],'existing B/C edge cannot commute to cancel'
    else:
        c=C.clone(base)
        # Change the per-wire order of two equal-control CXs, exactly commuting.
        i=next(i for i,u in enumerate(c['u']) if u.lines==[f'cx q[{b}],q[{cc}];'] and c['t'][i]==45)
        j=next(i for i,u in enumerate(c['u']) if u.lines==[f'cx q[{b}],q[{d}];'] and c['t'][i]==46)
        assert all(C.commute(c['u'][i],v) for v in c['u'][i+1:j]),'B/C check cannot commute through an intervening readout edge'
        c['u'][i].decoder_added=True
        c['u'][i],c['u'][j]=c['u'][j],c['u'][i]
        term=terminal(c);mi=term[cc]['index']
        # The C readout follows the newly delayed check.
        u=c['u'].pop(mi);t=c['t'].pop(mi);c['u'].append(u);c['t'].append(47)
    targets={i:t for i,t in enumerate(c['t']) if t<=40}
    for i,u in enumerate(c['u']):
        if getattr(u,'late_BD',False):targets[i]=45
        if getattr(u,'decoder_added',False) and u.name=='CX':targets[i]=46
    c=C.retime(c,targets=targets,horizon=47)
    assert c is not None,'no 48-step schedule with prefix through t40 fixed'
    order=sorted(range(len(c['u'])),key=lambda i:(c['t'][i],i));c['u']=[c['u'][i] for i in order];c['t']=[c['t'][i] for i in order]
    c['meta']['terminal_BC_check']=dict(index=k,B=b,C=cc,data=d,kind=kind,prefix_fixed_through=40)
    return c

if __name__=='__main__':
    base=C.read(H/'g_base');rows=[];errors=[]
    for mask in range(4):
        edges=[e for i,e in enumerate([(19,25),(17,16)]) if mask>>i&1]
        parent=remove_edges(base,edges)
        if mask:
            n=f'g_remove_{mask}';r=save(parent,n,['remove readout edges',edges]);rows.append(r)
        for k in range(7):
            for kind in ['forward','reverse']:
                n=f'g_bell2_{mask}_{k}_{kind}'
                try:
                    c=move_check(parent,k,kind);r=save(c,n,['late BC check',dict(index=k,kind=kind,removed_edges=edges)]);r['native_depth']=max(c['t'])+1;rows.append(r)
                except Exception as e:errors.append(dict(stem=n,error=repr(e)))
    (H/'v34_bell2.json').write_text(json.dumps(rows,indent=2)+'\n');(H/'v34_bell2_errors.json').write_text(json.dumps(errors,indent=2)+'\n')
    print(dict(built=len(rows),errors=len(errors)));print(errors[:8])
