"""Warm-start the relocated B/C resource while preserving the full circuit's guard slots.
Every improving CP solution is built and priced by the all-orders evaluator.
"""
import argparse,copy,hashlib,json,sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from ortools.sat.python import cp_model
from qedit import load,QRE
from borrow import save,HERE
from price import price

ap=argparse.ArgumentParser();ap.add_argument('base');ap.add_argument('tag');ap.add_argument('--seconds',type=float,default=240);ap.add_argument('--workers',type=int,default=8);ap.add_argument('--jobs',type=int,default=4);ap.add_argument('--seed',type=int,default=1);ap.add_argument('--wz',type=int,default=2);ap.add_argument('--wcx',type=int,default=3);a=ap.parse_args()
base=HERE/'builds'/a.base;c=load(str(base));metadata=json.loads(base.with_suffix('.json').read_text())
lay=json.loads((HERE/'layouts/r46_2.json').read_text());B,C=lay['B'],lay['C'];cells=B+C
state=json.loads((HERE/'enc/r46_2_bc_s1.json').read_text());T0=state['T0'];depth=len(state['ops'])
old={(T0+t,u,v) for t,ss in enumerate(state['ops']) for u,v in ss}
remaining=copy.deepcopy(c)
for t,u,v in old:remaining.segs[t].remove([f'cx q[{u}],q[{v}];'])
first={q:min(t for t,u,v in old if q in (u,v)) for q in cells}
init={}
for q in cells:
    opts=[(t,g) for t,ss in enumerate(c.segs[:first[q]]) for g in ss if g[0]==f'reset q[{q}];']
    init[q]=max(opts,key=lambda z:z[0])[0]
avail={q:max(0,init[q]+1-T0) for q in cells}
source=(HERE/'enc/bc_template.py').read_text().replace('if any(q in (18, 31, 34, 35) for q in e) and t >= D - 1:','if any(q in helpers and q in (18, 31, 34, 35) for q in e) and t >= D - 1:')
ns={'__name__':'warm_bc_model'};exec(compile(source,str(HERE/'enc/bc_template.py'),'exec'),ns);ns.update(B=B,C=C,CELLS=cells)
m,sel,x,nz,E,ncx,zexp=ns['build'](depth,avail,robust=True,w_cx=a.wcx,w_z=a.wz)
piv={int(q):(v if isinstance(v,int) else sum(b<<j for j,b in enumerate(v))) for q,v in state['pivots'].items()}
for q in cells:
    for j in range(3):m.Add(x[0][q][j]==((piv.get(q,0)>>j)&1))
ref={q:piv.get(q,0) for q in cells};refs=[]
for ss in state['ops']:
    refs.append(dict(ref))
    for u,v in ss:ref[v]^=ref[u]
def pure_plus(rows,q):
    vecs=[sum(((rows[v]>>j)&1)<<i for i,v in enumerate(cells)) for j in range(3)]
    span={0}
    for z in vecs:span|={v^z for v in list(span)}
    return 1<<cells.index(q) in span
pins=[]
for t in range(T0,T0+depth):
    busy=remaining.qubits_at(t)
    for e in E:
        if set(e)&busy:m.Add(sel[t-T0][e]==0)
        m.AddHint(sel[t-T0][e],int((t,*e) in old))
    for g in remaining.segs[t]:
        if not g[0].startswith('cx'):continue
        u,v=map(int,QRE.findall(g[0]));rows=refs[t-T0]
        if u in cells and t>init[u] and rows[u]==0:
            for j in range(3):m.Add(x[t-T0][u][j]==0)
            pins.append((t,u,'zero'))
        elif v in cells and t>init[v] and pure_plus(rows,v):
            for q in cells:
                for j in range(3):m.Add(x[t-T0][q][j]==((rows[q]>>j)&1))
            pins.append((t,v,'plus-span'))
executor=ThreadPoolExecutor(a.jobs);futures=[];states=[]
class Callback(cp_model.CpSolverSolutionCallback):
    def on_solution_callback(self):
        ops=[[list(e) for e in E if self.Value(sel[t][e])] for t in range(depth)]
        if ops==state['ops']:return
        idx=len(states);name=f'{a.tag}_{idx:03d}';candidate=copy.deepcopy(remaining)
        for t,ss in enumerate(ops,T0):
            for u,v in ss:candidate.segs[t].append([f'cx q[{u}],q[{v}];'])
        out=dict(T0=T0,ops=ops,pivots=state['pivots'],cx=self.Value(ncx),zexp=self.Value(zexp),objective=self.ObjectiveValue(),base=a.base,guard_constraints=pins)
        sf=HERE/'enc'/f'{name}.json';sf.write_text(json.dumps(out,indent=2)+'\n')
        stem=save(candidate,name,dict(family='warm B/C refinement',base=a.base,state=str(sf)))
        meta=json.loads(stem.with_suffix('.json').read_text());meta['data_qubits']=metadata['data_qubits'];stem.with_suffix('.json').write_text(json.dumps(meta,indent=2)+'\n')
        states.append(name);futures.append(executor.submit(price,stem,1))
        print(json.dumps(dict(built=name,cx=out['cx'],zexp=out['zexp'],objective=out['objective'])),flush=True)
s=cp_model.CpSolver();s.parameters.max_time_in_seconds=a.seconds;s.parameters.num_workers=a.workers;s.parameters.random_seed=a.seed;s.parameters.cp_model_presolve=False
status=s.Solve(m,Callback());executor.shutdown(wait=True)
results=[f.result() for f in futures];good=[r for r in results if r]
out=dict(status=s.StatusName(status),seconds=s.WallTime(),states=states,priced=len(good),best=min(good,key=lambda r:r['J_tau']) if good else None,pins=pins)
(HERE/'logs'/f'{a.tag}.warm_result.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k not in ['best','pins']}),flush=True)
