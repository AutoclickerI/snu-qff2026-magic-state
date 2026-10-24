"""Broad cache feedback over FRESH resource SAT and joint commuting schedules."""
from core35 import *
from boundary35 import region
from moments_batch import evaluate
from ortools.sat.python import cp_model
import lzma,argparse

def sat_models(base,seednum,cap,clean=True,joint=False):
    import fresh_synth as F
    if joint:
        F.S.target=lambda cells:{q:sum(1<<k for k,row in enumerate(F.ROWS) if q in {B[i] for i in row}) for q in cells}
        F.S.endpoint_signature=lambda q:F.ft.sig({q},B)|sum(int(q==cc)<<(4+i) for i,cc in enumerate(C))
        clean=False
    d=seed(base,joint);D=len(d['ops']);start=d['start'];m=F.Model(D,cap,seednum,clean=clean);piv=set(d['pivots']);init=init_indices(base)
    flag_times=[base['ts'][i] for i,u in enumerate(base['us']) if u.name=='MEASURE' and u.qs==(13,) and i!=init[13] and base['ts'][init[13]]<=base['ts'][i]<44]
    for q,z in m.nz.items():m.add([z if q in piv else -z])
    # Hold the initial random-MX frame map, not merely its output span.
    ar={q:F.S.target(m.cells)[q] for q in m.cells}
    for layer in reversed(d['ops']):
        for a,b in layer:ar[b]^=ar[a]
    for q in m.cells:
        val=F.S.transform(ar[q],m.bas)
        for j,z in enumerate(m.x[0][q]):m.add([z if val>>j&1 else -z])
    for t,ss in enumerate(m.sel):
        for e,z in ss.items():
            if any(start+t<=base['ts'][init[q]] for q in e) or (13 in e and start+t in flag_times):m.add([-z])
    for tm in flag_times:
        if tm>=start:
            for z in m.x[tm-start][13]:m.add([-z])
    for t in range(D+1):
        for q in m.cells:m.cut((t,(q,)))
    for t,ss in enumerate(m.sel):
        for e in ss:m.cut((t+1,e))
    m.warm(d);rng=random.Random(seednum);hint=d
    while True:
        free=set(rng.sample(range(D),rng.choice([3,4,5,6,D])));ass=[]
        for t,ss in enumerate(m.sel):
            if t not in free:
                act={tuple(e) for e in hint['ops'][t]};ass.extend(z if e in act else -z for e,z in ss.items())
        m.s.conf_budget(1200);ok=m.s.solve_limited(assumptions=ass)
        if ok is not True:yield None;continue
        cand=m.candidate();cand.update(start=start,joint=joint)
        if joint:
            xs=[F.ft.propagate(cand['ops'],(0,(q,))) for q in cand['pivots']];gs=[sum(1<<B[i] for i in row) for row in F.ROWS]
            bad=[]
            for src in F.ft.sources(cand,cand['cells']):
                err=F.ft.propagate(cand['ops'],src)
                if not(set(C)&err) and F.ft.dangerous(F.ft.sig(err,B)):bad.append(src)
            vv=dict(target_ok=F.span([sum(1<<q for q in err) for err in xs])==F.span(gs),bad=bad,cx=sum(map(len,cand['ops'])))
        else:vv=F.verify(cand,clean)
        assert vv['target_ok'] and not vv['bad'],vv
        active={v for v in m.s.get_model() if v>0};m.add([-z if z in active else z for ss in m.sel for z in ss.values()])
        accepted=yield (replace_encoder(base,cand),dict(kind='fresh_sat',seed=seednum,prep=cand,verification=vv))
        if accepted or rng.random()<.04:hint=cand
        m.warm(hint)

