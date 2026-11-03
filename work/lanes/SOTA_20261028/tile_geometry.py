"""Construct connected resource geometries by packing unlabelled native tiles.

Unlike the coordinate model, this solves set packing before assigning code
coordinates. Witnesses have actual D-A, B-D, B-C edges and at least four C-A
edges, with connected A and B/C footprints. They are not complete circuits.
"""
import argparse,itertools,json,random,time
from pathlib import Path
from ortools.sat.python import cp_model

HERE=Path(__file__).resolve().parent
OLD=[6,20,19,10,2,22,16]
MASKS=[85,102,120,51,45,30,75]
NEAR={q:[r for r in range(36)if abs(q//6-r//6)+abs(q%6-r%6)==1]for q in range(36)}
EDGES=[(q,r)for q in range(36)for r in NEAR[q]]
TILES=[(d,a,b,c)for d in range(36)for a in NEAR[d]for b in NEAR[d]if b!=a
       for c in NEAR[b]if c not in (d,a)]


def label(tiles,require_support=True):
    best=None
    for perm in itertools.permutations(range(7)):
        ordered=[tiles[i]for i in perm]
        mask=sum((1<<i)for i,(_,a,b,c)in enumerate(ordered)if c in NEAR[a])
        if require_support and not any(mask&s==s for s in MASKS):continue
        distance=sum(abs(t[0]//6-q//6)+abs(t[0]%6-q%6)for t,q in zip(ordered,OLD))
        if best is None or distance<best[0]:best=(distance,ordered,mask)
    if best is None:return None
    d,ordered,mask=best
    return dict(roles={k:[t[i]for t in ordered]for i,k in enumerate('DABC')},
                move_distance=d,square_mask=mask,squares=[i for i in range(7)if mask>>i&1])


def solve(seed,seconds,minimum,aroot,bcroot,objective=True,borrow_free=False):
    rng=random.Random(seed);m=cp_model.CpModel()
    chosen=[m.new_bool_var(f'tile{i}')for i in range(len(TILES))]
    m.add(sum(chosen)==7)
    occupied={k:[m.new_bool_var(f'{k}{q}')for q in range(36)]for k in 'DABC'}
    for q in range(36):
        for j,k in enumerate('DABC'):
            m.add(occupied[k][q]==sum(chosen[i]for i,t in enumerate(TILES)if t[j]==q))
        m.add(sum(occupied[k][q]for k in 'DABC')<=1)
    square=[i for i,t in enumerate(TILES)if t[3]in NEAR[t[1]]]
    m.add(sum(chosen[i]for i in square)>=minimum)
    bc=[m.new_bool_var(f'BC{q}')for q in range(36)]
    for q in range(36):m.add(bc[q]==occupied['B'][q]+occupied['C'][q])
    def connect(occ,n,root,tag,allowed=None):
        if allowed is None:allowed=occ
        if root>=0:
            m.add(occ[root]==1);roots=[int(q==root)for q in range(36)]
        else:
            roots=[m.new_bool_var(f'root{tag}{q}')for q in range(36)]
            m.add(sum(roots)==1)
            for q in range(36):
                m.add(roots[q]<=occ[q])
                if q:m.add(sum(occ[:q])==0).only_enforce_if(roots[q])
        flows={}
        for q,r in EDGES:
            z=m.new_int_var(0,n-1,f'f{tag}{q}_{r}')
            m.add(z<=(n-1)*allowed[q]);m.add(z<=(n-1)*allowed[r]);flows[q,r]=z
        for q in range(36):
            outgoing=sum(flows[q,r]for r in NEAR[q]);incoming=sum(flows[r,q]for r in NEAR[q])
            m.add(outgoing-incoming==n*roots[q]-occ[q])
    connect(occupied['A'],7,aroot,'A')
    allowed=[1-occupied['A'][q]-occupied['D'][q]for q in range(36)]if borrow_free else bc
    connect(bc,14,bcroot,'BC',allowed)
    if objective:
        costs=[]
        for i,t in enumerate(TILES):
            d,a,b,c=t
            move=min(abs(d//6-q//6)+abs(d%6-q%6)for q in OLD)
            compact=abs(a//6-2)+abs(a%6-2)
            costs.append((20*move+2*compact+rng.randrange(7))*chosen[i])
        m.minimize(sum(costs)-sum(chosen[i]for i in square))
    solver=cp_model.CpSolver();solver.parameters.max_time_in_seconds=seconds
    solver.parameters.num_search_workers=1;solver.parameters.random_seed=seed
    started=time.perf_counter();status=solver.solve(m)
    row=dict(status=solver.status_name(status),seconds=time.perf_counter()-started,seed=seed,
             minimum=minimum,A_root=aroot,BC_root=bcroot,borrow_free=borrow_free,tiles_available=len(TILES),
             scope='Native geometry only. Source relocation and fault-tolerant resource preparation remain to be implemented.')
    if status in (cp_model.FEASIBLE,cp_model.OPTIMAL):
        tiles=[t for i,t in enumerate(TILES)if solver.value(chosen[i])]
        row.update(tiles=tiles,**label(tiles,minimum>=4))
        if objective:row.update(objective=solver.objective_value,bound=solver.best_objective_bound)
    return row


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--seed',type=int,default=0);p.add_argument('--seconds',type=float,default=120)
    p.add_argument('--minimum',type=int,default=4);p.add_argument('--a-root',type=int,default=7);p.add_argument('--bc-root',type=int,default=12)
    p.add_argument('--borrow-free',action='store_true')
    p.add_argument('--feasible-only',action='store_true');p.add_argument('--output',type=Path,default=HERE/'tile_geometry.json');a=p.parse_args()
    row=solve(a.seed,a.seconds,a.minimum,a.a_root,a.bc_root,not a.feasible_only,a.borrow_free)
    a.output.write_text(json.dumps(row,indent=2)+'\n');print(json.dumps(row),flush=True)
