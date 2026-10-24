"""Grid CP-SAT synthesis of the Clifford resource immediately before the first T.

Output constraints fix the complete CSS stabilizer state, allowing arbitrary
bases for its six-dimensional X space. This changes the physical parity network.
"""
import os,sys,json,re,argparse
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]; OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'work/lanes/SCHED'),str(ROOT/'work/lanes/EVAL')]
import schedule as S
from exact2 import Eval
from ortools.sat.python import cp_model
from util import native_times

def xor_equal(m,vs,bit):
    m.add_bool_xor(list(vs)+([] if bit else [True]))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--depth',type=int,default=5);ap.add_argument('--seed',type=int,default=0);ap.add_argument('--seconds',type=float,default=60);ap.add_argument('--workers',type=int,default=8);ap.add_argument('--full',action='store_true');ap.add_argument('--zprep',action='store_true');a=ap.parse_args()
    src=(OUT/'inputs/v17a.qasm').read_text(); head,raw,tail=S.qasm_ops(src);units=S.fold_units(raw);times=native_times(src,units)
    cells=[1,2,3,7,8,13,14,15];zero=[2,14];plus=[q for q in cells if q not in zero];n=len(cells);r=n if a.full else len(plus)
    initial=[(1<<i if a.full else (0 if q in zero else 1<<plus.index(q))) for i,q in enumerate(cells)]
    target=initial[:];old=[];init={}
    for i,u in enumerate(units):
        if times[i]>=7:continue
        if set(u.qs)<=set(cells):
            if u.name=='CX':
                c,t=map(int,re.findall(r'q\[(\d+)\]',u.lines[0]));target[cells.index(t)]^=target[cells.index(c)];old.append(i)
            else:init[u.qs[0]]=i;old.append(i)
    checks=[s for s in range(1,1<<n) if __import__('functools').reduce(int.__xor__,[target[i] for i in range(n) if s>>i&1],0)==0]
    if a.zprep:r=2
    edges=[(i,j) for i,q in enumerate(cells) for j,v in enumerate(cells) if abs(q//6-v//6)+abs(q%6-v%6)==1]
    m=cp_model.CpModel(); D=a.depth
    bits=[[[m.new_bool_var(f'b_{l}_{q}_{k}') for k in range(r)]for q in range(n)]for l in range(D+1)]
    gates=[[m.new_bool_var(f'g_{l}_{i}_{j}')for i,j in edges]for l in range(D)]
    if a.zprep:
        for k in range(r):m.add(sum(bits[0][q][k] for q in range(n))==1)
        for q in range(n):m.add(sum(bits[0][q])<=1)
    else:
        for q in range(n):
            for k in range(r):m.add(bits[0][q][k]==((initial[q]>>k)&1))
    for l in range(D):
        for q in range(n):
            m.add(sum(gates[l][e] for e,(c,t) in enumerate(edges) if q in (c,t))<=1)
            incoming=[gates[l][e] for e,(c,t) in enumerate(edges) if (c if a.zprep else t)==q]
            none=m.new_bool_var(f'none_{l}_{q}');m.add(sum(incoming)+none==1)
            for k in range(r):m.add(bits[l+1][q][k]==bits[l][q][k]).only_enforce_if(none)
        for e,(c,t) in enumerate(edges):
            if a.zprep:c,t=t,c
            for k in range(r):
                m.add_allowed_assignments([bits[l][c][k],bits[l][t][k],bits[l+1][t][k]],[(0,0,0),(0,1,1),(1,0,1),(1,1,0)]).only_enforce_if(gates[l][e])
    if a.zprep:
        m.add_allowed_assignments([bits[-1][q][k] for q in range(n) for k in range(2)],
                                 [[(s>>q)&1 for q in range(n) for s in pair]for pair in __import__('itertools').permutations(checks,2)])
    elif a.full:
        for q in range(n):
            for k in range(r):m.add(bits[-1][q][k]==((target[q]>>k)&1))
    else:
        for s in checks:
            for k in range(r):xor_equal(m,[bits[-1][q][k]for q in range(n)if s>>q&1],0)
    # CX count and use of the congested cells 1,2,13,14.
    m.minimize(sum(g*(100+int(cells[c]in(1,2,13,14))+int(cells[t]in(1,2,13,14))) for layer in gates for g,(c,t)in zip(layer,edges)))
    solver=cp_model.CpSolver();solver.parameters.max_time_in_seconds=a.seconds;solver.parameters.num_search_workers=a.workers;solver.parameters.random_seed=a.seed
    status=solver.solve(m);tag=f'init_{"zprep" if a.zprep else "unitary" if a.full else "state"}_d{D}_s{a.seed}'
    result=dict(status=solver.status_name(status),depth=D,seed=a.seed,wall=solver.wall_time,old_cx=sum(units[i].name=='CX'for i in old))
    if status in (cp_model.FEASIBLE,cp_model.OPTIMAL):
        network=[[(cells[c],cells[t]) for g,(c,t)in zip(layer,edges)if solver.value(g)]for layer in gates]; result['network']=network;result['cx']=sum(map(len,network))
        # Keep the unrelated early q9/q10 subnetwork. Shift the whole suffix by the saved depth.
        shift=D+1-7;newunits=[];newtimes=[]
        for i,u in enumerate(units):
            if i in old:continue
            t=max(0,times[i]+shift)
            newunits.append(u);newtimes.append(t)
        first={q:min([l+1 for l,L in enumerate(network)if any(q in e for e in L)] or [D+1])for q in cells}
        newzero=[cells[q] for q in range(n)if a.zprep and sum(solver.value(x)for x in bits[0][q])]
        result['initial_zero']=newzero if a.zprep else zero
        for q,i in init.items():
            if a.zprep:
                lines=[f'measure q[{q}] -> c[{39+newzero.index(q)}];'] if q in newzero else [f'reset q[{q}];',f'h q[{q}];']
                newunits.append(S.Unit(lines,[]))
            else:newunits.append(units[i])
            newtimes.append(first[q]-1)
        for l,L in enumerate(network):
            for c,t in L:newunits.append(S.Unit([f'cx q[{c}],q[{t}];'],[]));newtimes.append(l+1)
        text=S.emit(head,newunits,newtimes,tail)
        data=[0,20,7,10,3,22,21]
        (OUT/(tag+'.qasm')).write_text(text);(OUT/(tag+'.json')).write_text(json.dumps(dict(data_qubits=data,R=47+shift,pre_end=32+shift,form='f00_0',**result),indent=2)+'\n')
        try:
            ev=Eval(text,data);result['c1']=float((ev.fp*ev.n_single).sum());result['correct']=True
        except Exception as ex:result['error']=str(ex);result['correct']=False
    print(json.dumps(result,indent=2),flush=True)
    (OUT/(tag+'.solver.json')).write_text(json.dumps(result,indent=2)+'\n')

if __name__=='__main__':main()
