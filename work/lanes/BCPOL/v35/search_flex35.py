"""Joint resource/transfer synthesis with initialization release co-design."""
from core35 import *
import search35 as search
from boundary_flex35 import region
import fresh_synth as F
import argparse

START=28
FREE_MAP=False
def models(base,seednum,cap,clean=True,joint=True):
    assert joint
    F.S.target=lambda cells:{q:sum(1<<k for k,row in enumerate(F.ROWS) if q in {B[i] for i in row}) for q in cells}
    F.S.endpoint_signature=lambda q:F.ft.sig({q},B)|sum(int(q==cc)<<(4+i) for i,cc in enumerate(C))
    d=seed(base,True);start=START;D=45-start;d['ops']=[[]]*(d['start']-start)+d['ops'];d['start']=start
    init=init_indices(base);release={q:max([base['ts'][j] for j,u in enumerate(base['us']) if q in u.qs and base['ts'][j]<base['ts'][i]],default=-1)+1 for q,i in init.items()}
    flag_times=[base['ts'][i] for i,u in enumerate(base['us']) if u.name=='MEASURE' and u.qs==(13,) and i!=init[13] and base['ts'][init[13]]<=base['ts'][i]<44]
    m=F.Model(D,cap,seednum,clean=False);piv=set(d['pivots'])
    for q,z in m.nz.items():m.add([z if q in piv else -z])
    ar=F.S.target(m.cells)
    for layer in reversed(d['ops']):
        for a,b in layer:ar[b]^=ar[a]
    if not FREE_MAP:
        for q in m.cells:
            val=F.S.transform(ar[q],m.bas)
            for j,z in enumerate(m.x[0][q]):m.add([z if val>>j&1 else -z])
    for t,ss in enumerate(m.sel):
        for e,z in ss.items():
            if any(start+t<=release[q] for q in e) or (13 in e and start+t in flag_times):m.add([-z])
    for tm in flag_times:
        for z in m.x[tm-start][13]:m.add([-z])
    for t in range(D+1):
        for q in m.cells:m.cut((t,(q,)))
    for t,ss in enumerate(m.sel):
        for e in ss:m.cut((t+1,e))
    m.warm(d);rng=random.Random(seednum);hint=d
    while True:
        free=set(rng.sample(range(D),rng.choice([4,6,8,10,D])));ass=[]
        for t,ss in enumerate(m.sel):
            if t not in free:
                act={tuple(e) for e in hint['ops'][t]};ass.extend(z if e in act else -z for e,z in ss.items())
        m.s.conf_budget(2000);ok=m.s.solve_limited(assumptions=ass)
        if ok is not True:yield None;continue
        cand=m.candidate();cand.update(start=start,joint=True)
        xs=[F.ft.propagate(cand['ops'],(0,(q,))) for q in cand['pivots']];gs=[sum(1<<B[i] for i in row) for row in F.ROWS]
        assert F.span([sum(1<<q for q in e) for e in xs])==F.span(gs)
        for src in F.ft.sources(cand,cand['cells']):
            e=F.ft.propagate(cand['ops'],src);assert (set(C)&e) or not F.ft.dangerous(F.ft.sig(e,B))
        active={v for v in m.s.get_model() if v>0};m.add([-z if z in active else z for ss in m.sel for z in ss.values()])
        c=replace_encoder(base,cand);before=copy.deepcopy(c);ix=init_indices(c);changes={}
        for q,i in ix.items():
            first=min([start+t for t,layer in enumerate(cand['ops']) if any(q in e for e in layer)],default=base['ts'][init[q]]+1)
            at=first-1
            if q==13 and flag_times:at=min(at,min(flag_times)-1)
            assert at>=release[q],(q,at,release[q]);c['ts'][i]=at;c['md']['init_times'][str(q)]=at;changes[q]=at
        c=reframe(c,before)
        accepted=yield c,dict(kind='flex_initializations_and_joint_encoder',seed=seednum,prep=cand,init_times=changes,release_times=release,free_generator_map=FREE_MAP)
        if accepted or rng.random()<.05:hint=cand
        m.warm(hint)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('seed',type=int);p.add_argument('--source',required=True);p.add_argument('--start',type=int,default=28);p.add_argument('--seconds',type=int,default=900);p.add_argument('--cap',type=int,default=64);p.add_argument('--free-map',action='store_true');a=p.parse_args();START=a.start;FREE_MAP=a.free_map
    search.sat_models=models;search.region=region
    search.run('joint',a.seed,a.seconds,a.cap,a.source)
