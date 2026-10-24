"""Joint injection-network and full-circuit timing CP-SAT model."""
import os,sys,json,re,argparse
from pathlib import Path
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(OUT),str(OUT/'inputs'),str(ROOT/'work/lanes/EVAL')]
import schedule as S
from util import native_times
from schedules import placement,write
from exact2 import Eval
from ortools.sat.python import cp_model

def main(a):
    src=(OUT/'inputs/v17a.qasm').read_text();h,r,tail=S.qasm_ops(src);units=S.fold_units(r);old=native_times(src,units)
    cells=[0,1,2,3,4,7,8,9,10,13,14,15,19];data=[0,19,7,4,3,15,8];n=len(cells);D=a.depth
    gens=[[0,2,4,6],[1,2,5,6],[3,4,5,6],list(range(7))]
    target=[[int(q in [data[i]for i in g])for g in gens]for q in cells]
    edges=[(c,t)for c in range(n)for t in range(n)if abs(cells[c]//6-cells[t]//6)+abs(cells[c]%6-cells[t]%6)==1]
    m=cp_model.CpModel();bits=[[[m.new_bool_var(f'z{l}_{q}_{k}')for k in range(4)]for q in range(n)]for l in range(D+1)]
    gates=[[m.new_bool_var(f'g{l}_{c}_{t}')for c,t in edges]for l in range(D)]
    zero=[m.new_bool_var(f'zero{q}')for q in range(n)];magic=[m.new_bool_var(f'magic{q}')for q in range(n)]
    m.add(sum(zero)==3);m.add(sum(magic)==1)
    for q in range(n):
        m.add(sum(bits[0][q][:3])>=1).only_enforce_if(zero[q]);m.add(sum(bits[0][q][:3])==0).only_enforce_if(zero[q].Not())
        m.add(magic[q]+zero[q]<=1);m.add(bits[0][q][3]==magic[q]).only_enforce_if(zero[q].Not())
        for k in range(4):m.add(bits[-1][q][k]==target[q][k])
    for l in range(D):
        for q in range(n):
            m.add(sum(gates[l][e]for e,(c,t)in enumerate(edges)if q in(c,t))<=1)
            none=m.new_bool_var(f'none{l}_{q}');m.add(none+sum(gates[l][e]for e,(c,t)in enumerate(edges)if c==q)==1)
            for k in range(4):m.add(bits[l+1][q][k]==bits[l][q][k]).only_enforce_if(none)
        for e,(c,t)in enumerate(edges):
            for k in range(4):m.add_allowed_assignments([bits[l][c][k],bits[l][t][k],bits[l+1][c][k]],[(0,0,0),(0,1,1),(1,0,1),(1,1,0)]).only_enforce_if(gates[l][e])
    removed={i for i,u in enumerate(units)if old[i]<=10 or(old[i]==11 and u.name=='CX')or(old[i]==12 and u.lines==['cx q[10],q[4];'])}
    keep=[i for i in range(len(units))if i not in removed];us=[units[i]for i in keep]
    tv=[m.new_int_var(0,65,f't{i}')for i in keep];end=m.new_int_var(0,65,'end');m.add_max_equality(end,tv)
    last={};first={}
    for i,u in enumerate(us):
        for q in u.qs:
            if q in last:m.add(tv[i]>tv[last[q]])
            else:first[q]=i
            last[q]=i
    for l,layer in enumerate(gates):
        for e,(c,t)in enumerate(edges):
            for q in (cells[c],cells[t]):
                if q in first:m.add(tv[first[q]]>=l+3).only_enforce_if(layer[e])
    for q in cells:
        if q in first:m.add(tv[first[q]]>=2).only_enforce_if(magic[cells.index(q)])
    # Timing is part of the network objective: minimize makespan, then CX,
    # then keep the pre-stage gates as late as dependencies allow.
    pre=[j for j,i in enumerate(keep)if old[i]<=32]
    m.minimize(1000000*end+1000*sum(g for layer in gates for g in layer)-sum(tv[j]for j in pre))
    witness=json.loads((OUT/'encoder_d7_s0.solver.json').read_text())
    for q in range(n):m.add_hint(zero[q],int(cells[q]in witness['zero']));m.add_hint(magic[q],int(cells[q]==witness['T_site']))
    for l,layer in enumerate(gates):
        for e,(c,t)in enumerate(edges):m.add_hint(layer[e],int(l<len(witness['network'])and [cells[c],cells[t]]in witness['network'][l]))
    s=cp_model.CpSolver();s.parameters.num_search_workers=a.workers;s.parameters.random_seed=a.seed;s.parameters.max_time_in_seconds=a.seconds
    st=s.solve(m);row=dict(status=s.status_name(st),wall=s.wall_time,objective=s.objective_value,bound=s.best_objective_bound,depth=D,seed=a.seed)
    tag=f'joint_d{D}_s{a.seed}'
    if st in(cp_model.OPTIMAL,cp_model.FEASIBLE):
        net=[[(cells[c],cells[t])for e,(c,t)in enumerate(edges)if s.value(gates[l][e])]for l in range(D)]
        zs=[cells[q]for q in range(n)if s.value(zero[q])];tq=next(cells[q]for q in range(n)if s.value(magic[q]));row.update(network=net,zero=zs,T_site=tq,cx=sum(map(len,net)),solver_end=s.value(end))
        used=sorted({tq,*zs,*[q for layer in net for e in layer for q in e]});nu=[];nt=[]
        for q in used:
            ls=[f'measure q[{q}] -> c[{39+zs.index(q)}];']if q in zs else[f'reset q[{q}];',f'h q[{q}];']
            firstgate=min([l+2 for l,L in enumerate(net)if any(q in e for e in L)]or[D+2]);nu.append(S.Unit(ls,[]));nt.append(0 if q==tq else firstgate-1)
        nu.append(S.Unit([f't q[{tq}];'],[]));nt.append(1)
        for l,L in enumerate(net):
            for c,t in L:nu.append(S.Unit([f'cx q[{c}],q[{t}];'],[]));nt.append(l+2)
        nu+=us;nt+=[s.value(t)for t in tv]
        # Sort by the solved times before constructing the per-wire ALAP DAG.
        order=sorted(range(len(nu)),key=lambda i:(nt[i],i));nu=[nu[i]for i in order]
        times=placement(nu,'alap')
        meta=dict(data_qubits=[0,20,7,10,3,22,21],injection_cx=row['cx'],joint_synthesis=row)
        stem=write('v17a',tag,times,nu,h,tail,meta)
        try:ev=Eval(stem.with_suffix('.qasm').read_text(),meta['data_qubits']);row.update(correct=True,c1=float(ev.fp@ev.n_single))
        except Exception as ex:row.update(correct=False,error=str(ex))
    (OUT/(tag+'.solver.json')).write_text(json.dumps(row,indent=2)+'\n');print(json.dumps(row),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--depth',type=int,default=7);p.add_argument('--seed',type=int,default=0);p.add_argument('--seconds',type=float,default=120);p.add_argument('--workers',type=int,default=2);main(p.parse_args())
