"""Search the 64 square-tile A/B orientations for native A-only preparation."""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[key]='1'
import argparse,json,random,time
from pathlib import Path
import a_factory as af
import a_factory_search as search
from partial_contract import A as A0,B as B0,C,D
HERE=Path(__file__).resolve().parent

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--trials',type=int,default=400);ap.add_argument('--seed',type=int,default=1)
    ap.add_argument('--boundary');ap.add_argument('--states');ap.add_argument('--output');ap.add_argument('--mask',type=int)
    ap.add_argument('--a');ap.add_argument('--b');ap.add_argument('--c')
    a=ap.parse_args();st=time.perf_counter();boundary=json.loads(Path(a.boundary or HERE/'prefix_release.json').read_text())
    release={int(q):t for q,t in boundary['release'].items()};states={r['q']:r for r in json.loads(Path(a.states or HERE/'prefix_product_states.json').read_text())['cells']}
    allbest=[];scores=[]
    for mask in ([0] if a.a else [a.mask] if a.mask is not None else range(64)):
        aa=list(map(int,a.a.split(','))) if a.a else [B0[i] if mask>>i&1 else A0[i] for i in range(7)]
        bb=list(map(int,a.b.split(','))) if a.b else [A0[i] if mask>>i&1 else B0[i] for i in range(7)]
        cc=list(map(int,a.c.split(','))) if a.c else C
        assert len(aa)==7 and len(set(aa))==7 and not set(aa)&set(D)
        af.A=aa;af.TARGET={q:aa.index(q)+1 if q in aa else 0 for q in af.CELLS}
        rng=random.Random(a.seed+1009*mask);best=[]
        for i in range(a.trials):
            direct=bool(i%2);result=search.construct(rng,direct)
            if not result:continue
            initial,gates=result;row=search.schedule(initial,gates,release,states,rng,direct)
            row.update(trial=i,orientation=mask,A=aa,B=bb,C=cc,D=D)
            best.append(row)
            if len(best)>20:best=sorted(best,key=lambda r:(r['a_ready'],r['cx'],len(r['helpers'])))[:10]
        best.sort(key=lambda r:(r['a_ready'],r['cx'],len(r['helpers'])))
        if not best:continue
        row=best[0];gates=[tuple(o['qs']) for o in row['operations'] if o['kind']=='CX']
        opt=search.schedule({int(q):v for q,v in row['initial_rows'].items()},gates,release,states,rng,row['direct'],.5)
        if opt['a_ready']<=row['a_ready']:row.update(opt)
        allbest+=best[:3];brief={k:row[k] for k in ('orientation','A','a_ready','module_end','cx','direct','plus_inputs','helper_release')};scores.append(brief)
        if mask in (0,3) or row['a_ready']<=45:print(json.dumps(brief),flush=True)
    allbest.sort(key=lambda r:(r['a_ready'],r['cx'],len(r['helpers'])))
    out=dict(prefix_stem=boundary['stem'],boundary_file=a.boundary or str(HERE/'prefix_release.json'),
        states_file=a.states or str(HERE/'prefix_product_states.json'),trials_per_orientation=a.trials,seed=a.seed,
        seconds=time.perf_counter()-st,orientations=sorted(scores,key=lambda r:(r['a_ready'],r['cx'])),candidates=allbest[:30])
    Path(a.output or HERE/'a_orientation.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(dict(seconds=out['seconds'],best=out['orientations'][:12])),flush=True)

if __name__=='__main__':main()
