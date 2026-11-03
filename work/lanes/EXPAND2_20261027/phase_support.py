"""CP-SAT search for a rank-six exact logical-T phase polynomial."""
import argparse,itertools,json,time
from pathlib import Path
from ortools.sat.python import cp_model
HERE=Path(__file__).resolve().parent

def run(seconds=120,no_pairs=True):
    model=cp_model.CpModel();axes=[v for v in range(1,64) if v!=8]
    plus={v:model.new_bool_var(f'p{v}') for v in axes}
    minus={v:model.new_bool_var(f'n{v}') for v in axes}
    take={v:model.new_bool_var(f'x{v}') for v in axes}
    for v in axes:model.add(plus[v]+minus[v]==take[v])
    coef={v:plus[v]-minus[v] for v in axes}
    for degree,modulus in [(1,8),(2,4),(3,2)]:
        for bits in itertools.combinations(range(6),degree):
            mask=sum(1<<i for i in bits);target=1 if mask==8 else 0
            q=model.new_int_var(-32,32,'q'+str(mask))
            model.add(sum(coef[v] for v in axes if v&mask==mask)-target==modulus*q)
    for dual in range(1,64):
        model.add(sum(take[v] for v in axes if (v&dual).bit_count()%2)>=1)
    if no_pairs:
        for v in axes:
            if v<(v^8) and v^8 in take:model.add(take[v]+take[v^8]<=1)
    model.minimize(sum(take.values()))
    for v in axes:
        hint=bool(v&8)
        model.add_hint(minus[v],int(hint));model.add_hint(plus[v],0);model.add_hint(take[v],int(hint))
    solver=cp_model.CpSolver();solver.parameters.max_time_in_seconds=seconds;solver.parameters.num_search_workers=1
    solver.parameters.random_seed=612
    tag='nopairs' if no_pairs else 'free'
    class Found(cp_model.CpSolverSolutionCallback):
        def on_solution_callback(self):
            cs={v:int(self.value(plus[v])-self.value(minus[v])) for v in axes if self.value(take[v])}
            for z in range(64):assert (sum(c*((v&z).bit_count()%2) for v,c in cs.items())-((8&z).bit_count()%2))%8==0
            d=dict(coefficients=cs,t_count=len(cs),no_logical_phase_pairs=no_pairs,seconds=self.wall_time,objective=self.objective_value,bound=self.best_objective_bound)
            (HERE/f'phase_support_{tag}.json').write_text(json.dumps(d,indent=2)+'\n')
            print(json.dumps(d),flush=True)
    result=solver.solve(model,Found())
    print('status',solver.status_name(result),'bound',solver.best_objective_bound,flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--seconds',type=float,default=120);p.add_argument('--allow-pairs',action='store_true');a=p.parse_args();run(a.seconds,not a.allow_pairs)
