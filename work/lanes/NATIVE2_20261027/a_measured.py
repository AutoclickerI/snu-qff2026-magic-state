"""Native dual A encoders whose borrowed cells are measured, not uncomputed.

Before the final H on A, each measured helper carries a linear function of
the three |0L> variables. Its X outcome induces a known X byproduct on the
final |+L> ancilla. Such X operators commute through terminal CXs targeting
A; they can therefore be included in A's Z-record parity checks.
"""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[key]='1'
import argparse,json,random,time
from pathlib import Path
import a_factory as af
import a_factory_search as search
HERE=Path(__file__).resolve().parent

def construct(rng):
    result=search.construct(rng,False)
    if not result:return
    initial,gates=result;target=search.canonical({q:v for q,v in af.TARGET.items() if q in af.A},3)
    def run(gs):
        rr=initial.copy()
        for a,b in gs:rr[b]^=rr[a]
        return rr
    def valid(gs):return search.canonical({q:v for q,v in run(gs).items() if q in af.A},3)==target
    for _ in range(2):
        order=list(range(len(gates)));rng.shuffle(order);changed=False
        for i in order:
            if i>=len(gates):continue
            trial=gates[:i]+gates[i+1:]
            if valid(trial):gates=trial;changed=True
        if not changed:break
    rr=initial.copy();pruned=[]
    for a,b in gates:
        if rr[a]:rr[b]^=rr[a];pruned.append((a,b))
    assert valid(pruned)
    return initial,pruned,rr

def schedule(initial,gates,final,release,states,rng):
    used=set(af.A)|{q for edge in gates for q in edge};plus={q for q,v in initial.items() if v}
    def known(q):return states[q].get('product_axis')==('X' if q in plus else 'Z') and not states[q].get('phase_constant')
    earliest={q:release[q]+int(not known(q)) for q in used}
    pred=[{j for j,(c,d) in enumerate(gates[:i]) if b==c or d==a} for i,(a,b) in enumerate(gates)]
    succ=[set() for _ in gates]
    for i,ps in enumerate(pred):
        for j in ps:succ[j].add(i)
    length=[1]*len(gates)
    for i in range(len(gates)-1,-1,-1):length[i]=1+max((length[j] for j in succ[i]),default=0)
    remaining=set(range(len(gates)));done=set();times=[None]*len(gates);busy=earliest.copy()
    while remaining:
        avail=[i for i in remaining if pred[i]<=done]
        def key(i):
            a,b=gates[i];t=max(busy[a],busy[b],max((times[j]+1 for j in pred[i]),default=0))
            return t,-length[i]+rng.random()*.1
        i=min(avail,key=key);a,b=gates[i];t=max(busy[a],busy[b],max((times[j]+1 for j in pred[i]),default=0))
        times[i]=t;busy[a]=busy[b]=t+1;done.add(i);remaining.remove(i)
    first={q:min((t for t,e in zip(times,gates) if q in e),default=release[q]+1) for q in used}
    last={q:max((t for t,e in zip(times,gates) if q in e),default=first[q]-1) for q in used}
    lookup={final[q]:q for q in af.A};assert len(lookup)==7 and 0 not in lookup
    operations=[];reused=[];phase_records=[]
    for q in used:
        if first[q]==release[q] and known(q):
            reused.append(q)
            for bit in states[q].get('phase_xor',[]):phase_records.append(dict(source_bit=bit,target=lookup[initial[q]],source_qubit=q))
        else:operations.append(dict(time=first[q]-1,kind='RX' if q in plus else 'R',qs=[q]))
    operations += [dict(time=t,kind='CX',qs=list(e)) for t,e in zip(times,gates)]
    operations += [dict(time=last[q]+1,kind='H',qs=[q]) for q in af.A]
    helpers=sorted(used-set(af.A));byproducts=[]
    for q in helpers:
        row=dict(time=last[q]+1,kind='MX' if final[q] else 'M',qs=[q],zero_flag=not final[q])
        if final[q]:row['a_x_byproduct']=lookup[final[q]];byproducts.append(dict(helper=q,target=lookup[final[q]],time=last[q]+1))
        operations.append(row)
    return dict(cx=len(gates),a_ready=max(last[q]+2 for q in af.A),module_end=max(o['time'] for o in operations)+1,
        A=af.A,helpers=helpers,helper_release={q:last[q]+2 for q in helpers},reused_inputs=reused,
        plus_inputs=sorted(plus),initial_rows=initial,final_rows=final,operations=sorted(operations,key=lambda o:(o['time'],o['kind'],o['qs'])),
        helper_x_byproducts=byproducts,source_x_byproducts=phase_records,backward_map_verified=True,
        target='A plusL with recorded X byproducts; helper MX phases are propagated into terminal A-Z checks')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--a',default='7,14,18,4,8,21,15');ap.add_argument('--trials',type=int,default=5000);ap.add_argument('--seed',type=int,default=1)
    ap.add_argument('--boundary');ap.add_argument('--states');ap.add_argument('--output');a=ap.parse_args();st=time.perf_counter()
    af.A=list(map(int,a.a.split(',')));af.TARGET={q:af.A.index(q)+1 if q in af.A else 0 for q in af.CELLS}
    boundary=json.loads(Path(a.boundary or HERE/'prefix_release.json').read_text());release={int(q):v for q,v in boundary['release'].items()}
    states={r['q']:r for r in json.loads(Path(a.states or HERE/'prefix_product_states.json').read_text())['cells']};rng=random.Random(a.seed)
    candidates=[];seen=set()
    for i in range(a.trials):
        result=construct(rng)
        if not result:continue
        initial,gates,final=result;row=schedule(initial,gates,final,release,states,rng)
        key=(row['a_ready'],row['cx'],tuple(row['helpers']),tuple(row['plus_inputs']))
        if key in seen:continue
        seen.add(key);row['trial']=i;candidates.append(row)
        if len(candidates)>100:candidates=sorted(candidates,key=lambda r:(r['a_ready'],r['cx'],sum(r['helper_release'].values())))[:50]
    candidates.sort(key=lambda r:(r['a_ready'],r['cx'],sum(r['helper_release'].values())))
    out=dict(prefix_stem=boundary['stem'],boundary_file=a.boundary or str(HERE/'prefix_release.json'),
        states_file=a.states or str(HERE/'prefix_product_states.json'),trials=a.trials,seed=a.seed,seconds=time.perf_counter()-st,candidates=candidates[:20])
    Path(a.output or HERE/'a_measured.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(dict(seconds=out['seconds'],best=[{k:r[k] for k in ('cx','a_ready','helpers','helper_release','plus_inputs','helper_x_byproducts')} for r in candidates[:5]])),flush=True)

if __name__=='__main__':main()
