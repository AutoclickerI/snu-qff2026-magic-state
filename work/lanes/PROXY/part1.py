"""Reproduce every legacy round proxy and compare independent X/Y probes."""
import os, sys, json, itertools, math
from pathlib import Path
ROOT=Path('/home/jihoon/competitions/quantumn'); HERE=ROOT/'work/lanes/PROXY'
sys.path[:0]=[str(HERE),str(ROOT/'work'),*[str(ROOT/'work/lanes'/p) for p in ('DR','ST_TP','ST_AV','me_layout')]]
import stim, numpy as np, proxy2
OLD=proxy2.joint_loss
import exact_proxy as ep
import steane, poc, tp, stav, run_moves, gmodel, verify
ROWS=[]; LAST=[]
def capture(cx,cz):
    cy=ep.logical_y(cz)
    cy.without_noise().detector_error_model()
    old=OLD(cx,cz); r=ep.exact_loss(cx,cy,details=True)
    LAST[:]=[cx,cy,cz,r,old]
    steane.FIRST.append(r['first'])
    return old
proxy2.joint_loss=capture

def row(name,fn):
    LAST.clear(); steane.FIRST.clear(); fn()
    cx,cy,cz,r,old=LAST
    out=dict(name=name,old=old,exact=r['cost'],first=r['first'],delta_pct=100*(r['cost']/old-1))
    out['all_orders']=ep.conditional_loss(cx,cy) if cx.num_detectors+7<=21 else None; ROWS.append(out); print(json.dumps(out),flush=True)
    (HERE/'part1_rows.json').write_text(json.dumps(ROWS,indent=2))
    return cx,cy,cz

def all_dem(c):
    return [(d,p,m) for d,vs in ep.mechanisms(c).items() for p,m in vs]

def toy():
    # Three independent physical faults have the same detector and logical X,Y,Z.
    def probe(logical):
        c=stim.Circuit('R 0 1\n'+{'X':'H 0\n','Y':'H 0\nS 0\n','Z':''}[logical])
        for p in 'XYZ':
            c.append('E',[getattr(stim,'target_'+p.lower())(0),stim.target_x(1)],.001)
        if logical=='X':c.append('H',[0])
        if logical=='Y':c.append('S_DAG',[0]);c.append('H',[0])
        c+=stim.Circuit('M 0 1\nDETECTOR rec[-1]\nOBSERVABLE_INCLUDE(6) rec[-2]')
        return c
    cx,cy,cz=[probe(k) for k in 'XYZ']
    p=.001; num=den=0.
    for bs in itertools.product((0,1),repeat=3):
        w=math.prod(p if b else 1-p for b in bs)
        if sum(bs)%2:continue
        den+=w
        x=bs[0]^bs[1];z=bs[1]^bs[2]
        num+=w*(z+(x^z))/2
    r=dict(old=OLD(cx,cz),exact_second=ep.exact_loss(cx,cy),brute_second=2*p*p,brute_all_orders=num/den,acceptance=den,states=8)
    r['xy_all_orders']=ep.conditional_loss(cx,cy)
    assert abs(r['xy_all_orders']-r['brute_all_orders'])<1e-15
    assert abs(r['exact_second']-2e-6)<3e-9
    print('TOY',r,flush=True)
    return r

def physical_faults(c):
    """Explicit mutually-exclusive Pauli branches at every physical noise channel."""
    base=[]; branches=[]
    for inst in c.flattened():
        nm=inst.name;qs=[t.value for t in inst.targets_copy()];args=inst.gate_args_copy()
        if nm not in ('DEPOLARIZE1','DEPOLARIZE2','X_ERROR','Z_ERROR','Y_ERROR'):
            base.append(inst);continue
        n=2 if nm=='DEPOLARIZE2' else 1
        for j in range(0,len(qs),n):
            group=qs[j:j+n]; ps=list(itertools.product('IXYZ',repeat=n))[1:] if nm.startswith('DEPOLARIZE') else [(nm[0],)]
            branches.append((len(base),group,[(a,args[0]/len(ps)) for a in ps]))
    ideal=stim.Circuit()
    for ins in base:ideal.append(ins)
    out=[]
    for ch,(pos,qs,ps) in enumerate(branches):
        for pa,p in ps:
            f=stim.Circuit()
            for ins in base[:pos]:f.append(ins)
            for q,k in zip(qs,pa):
                if k!='I':f.append(k+'_ERROR',[q],1)
            for ins in base[pos:]:f.append(ins)
            d,o=f.compile_detector_sampler(seed=1).sample(1,separate_observables=True)
            dm=sum(int(v)<<i for i,v in enumerate(d[0]));om=sum(int(v)<<i for i,v in enumerate(o[0]))
            out.append((ch,p,dm,om))
    return out,len(branches)

