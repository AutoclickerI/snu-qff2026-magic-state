"""Native B-zeroL factories on cells disjoint from the restored A footprint."""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='1'
import argparse,json,random,sys,time
from pathlib import Path
from measured_resource import ROOT,HERE,construct,schedule
from resource_pauli_audit import audit
from partial_contract import make_partial_contract,STEANE_X


def contract(swap=False):
    roles=dict(D=[6,20,19,10,2,22,16],A=[7,14,13,9,8,21,15],
               B=[12,26,25,11,3,28,17],C=[0,1,4,5,18,23,24])
    if swap:roles['A'],roles['B']=roles['B'],roles['A']
    pc=make_partial_contract(roles,0,True,False)
    old=pc.terminal();active=set(roles['D']+roles['A']+roles['B'])
    terminal=[o for o in old if set(o[1])<=active]
    pc.terminal=lambda:terminal
    pc.DETECTORS=pc.DETECTORS[:6]
    pc.ROWS=[{pc.B[i] for i in range(7) if g>>i&1} for g in STEANE_X]
    pc.COLS={q:sum(1<<j for j,r in enumerate(pc.ROWS) if q in r) for q in range(36) if q not in set(pc.D+pc.A)}
    pc.rank=3;pc.post_h=[];pc.late_plus=[]
    pc.CELLS=list(pc.B);pc.HELPERS=sorted(set(pc.COLS)-set(pc.B));pc.kind='disjoint_b_only'
    return pc


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--trials',type=int,default=10000);ap.add_argument('--seed',type=int,default=0)
    ap.add_argument('--protect',type=float,default=1);ap.add_argument('--basis-steps',type=int,default=20)
    ap.add_argument('--swap',action='store_true')
    ap.add_argument('--boundary',default=str(ROOT/'work/lanes/NATIVE2_20261027/prefix_release.json'))
    ap.add_argument('--states',default=str(ROOT/'work/lanes/NATIVE2_20261027/prefix_product_states.json'))
    ap.add_argument('--output',default=str(HERE/'b_resource.json'))
    args=ap.parse_args();start=time.perf_counter();pc=contract(args.swap);rng=random.Random(args.seed)
    boundary=json.loads(Path(args.boundary).read_text());release={int(q):v for q,v in boundary['release'].items()}
    states={r['q']:r for r in json.loads(Path(args.states).read_text())['cells']}
    candidates=[];seen=set();valid=0
    for i in range(args.trials):
        result=construct(pc,rng,release,mix=True,fill_mode=i%3,basis_steps=args.basis_steps,protect=args.protect,root_any=True)
        if result is None:continue
        valid+=1;row=schedule(pc,*result,release,states,rng)
        row['resource_ready']=max(o['time']+1 for o in row['operations'] if set(o['qs'])&set(pc.B))
        row['trial']=i;row['resource_c1']=audit(pc,row)['resource_c1']
        key=(row['resource_c1'],row['resource_ready'],row['cx'],tuple(row['plus_inputs']))
        if key in seen:continue
        seen.add(key);candidates.append(row);candidates.sort(key=lambda r:(r['resource_c1'],r['resource_ready'],r['cx']));candidates=candidates[:30]
        if len(candidates)==1 or candidates[0] is row:
            print(json.dumps(dict(trial=i,valid=valid,seconds=time.perf_counter()-start,best={k:row[k] for k in ['resource_c1','resource_ready','module_end','cx','plus_inputs']})),flush=True)
    out=dict(prefix_stem=boundary['stem'],roles=pc.roles,square_mask=0,terminal_operations=pc.terminal(),
        drop_free=True,b_only=True,swapped=args.swap,dual_a=False,boundary_file=args.boundary,states_file=args.states,
        trials=args.trials,valid_seeds=valid,seed=args.seed,protect_fraction=args.protect,seconds=time.perf_counter()-start,candidates=candidates)
    Path(args.output).write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(dict(output=args.output,seconds=out['seconds'],best=[{k:r[k] for k in ['resource_c1','resource_ready','module_end','cx','helpers','plus_inputs']} for r in candidates[:5]])),flush=True)


if __name__=='__main__':main()
