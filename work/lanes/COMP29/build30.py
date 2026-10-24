"""Native v30f exterior edits; FRESH's rank-three resource is retained."""
from build import *

def resource_ids(c):
    it={int(q):int(t) for q,t in c['meta']['init_times'].items()}
    return {i for i,(u,t) in enumerate(zip(c['u'],c['t'])) if t<48 and set(u.qs)<=it.keys() and all(t>=it[q] for q in u.qs)}

def instrument15(c):
    c=C.clone(c);us=c['u'];ts=c['t'];fix=resource_ids(c)
    mi=next(i for i,u in enumerate(us) if 'measure q[9] -> c[9];' in u.lines)
    ci=max(i for i in range(mi) if us[i].lines==['cx q[9],q[15];']);T=ts[ci];drop={ci,mi}
    for line in ['tdg q[15];','measure q[16] -> c[43];','cx q[15],q[16];','cx q[16],q[15];','measure q[15] -> c[53];']:
        drop.add(next(i for i,u in enumerate(us) if line in u.lines))
    b=C.bit(c)
    new=[(C.Unit(['measure q[16] -> c[43];']),T-1)]
    new += [(C.Unit([f'cx q[{a}],q[{d}];']),T+j) for j,(a,d) in enumerate([(9,15),(15,16),(16,15),(15,16)])]
    new += [(C.Unit(['h q[9];','measure q[9] -> c[9];']),T+4),(C.Unit([f'measure q[15] -> c[{b}];']),T+4),(C.Unit(['tdg q[16];']),T+4)]
    nu=[];nt=[];targets={}
    for i,(u,t) in enumerate(zip(us,ts)):
        if i==ci:
            for v,tv in new:nu.append(v);nt.append(tv)
        if i in drop:continue
        if i in fix:targets[len(nu)]=t
        nu.append(u);nt.append(t)
    c['u']=nu;c['t']=nt;c['tail']=[l for l in c['tail'] if l!='// DETECTOR c[53]']+[f'// DETECTOR c[{b}]']
    c=C.retime(c,targets=targets,round_fixed=True)
    assert c is not None,'instrument15 schedule infeasible with unchanged R48/BC times'
    return finish(c)

def prefix_feedback(c):
    c=C.clone(c)
    diffs=json.loads((H/'v30_prefix_diff.json').read_text())['ST1/v25k_exchange4_feedback_best']['timing_differences']
    for r in diffs:
        if r['lines']==['cx q[10],q[4];'] and r['occurrence']==1:continue # independent timing10 choice
        inds=[i for i,u in enumerate(c['u']) if u.lines==r['lines']]
        i=inds[r['occurrence']];c['t'][i]=r['new']
    # These are a coupled timing macro; repair precedence without moving the
    # FRESH preparation or verification round.
    fix=resource_ids(c);targets={i:c['t'][i] for i in fix}
    for r in diffs:
        if r['lines']==['cx q[10],q[4];'] and r['occurrence']==1:continue
        ids=[i for i,u in enumerate(c['u']) if u.lines==r['lines']];targets[ids[r['occurrence']]]=r['new']
    c=C.retime(c,targets=targets,round_fixed=True)
    assert c is not None,'prefix feedback incompatible with fixed BC schedule'
    return finish(c)

def known_zeros(c):
    it={int(q):int(t) for q,t in c['meta']['init_times'].items()}
    vals={};n=0;out=[]
    for t in range(c['meta']['R']):
        busy=set()
        for u,tt in zip(c['u'],c['t']):
            if tt!=t:continue
            busy|=set(u.qs)
            for q in u.qs:
                if q in it and tt==it[q] and len(u.qs)==1:
                    vals[q]=(1<<n) if u.name in ('RX','MX') else 0;n+=u.name in ('RX','MX')
            if u.name=='CX' and set(u.qs)<=vals.keys():
                a,b=map(int,C.S.QRE.findall(u.lines[0]));vals[b]^=vals[a]
        for q in vals.keys()-busy:
            if vals[q]==0 and t>it[q] and any(tt>t and q in u.qs for u,tt in zip(c['u'],c['t'])):
                out.append((q,t))
    return out

def edit30(c,k):
    if k=='instrument15':return instrument15(c)
    if k=='prefix_feedback':return prefix_feedback(c)
    if k.startswith('zero_'):
        q,t=map(int,k.split('_')[1:]);assert (q,t) in known_zeros(c),(q,t,'not a proven known zero')
        c=C.clone(c);b=C.bit(c);c['u'].append(C.Unit([f'measure q[{q}] -> c[{b}];']));c['t'].append(t);c['tail'].append(f'// DETECTOR c[{b}]')
        return finish(c)
    return edit(c,k)

if __name__=='__main__':
    base=C.read(H/'f_base')
    zeros=known_zeros(base)
    kinds=['instrument15','prefix_feedback','copy4','timing10','commute1','q19check','q11measure','edge14to15']+[f'zero_{q}_{t}' for q,t in zeros]
    (H/'v30_edit_catalog.json').write_text(json.dumps(dict(already_present=['blue_XZ','fused_q4_q10_exchange','v25_prefix_checks'],kinds=kinds,known_zero= zeros),indent=2))
    rows=[save(base,'f_base',[])];errors=[]
    for k in kinds:
        try:
            c=edit30(base,k);name='f_'+k;row=save(c,name,[k]);row.update(screen(name));rows.append(row)
        except Exception as e:errors.append(dict(edit=k,error=repr(e)))
        print(k,rows[-1].get('total') if rows[-1]['edits']==[k] else errors[-1],flush=True)
    (H/'v30_singletons.json').write_text(json.dumps(rows,indent=2)+'\n')
    (H/'v30_build_errors.json').write_text(json.dumps(errors,indent=2)+'\n')