def brute_steane(cx,cy):
    a,nch=physical_faults(cx); b,nchb=physical_faults(cy);assert nch==nchb
    assert [(c,p,d) for c,p,d,m in a]==[(c,p,d) for c,p,d,m in b]
    first=sum(p*(ep.decoded_flip(mx,'X')+ep.decoded_flip(my,'Y'))/2 for (ch,p,d,mx),(_,_,_,my) in zip(a,b) if d==0)
    assert first==0
    pairs=0.;count=0
    for i,(ch,p,d,mx) in enumerate(a):
        my=b[i][3]
        for j in range(i):
            ch2,p2,d2,mx2=a[j]
            if ch==ch2:continue
            count+=1
            if d==d2:pairs+=p*p2*(ep.decoded_flip(mx^mx2,'X')+ep.decoded_flip(my^b[j][3],'Y'))/2
    # The existing proxy keeps Stim's finite-p independent-channel conversion.
    # Scale physical probabilities to isolate the homogeneous p^2 coefficient.
    def scale(c,factor):
        r=stim.Circuit()
        for i in c.flattened():
            args=i.gate_args_copy()
            if i.name in ('DEPOLARIZE1','DEPOLARIZE2','X_ERROR','Y_ERROR','Z_ERROR'):args=[v*factor for v in args]
            r.append(i.name,i.targets_copy(),args)
        return r
    eps=1e-4
    leading=ep.exact_loss(scale(cx,eps),scale(cy,eps))/eps**2
    assert abs(leading-pairs)<2e-11,(leading,pairs)
    # All 64 physical branches on a real ideal Steane round with 3 tail channels.
    # Keep the three final data depolarization channels; enumerate all events.
    tail=[i for i,(ch,p,d,m) in enumerate(a) if ch>=nch-3]
    chans=sorted({a[i][0] for i in tail})
    opts=[[(1-sum(a[i][1] for i in tail if a[i][0]==ch),0,0,0)]+[(a[i][1],a[i][2],a[i][3],b[i][3]) for i in tail if a[i][0]==ch] for ch in chans]
    num=den=0.;states=0
    for combo in itertools.product(*opts):
        states+=1;pr=math.prod(x[0] for x in combo);det=xx=yy=0
        for _,d,x,y in combo:det^=d;xx^=x;yy^=y
        if det==0:
            den+=pr;num+=pr*(ep.decoded_flip(xx,'X')+ep.decoded_flip(yy,'Y'))/2
    r=dict(channels=nch,physical_branches=len(a),cross_channel_pairs=count,first=first,brute_second=pairs,xy_leading_second=leading,xy_finite_p=ep.exact_loss(cx,cy),tail_enumerated_states=states,tail_exact_conditional=num/den)
    print('STEANE_BRUTE',r,flush=True);return r