def commute(e,f):return e[0]!=f[1] and e[1]!=f[0]
def schedules(base,seednum,transfers=True):
    rng=random.Random(seednum);selected=prep_indices(base)
    if transfers:selected += [i for i,u in enumerate(base['us']) if u.name=='CX' and edge(u) in list(zip(B,C)) and base['ts'][i]==44]
    selected=sorted(selected,key=lambda i:(base['ts'][i],i));chosen=set(selected);m=cp_model.CpModel();tv={};bounds={}
    for i in selected:
        u=base['us'][i];t=base['ts'][i];lo=0;hi=44
        for j,v in enumerate(base['us']):
            if j in chosen or not(set(u.qs)&set(v.qs)):continue
            if base['ts'][j]<t:lo=max(lo,base['ts'][j]+1)
            elif base['ts'][j]>t:hi=min(hi,base['ts'][j]-1)
        tv[i]=m.NewIntVar(lo,hi,f't{i}');bounds[i]=(lo,hi)
    for q in BC:
        intervals=[m.NewFixedSizeIntervalVar(tv[i],1,f'q{q}i{i}') for i in selected if q in base['us'][i].qs];m.AddNoOverlap(intervals)
    for k,i in enumerate(selected):
        for j in selected[k+1:]:
            if not commute(edge(base['us'][i]),edge(base['us'][j])):m.Add(tv[i]<tv[j])
    solver=cp_model.CpSolver();solver.parameters.num_search_workers=1;solver.parameters.max_time_in_seconds=.35;solver.parameters.random_seed=seednum
    while True:
        m.ClearObjective();m.Minimize(sum(rng.choice([-13,-7,-3,-1,1,3,7,13])*tv[i] for i in selected));st=solver.Solve(m)
        if st==cp_model.INFEASIBLE:return
        if st not in (cp_model.OPTIMAL,cp_model.FEASIBLE):yield None;continue
        c=copy.deepcopy(base);changes=[]
        for i in selected:
            new=solver.Value(tv[i]);c['ts'][i]=new
            if new!=base['ts'][i]:changes.append(dict(index=i,lines=base['us'][i].lines,old=base['ts'][i],new=new))
        m.AddForbiddenAssignments([tv[i] for i in selected],[[solver.Value(tv[i]) for i in selected]])
        yield c,dict(kind='commuting_joint_schedule',seed=seednum,changes=changes,transfers=transfers)

def run(mode,seednum,seconds=300,cap=61,source=None):
    base=load(source);cache_stem=Path(source) if source else V/'inputs/cache_open_v35a';cache=AllOrdersCache(cache_stem.with_suffix('.boundary_allorders.npz'))
    control=json.loads(cache_stem.with_suffix('.boundary_allorders.json').read_text());best=control['loss'];name=f'{mode}_{seednum}';current=V/'inputs'/f'{name}_current'
    gen=sat_models(base,seednum,cap,mode!='relaxed',mode=='joint') if mode in ('sat','relaxed','joint') else schedules(base,seednum,mode!='prep_timing')
    seen=set();counts=collections.Counter();besttag=None;start=time.monotonic();accepted=False;missbest=1
    with lzma.open(V/'runs'/f'{name}.jsonl.xz','wt') as log:
        while time.monotonic()-start<seconds:
            try:result=gen.send(accepted) if accepted else next(gen)
            except StopIteration:counts['enumeration_complete']=1;break
            accepted=False;counts['iterations']+=1
            if result is None:continue
            c,recipe=result;counts['witnesses']+=1
            try:
                text,md=emit(c,recipe=recipe);sha=md['qasm_sha256']
                if sha in seen:counts['duplicates']+=1;continue
                seen.add(sha);current.with_suffix('.qasm').write_text(text);current.with_suffix('.json').write_text(json.dumps(md))
                r,ev=region(current)
                if r.fingerprint!=cache.fingerprint:
                    counts['fingerprint_miss']+=1;p=evaluate(ev);row=dict(status='NEW_EXTERIOR',price=p,recipe=recipe)
                    if p['total']<missbest and p['exp_minus_A1']>=.5002:
                        missbest=p['total'];tag=f'{name}_exterior_{counts["witnesses"]:06d}';emit(c,V/'finalists'/tag,recipe);(V/'finalists'/f'{tag}.screen.json').write_text(json.dumps(p));row['tag']=tag
                else:
                    p=cache.score(r);counts['cache_hits']+=1;row=dict(status='CACHE',**p,recipe=recipe)
                    if p['acceptance']>=.5005 and p['loss']<best-1e-13:
                        best=p['loss'];besttag=f'{name}_{counts["witnesses"]:06d}';emit(c,V/'finalists'/besttag,recipe);(V/'finalists'/f'{besttag}.cached_allorders.json').write_text(json.dumps(p,indent=2));(V/'runs'/f'{name}.best.json').write_text(json.dumps(dict(tag=besttag,**p,recipe=recipe),indent=2));row['tag']=besttag;accepted=True;print(json.dumps(dict(tag=besttag,**p)),flush=True)
            except (ValueError,AssertionError) as ex:counts['rejected']+=1;row=dict(status='REJECTED',error=str(ex),recipe=recipe)
            log.write(json.dumps(row)+'\n')
    out=dict(status='FINITE_RUN_COMPLETE',mode=mode,seed=seednum,seconds=time.monotonic()-start,counts=dict(counts),best=best,best_tag=besttag,baseline=control['loss']);(V/'runs'/f'{name}.receipt.json').write_text(json.dumps(out,indent=2));print(json.dumps(out),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode');p.add_argument('seed',type=int);p.add_argument('--seconds',type=int,default=300);p.add_argument('--cap',type=int,default=61);p.add_argument('--source');a=p.parse_args();run(a.mode,a.seed,a.seconds,a.cap,a.source)
