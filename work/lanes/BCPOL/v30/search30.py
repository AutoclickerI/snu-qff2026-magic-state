"""Finite SAT portfolios on v30f; no exterior timing edits and no fake UNSAT."""
from evaluator import *
from contract30 import spec,Model,verify,joint
from build30 import build
from moments_batch import evaluate
from boundary_api import prepare_candidate,AllOrdersCache
import random,lzma,traceback

def main(a):
    t=time.monotonic();rng=random.Random(a.seed);tag=f'{a.family}_{a.value}_s{a.seed}'
    meta=json.loads((V/'inputs/v30f.json').read_text());hint=meta['prep'];contract=spec(a.family,a.value,[int(q) for q in a.helpers.split(',') if q])
    m=Model(a.depth,a.cap,a.seed,contract,helper_x=a.family in ('c6','helpermx'))
    hint=dict(hint,ops=(hint['ops'][:-1]+[[]]*a.depth)[:a.depth])
    for tt in range(a.depth+1):
        for q in m.cells:m.cut((tt,(q,)))
    for tt,ss in enumerate(m.sel):
        for edge in ss:m.cut((tt+1,edge))
    m.warm(hint);best=1.;count=priced=clean=0;it=0;solver=0.;besttag=None
    cache=AllOrdersCache(V/'inputs/cache_v30f.boundary_allorders.npz');compatible=0
    with lzma.open(V/'runs'/f'{tag}.jsonl.xz','wt') as log:
        while time.monotonic()-t<a.seconds:
            width=min(a.depth,rng.choice([3,4,5,7,a.depth]));free=set(rng.sample(range(a.depth),width));ass=[]
            for tt,ss in enumerate(m.sel):
                if tt not in free:
                    edges={tuple(e) for e in hint['ops'][tt]};ass.extend(z if e in edges else -z for e,z in ss.items())
            m.s.conf_budget(3000 if width<a.depth else 15000);beg=time.monotonic();ok=m.s.solve_limited(assumptions=ass);solver+=time.monotonic()-beg;it+=1
            if ok is not True:continue
            d=m.candidate();v=verify(d);assert v['stim_target_pass'] and v['policy_pass'],v;count+=1
            mv={z for z in m.s.get_model() if z>0};m.add([-z if z in mv else z for ss in m.sel for z in ss.values()])
            row=dict(tag=f'{tag}_{count:05d}',verification=v)
            try:
                jd=joint(d);opts=dict(base='v30f',mx=[q for q in d['pivots'] if q!=19],timing='alap')
                text,md=build(jd,opts);ev=exact2.Eval(text,md['data_qubits']);c1=float(ev.fp@ev.n_single)
                if abs(c1)>=1e-12:
                    row.update(c1=c1,status='NONZERO_FIRST_ORDER',exp_minus_A1=math.exp(-float(ev.fp@(1-ev.a_single))))
                else:
                    row.update(evaluate(ev));row['status']='CUBIC_SCREEN';priced+=1
                    if row['total']<best and row['exp_minus_A1']>=.5002:
                        stem=V/'finalists'/row['tag'];stem.with_suffix('.qasm').write_text(text);stem.with_suffix('.json').write_text(json.dumps(md,indent=2))
                        try:
                            exact=cache.score(prepare_candidate(stem));row['cached_allorders']=exact;compatible+=1
                        except ValueError as ex:row['cache_mismatch']=str(ex)
                        best=row['total'];besttag=row['tag'];stem.with_suffix('.screen.json').write_text(json.dumps(row,indent=2));print(json.dumps(row),flush=True)
                        (V/'runs'/f'{tag}.best.json').write_text(json.dumps(dict(tag=besttag,prep=d,row=row),indent=2))
                if 'total' in row and (row['total']<=best+5e-7 or rng.random()<.08):hint=d
            except (ValueError,AssertionError) as ex:row.update(status='REJECTED',error=str(ex))
            log.write(json.dumps(dict(row=row,prep=d))+'\n');log.flush();m.warm(hint)
    result=dict(family=a.family,value=a.value,depth=a.depth,cap=a.cap,helpers=contract['helpers'],status='BUDGET_FINISHED',seconds=time.monotonic()-t,solver_seconds=solver,witnesses=count,priced=priced,clean_skipped=clean,cache_hits=compatible,best=best,best_tag=besttag)
    (V/'runs'/f'{tag}.receipt.json').write_text(json.dumps(result,indent=2));print(json.dumps(result),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('family',choices=['rank4','policy','bell4','bell7','c6','helper','helpermx']);p.add_argument('value',type=int);p.add_argument('--seed',type=int,required=True);p.add_argument('--depth',type=int,default=11);p.add_argument('--cap',type=int,default=64);p.add_argument('--seconds',type=float,default=900);p.add_argument('--helpers',default='');main(p.parse_args())
