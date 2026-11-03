"""Joint terminal geometry with connected native preparation footprints.

Data cells are free. A is required connected, and B union C is connected, so
the resource generator need not route through the data by construction. A
weight-four Steane support must have real C-to-A square contacts. This is only
geometry; no loss or preparation performance is inferred from a witness.
"""
import argparse,json,time
from pathlib import Path
from ortools.sat.python import cp_model

HERE=Path(__file__).resolve().parent
OLD=dict(D=[6,20,19,10,2,22,16],A=[7,14,13,9,8,21,15],
         B=[12,26,25,11,3,28,17],C=[18,27,24,5,4,29,23])
MASKS=[85,102,120,85^102,85^120,102^120,85^102^120]


def build(seed,seconds,minimum=4,keep_a=False,max_move=None):
    m=cp_model.CpModel()
    cells={k:[m.new_int_var(0,35,f'{k}{i}')for i in range(7)]for k in 'DABC'}
    rs={};cs={}
    for k in 'DABC':
        for i,q in enumerate(cells[k]):
            r=m.new_int_var(0,5,f'r{k}{i}');c=m.new_int_var(0,5,f'c{k}{i}')
            m.add(q==6*r+c);rs[k,i]=r;cs[k,i]=c
            m.add_hint(q,OLD[k][i])
    m.add_all_different([q for arr in cells.values()for q in arr])
    distance={};adjacency={}
    def dist(u,v):
        key=tuple(sorted((u,v)))
        if key not in distance:
            dr=m.new_int_var(0,5,f'dr{key}');dc=m.new_int_var(0,5,f'dc{key}')
            m.add_abs_equality(dr,rs[u]-rs[v]);m.add_abs_equality(dc,cs[u]-cs[v])
            d=m.new_int_var(1,10,f'd{key}');m.add(d==dr+dc);distance[key]=d
        return distance[key]
    def adjacent(u,v):
        key=tuple(sorted((u,v)))
        if key not in adjacency:
            a=m.new_bool_var(f'adj{key}');d=dist(u,v)
            m.add(d==1).only_enforce_if(a);m.add(d!=1).only_enforce_if(a.Not())
            adjacency[key]=a
        return adjacency[key]
    squares=[]
    for i in range(7):
        for a,b in [('D','A'),('D','B'),('B','C')]:m.add(dist((a,i),(b,i))==1)
        squares.append(adjacent(('A',i),('C',i)))
    m.add(sum(squares)>=minimum)
    complete_support=[]
    for mask in MASKS:
        z=m.new_bool_var(f'support{mask}')
        for i in range(7):
            if mask>>i&1:m.add(squares[i]==1).only_enforce_if(z)
        complete_support.append(z)
    m.add(sum(complete_support)>=1)
    edge_sets={}
    def connected(nodes,label):
        n=len(nodes);flows={};edges=[]
        for i,u in enumerate(nodes):
            for j in range(i+1,n):
                v=nodes[j];a=adjacent(u,v);edges.append(a)
                for x,y in [(i,j),(j,i)]:
                    f=m.new_int_var(0,n-1,f'flow{label}_{x}_{y}');m.add(f<=(n-1)*a);flows[x,y]=f
        for i in range(n):
            outgoing=sum(f for (x,y),f in flows.items()if x==i)
            incoming=sum(f for (x,y),f in flows.items()if y==i)
            m.add(outgoing-incoming==(n-1 if i==0 else -1))
        edge_sets[label]=edges
    connected([('A',i)for i in range(7)],'A')
    connected([(k,i)for k in 'BC'for i in range(7)],'BC')
    moves=[]
    for i,q in enumerate(OLD['D']):
        dr=m.new_int_var(0,5,f'dmove_r{i}');dc=m.new_int_var(0,5,f'dmove_c{i}')
        m.add_abs_equality(dr,rs['D',i]-q//6);m.add_abs_equality(dc,cs['D',i]-q%6)
        moves.extend([dr,dc])
    if keep_a:
        for i,q in enumerate(OLD['A']):m.add(cells['A'][i]==q)
    if max_move is not None:m.add(sum(moves)<=max_move)
    # Resource connectivity is a hard feasibility requirement; graph edge count
    # and displacement are only generation preferences, never noisy scores.
    m.minimize(20*sum(moves)-3*sum(edge_sets['A'])-sum(edge_sets['BC'])-2*sum(squares))
    solver=cp_model.CpSolver();solver.parameters.max_time_in_seconds=seconds
    solver.parameters.num_search_workers=1;solver.parameters.random_seed=seed
    started=time.perf_counter();status=solver.solve(m)
    row=dict(status=solver.status_name(status),seconds=time.perf_counter()-started,seed=seed,
             minimum_squares=minimum,keep_a=keep_a,max_move=max_move,
             scope='Geometry only; resources and source relocation are not implemented by this witness.')
    if status in (cp_model.FEASIBLE,cp_model.OPTIMAL):
        row.update(roles={k:[solver.value(q)for q in arr]for k,arr in cells.items()},
                   squares=[i for i,z in enumerate(squares)if solver.value(z)],
                   move_distance=sum(solver.value(x)for x in moves),
                   A_edges=sum(solver.value(x)for x in edge_sets['A']),
                   BC_edges=sum(solver.value(x)for x in edge_sets['BC']),
                   objective=solver.objective_value,bound=solver.best_objective_bound)
    return row


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--seed',type=int,default=0);p.add_argument('--seconds',type=float,default=180)
    p.add_argument('--minimum',type=int,default=4);p.add_argument('--keep-a',action='store_true');p.add_argument('--max-move',type=int)
    p.add_argument('--output',type=Path,default=HERE/'connected_geometry.json');args=p.parse_args()
    row=build(args.seed,args.seconds,args.minimum,args.keep_a,args.max_move)
    args.output.write_text(json.dumps(row,indent=2)+'\n');print(json.dumps(row),flush=True)
