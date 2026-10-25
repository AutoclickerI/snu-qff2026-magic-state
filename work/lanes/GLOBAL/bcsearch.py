"""BFLAG resource synthesis on the actual cells and release times of a new layout."""
import argparse,json,sys
from pathlib import Path
from rebuild import prefix,HERE

ap=argparse.ArgumentParser();ap.add_argument('label');ap.add_argument('--workers',type=int,default=9);ap.add_argument('--seconds',type=float,default=180);ap.add_argument('--seed',type=int,default=1);ap.add_argument('--reuse',action='store_true');ap.add_argument('--norobust',action='store_true');a=ap.parse_args()
c,lay,release=prefix(a.label)
B,C=lay['B'],lay['C'];cells=B+C
# The original helper-only late-readout restriction must not constrain relocated B/C roles.
source=(HERE/'enc/bc_template.py').read_text().replace('if any(q in (18, 31, 34, 35) for q in e) and t >= D - 1:', 'if any(q in helpers and q in (18, 31, 34, 35) for q in e) and t >= D - 1:')
namespace={'__name__':'global_bc_synth'};exec(compile(source,str(HERE.parent/'BFLAG/synth_bc.py'),'exec'),namespace)
namespace.update(B=B,C=C,CELLS=cells)
T0=31;depth=lay['R']-T0
avail={q:max(0,release[q][0]+(1 if a.reuse and release[q][1] in ['X','Z'] else 2)-T0) for q in cells}
from ortools.sat.python import cp_model
m,sel,x,nz,E,ncx,zexp=namespace['build'](depth,avail,robust=not a.norobust,w_cx=3,w_z=2)
if a.reuse:
    for q in cells:
        t=release[q][0]+1-T0
        if t<0 or t>=depth or release[q][1]=='unknown':continue
        for e in E:
            if q in e:m.Add(sel[t][e]==0).OnlyEnforceIf(nz[0][q] if release[q][1]=='Z' else nz[0][q].Not())
s=cp_model.CpSolver();s.parameters.max_time_in_seconds=a.seconds;s.parameters.num_search_workers=a.workers;s.parameters.random_seed=a.seed;s.parameters.cp_model_presolve=False
st=s.Solve(m);result=dict(status=s.StatusName(st),seconds=s.WallTime())
if st in [cp_model.OPTIMAL,cp_model.FEASIBLE]:
    result.update(ops=[[list(e) for e in E if s.Value(sel[t][e])] for t in range(depth)],pivots={q:[s.Value(b) for b in x[0][q]] for q in cells if s.Value(nz[0][q])},cx=s.Value(ncx),zexp=s.Value(zexp),obj=s.ObjectiveValue(),bound=s.BestObjectiveBound())
result.update(reuse=a.reuse,robust=not a.norobust)
result.update(T0=T0,layout=a.label,avail=avail,source='BFLAG synth_bc.py with dynamic B/C cells and helper restriction fixed')
out=HERE/'enc'/f'{a.label}_bc_s{a.seed}{"_reuse" if a.reuse else ""}{"_clean" if a.norobust else ""}.json';out.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['ops','source']}),flush=True)
