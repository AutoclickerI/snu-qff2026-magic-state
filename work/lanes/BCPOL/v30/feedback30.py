"""Fixed-pivot refinement priced by an exact exterior response cache."""
from evaluator import *
from contract30 import Model,verify,joint
from build30 import build
from cache30 import compile as compile_cache
from cache import setup
from boundary_api import AllOrdersCache,PreparedRegion
from moments_batch import evaluate
import random,lzma

def run(seed_tag,seed,seconds=600):
    rec=json.loads((V/'runs'/(seed_tag+'.best.json')).read_text());d=rec['prep'];source=V/'finalists'/rec['tag'];md=json.loads(source.with_suffix('.json').read_text())
    parent=V/'inputs'/f'feedback_{seed}';parent.with_suffix('.qasm').write_text(source.with_suffix('.qasm').read_text());parent.with_suffix('.json').write_text(json.dumps(md,indent=2))
    if parent.with_suffix('.boundary_allorders.json').exists() and parent.with_suffix('.allorders.json').exists():
        base=json.loads(parent.with_suffix('.boundary_allorders.json').read_text());oracle=json.loads(parent.with_suffix('.allorders.json').read_text())
        assert setup(parent)[-1]==base['exterior_hash']
    else:
        base=compile_cache(parent)
        oracle=globals()['run_oracle'](parent,False if not d.get('bell') else True)
    assert abs(oracle['loss']-base['loss'])<1e-12
    cache=AllOrdersCache(parent.with_suffix('.boundary_allorders.npz'));D=len(d['ops'])+1;cap=sum(map(len,d['ops']))+8
    m=Model(D,cap,seed,d,helper_x=d.get('helper_x',False))
    for q,z in m.nz.items():m.add([z if q in d['pivots'] else -z])
    for t in range(D+1):
        for q in m.cells:m.cut((t,(q,)))
    for t,ss in enumerate(m.sel):
        for e in ss:m.cut((t+1,e))
    d=dict(d,ops=d['ops']+[[]]);m.warm(d);best=base['loss'];besttag=None;hint=d;count=hits=misses=0;start=time.monotonic();rng=random.Random(seed);tally=[]
    with lzma.open(V/'runs'/f'feedback_{seed}.jsonl.xz','wt') as log:
        while time.monotonic()-start<seconds:
            free=set(rng.sample(range(D),rng.choice([3,4,5,6,D])));ass=[]
            for t,ss in enumerate(m.sel):
                if t not in free:
                    active={tuple(e) for e in hint['ops'][t]};ass.extend(z if e in active else -z for e,z in ss.items())
            m.s.conf_budget(5000);ok=m.s.solve_limited(assumptions=ass)
            if ok is not True:continue
            cand=m.candidate();v=verify(cand);assert v['stim_target_pass'] and v['policy_pass'];count+=1
            mv={z for z in m.s.get_model() if z>0};m.add([-z if z in mv else z for ss in m.sel for z in ss.values()]);row=dict(index=count,verification=v)
            try:
                text,new=build(joint(cand),dict(base='v30f',mx=md['options']['mx'],fixed_init=md['init_times'],timing='alap'))
                current=V/'inputs'/f'feedback_{seed}_current';current.with_suffix('.qasm').write_text(text);current.with_suffix('.json').write_text(json.dumps(new,indent=2))
                ev,b,classes,prep,ext,hh=setup(current);region=PreparedRegion(hh,tuple(tuple((int(k),float(ev.fp[i])) for i,k in items) for items in prep.values()),len(classes))
                if hh!=cache.fingerprint:misses+=1;row['status']='EXTERIOR_MISMATCH'
                else:
                    r=cache.score(region);hits+=1;row.update(r,status='EXACT_CACHE')
                    if r['acceptance']>=.5002 and r['loss']<best:
                        best=r['loss'];besttag=f'feedback_{seed}_{count:05d}';s=V/'finalists'/besttag;s.with_suffix('.qasm').write_text(text);s.with_suffix('.json').write_text(json.dumps(new,indent=2));price=evaluate(ev);s.with_suffix('.screen.json').write_text(json.dumps(price,indent=2));s.with_suffix('.cached_allorders.json').write_text(json.dumps(r,indent=2));print(json.dumps(dict(tag=besttag,**r)),flush=True)
                        (V/'runs'/f'feedback_{seed}.best.json').write_text(json.dumps(dict(tag=besttag,prep=cand,row=price,allorders=r),indent=2))
                    if r['loss']<best+5e-7 or rng.random()<.04:hint=cand
            except (ValueError,AssertionError) as ex:row.update(status='REJECTED',error=str(ex))
            log.write(json.dumps(dict(row=row,prep=cand))+'\n');log.flush();m.warm(hint)
    result=dict(parent=seed_tag,status='BUDGET_FINISHED',witnesses=count,cache_hits=hits,cache_misses=misses,best=best,best_tag=besttag,seconds=time.monotonic()-start,base=base['loss'])
    (V/'runs'/f'feedback_{seed}.receipt.json').write_text(json.dumps(result,indent=2));print(json.dumps(result),flush=True)

run_oracle=__import__('evaluator').run
if __name__=='__main__':run(sys.argv[1],int(sys.argv[2]))
