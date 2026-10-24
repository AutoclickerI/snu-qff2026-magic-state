"""Protect an echo's terminal readout by copying its basis value to a helper."""
from bell34 import *
CASES=[(264,17),(265,12),(268,18),(271,11),(272,27),(269,32),(270,17)]
def copy_echo(base,bit,helper):
    c=C.clone(base);i=next(i for i,u in enumerate(c['u']) if f'measure q[' in ' '.join(u.lines) and f'-> c[{bit}];' in ' '.join(u.lines));u=c['u'][i];q=u.qs[0];t=c['t'][i]
    assert u.name in ('MEASURE','MX') and f'// DETECTOR c[{bit}]' in c['tail']
    if bit in (268,271):
        j=max(j for j,v in enumerate(c['u']) if q in v.qs and c['t'][j]<t);assert c['u'][j].name=='CX' and c['t'][j]==t-1
        assert not any(set(v.qs)&set(c['u'][j].qs) and tt==t-2 for k,(v,tt) in enumerate(zip(c['u'],c['t'])) if k!=j)
        c['t'][j]=t-2;t-=1
    assert not any(helper in v.qs and t-1<=tt<=t+1 for v,tt in zip(c['u'],c['t']))
    c['t'][i]=t+1
    if bit==270:
        js=[j for j,v in enumerate(c['u']) if '-> c[43];' in ' '.join(v.lines)]
        if js:
            j=js[0];assert c['t'][j]==t+1;c['t'][j]=t+2
    assert not any(q in v.qs and tt==t+1 and j!=i for j,(v,tt) in enumerate(zip(c['u'],c['t'])))
    nb=C.bit(c);rx=u.name=='MX'
    def add(lines,tt):c['u'].append(C.Unit(lines));c['t'].append(tt)
    add([f'reset q[{helper}];']+([f'h q[{helper}];'] if rx else []),t-1)
    a,b=(helper,q) if rx else (q,helper);add([f'cx q[{a}],q[{b}];'],t)
    add(([f'h q[{helper}];'] if rx else [])+[f'measure q[{helper}] -> c[{nb}];']+([f'h q[{helper}];'] if rx else []),t+1)
    future=sorted((tt,v) for v,tt in zip(base['u'],base['t']) if helper in v.qs and tt>t+1)
    if future and future[0][1].name not in ('RESET','RX'):
        tf,v=future[0];assert v.name in ('MX','MEASURE') and tf-1>t+1
        if v.name=='MX':
            assert tf-2>t+1
            add([f'reset q[{helper}];'],tf-2);add([f'id q[{helper}];'],tf-1)
        else:add([f'reset q[{helper}];'],tf-1)
    c['tail'].append(f'// DETECTOR c[{nb}]');order=sorted(range(len(c['u'])),key=lambda j:(c['t'][j],j));c['u']=[c['u'][j] for j in order];c['t']=[c['t'][j] for j in order]
    c['meta']['echo_readout_copy']=dict(record=bit,qubit=q,helper=helper,basis='X' if rx else 'Z',copy_tick=t)
    return c

if __name__=='__main__':
    base=C.read(H/'g_base');rows=[];errors=[]
    for mask in range(4):
        edges=[e for i,e in enumerate([(19,25),(17,16)]) if mask>>i&1];parent=remove_edges(base,edges)
        for bit,helper in CASES:
            n=f'g_echo_{mask}_{bit}'
            try:
                c=copy_echo(parent,bit,helper);rows.append(save(c,n,['echo readout copy',dict(bit=bit,helper=helper,remove_edges=edges)]))
            except Exception as e:errors.append(dict(stem=n,error=repr(e)))
    (H/'v34_echo.json').write_text(json.dumps(rows,indent=2)+'\n');(H/'v34_echo_errors.json').write_text(json.dumps(errors,indent=2)+'\n');print(dict(built=len(rows),errors=errors))