def main():
    toy_result=toy();stav.PIN[0]=0
    cx,cy,cz=row('DR Steane verified block',lambda:steane.score(vblock=True))
    brute=brute_steane(cx,cy)
    for v in ((),(steane.W3[0],),(steane.W3[0],steane.W3[6])):
        row('DR Steane ver '+str([sorted(s) for s in v]),lambda v=v:steane.score(ver=v))
    for encname,enc in [('std',None),('s7307',tp.json_enc(str(ROOT/'work/lanes/DR/prepA_L5_s7307.json'),stav.A_CELLS)),('exact',tp.json_enc(str(ROOT/'work/lanes/EXENC/prepA_L5_exact.json'),stav.A_CELLS))]:
        for teleport in (False,True):row(f'ST_TP {encname} teleport={teleport}',lambda e=enc,t=teleport:tp.proxy(t,enc_o=e))
    for sa in stav.SPECS:
        for pin in (0,.005,.01,.02):
            for sd in (None,'std','exact'):
                row(f'ST_AV A={sa} D={sd} pin={pin}',lambda a=sa,d=sd,p=pin:stav.score(a,d,p))
    stav.PIN[0]=0
    for name in ('valid','zfirst'):
        sched={int(q):[(t,typ,set(s)) for t,typ,s in v] for q,v in json.loads((ROOT/f'work/lanes/DR/sched_{name}.json').read_text()).items()}
        for ver in (False,True):row(f'DR poc {name} verified={ver}',lambda s=sched,v=ver:poc.proxy(s,verify=v))
        for clean_z in (False,True):row(f'DR clean {name} clean_z={clean_z}',lambda s=sched,z=clean_z:poc.proxy(s,builder=lambda sc:poc.build_clean(sc,clean_z=z)))
        if name=='zfirst':
            for mode in ('pair','cat1'):row(f'DR hybrid {name} z={mode}',lambda s=sched,m=mode:poc.proxy(s,builder=lambda sc:poc.build_hybrid(sc,z_mode=m)))
    # GModel stored schedules, deduplicated by assignment and orientation.
    schedules=[]; seen=set()
    for path in sorted((ROOT/'work/lanes/me_layout').glob('res_*.json')):
        for idx,item in enumerate(json.loads(path.read_text())):
            if len(item)!=5:continue
            old,a,o,seed,name=item
            if name not in ('v6','A1','A2','A3'):continue
            key=json.dumps([a,o,name],sort_keys=True)
            if key in seen:continue
            seen.add(key);m=run_moves.variant(name);aa=verify.load_assign(a)
            LAST.clear();v=m.proxy(aa,o)
            rr=LAST[3]
            schedules.append(dict(src=path.name+'#'+str(idx),old=v,exact=rr['cost'],first=rr['first'],variant=name))
    (HERE/'schedules_rescored.json').write_text(json.dumps(schedules,indent=2))
    # Evaluate each MC source directly, including gen2 L1 mappings.
    mc=[json.loads(s) for s in (ROOT/'work/lanes/me_layout/mseed.jsonl').read_text().splitlines()]
    source={}
    for item in mc:
        src=item['src']
        if src in source:continue
        f,idx=src.split('#'); path=ROOT/'work/lanes/me_layout'/f
        spec=json.loads(path.read_text())[int(idx)]
        if f.startswith('L1_'):
            import ast
            _,aa,o,*_=spec;m=run_moves.variant('v6');ex={t:c for t,c,_ in m.extras};a={}
            for (t,d,typ),L in aa:
                t=int(t)
                k=(t,'U','') if d=='U' else ((t,'A',ex[t]) if d=='A' else (t,gmodel.DATA0.index(ast.literal_eval(d)),typ))
                a[k]=L
        else:
            _,aa,o,_,name=spec;m=run_moves.variant(name);a=verify.load_assign(aa)
        LAST.clear();m.proxy(a,o)
        source[src]=dict(old=LAST[4],exact=LAST[3]['cost'])
    for item in mc:item.update(source[item['src']])
    from scipy.stats import spearmanr,kendalltau
    stats={k:dict(spearman=float(spearmanr([r[k] for r in mc],[r['mean'] for r in mc]).statistic),kendall=float(kendalltau([r[k] for r in mc],[r['mean'] for r in mc]).statistic)) for k in ('old','exact')}
    grouped=[]
    for src,v in source.items():grouped.append(dict(src=src,mean=float(np.mean([r['mean'] for r in mc if r['src']==src])),**v))
    stats['grouped']={k:dict(spearman=float(spearmanr([r[k] for r in grouped],[r['mean'] for r in grouped]).statistic)) for k in ('old','exact')}
    (HERE/'part1_validation.json').write_text(json.dumps(dict(toy=toy_result,steane=brute,ranking=stats,mc=mc,grouped=grouped),indent=2))
    print('RANKING',stats,flush=True)
if __name__=='__main__':main()
