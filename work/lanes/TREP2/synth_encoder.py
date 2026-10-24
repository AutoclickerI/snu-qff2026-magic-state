"""Synthesize the complete one-T injection encoder as a grid parity network.

Backward Z constraints specify all three Steane code checks and logical Z.
At input the checks span three computational-basis preparations; logical Z
has exactly one component on the remaining |+> inputs, identifying the T site.
Ancillas have unrestricted product |+> outputs and are reset by the retained
injection verification. Full-fault checks decide whether this freedom is useful.
"""
import os,sys,json,re,argparse
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(OUT/'inputs'),str(ROOT/'work/lanes/EVAL')]
import schedule as S
from util import native_times
from exact2 import Eval
from ortools.sat.python import cp_model

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--depth',type=int,default=7);ap.add_argument('--seed',type=int,default=0);ap.add_argument('--seconds',type=float,default=120);ap.add_argument('--workers',type=int,default=8);a=ap.parse_args()
    src=(OUT/'inputs/v17a.qasm').read_text();head,raw,tail=S.qasm_ops(src);units=S.fold_units(raw);times=native_times(src,units)
    cells=[0,1,2,3,4,7,8,9,10,13,14,15,19];data=[0,19,7,4,3,15,8];n=len(cells);D=a.depth
    gens=[[0,2,4,6],[1,2,5,6],[3,4,5,6],list(range(7))]
    target=[[int(q in [data[i]for i in g])for g in gens]for q in cells]
    edges=[(c,t)for c in range(n)for t in range(n)if abs(cells[c]//6-cells[t]//6)+abs(cells[c]%6-cells[t]%6)==1]
    m=cp_model.CpModel();bits=[[[m.new_bool_var(f'z_{l}_{q}_{k}')for k in range(4)]for q in range(n)]for l in range(D+1)]
    gates=[[m.new_bool_var(f'g_{l}_{c}_{t}')for c,t in edges]for l in range(D)]
    zero=[m.new_bool_var(f'zero{q}')for q in range(n)];magic=[m.new_bool_var(f'magic{q}')for q in range(n)]
    m.add(sum(zero)==3);m.add(sum(magic)==1)
    for q in range(n):
        m.add(sum(bits[0][q][:3])>=1).only_enforce_if(zero[q]);m.add(sum(bits[0][q][:3])==0).only_enforce_if(zero[q].Not())
        m.add(magic[q]+zero[q]<=1);m.add(bits[0][q][3]==magic[q]).only_enforce_if(zero[q].Not())
        for k in range(4):m.add(bits[-1][q][k]==target[q][k])
    for l in range(D):
        for q in range(n):
            m.add(sum(gates[l][e]for e,(c,t)in enumerate(edges)if q in (c,t))<=1)
            none=m.new_bool_var(f'none{l}_{q}');m.add(none+sum(gates[l][e]for e,(c,t)in enumerate(edges)if c==q)==1)
            for k in range(4):m.add(bits[l+1][q][k]==bits[l][q][k]).only_enforce_if(none)
        for e,(c,t)in enumerate(edges):
            for k in range(4):m.add_allowed_assignments([bits[l][c][k],bits[l][t][k],bits[l+1][c][k]],[(0,0,0),(0,1,1),(1,0,1),(1,1,0)]).only_enforce_if(gates[l][e])
    m.minimize(sum(gates[l][e]*(100+l)for l in range(D)for e in range(len(edges))))
    s=cp_model.CpSolver();s.parameters.max_time_in_seconds=a.seconds;s.parameters.num_search_workers=a.workers;s.parameters.random_seed=a.seed
    status=s.solve(m);tag=f'encoder_d{D}_s{a.seed}';row=dict(status=s.status_name(status),depth=D,wall=s.wall_time)
    if status in (cp_model.OPTIMAL,cp_model.FEASIBLE):
        network=[[(cells[c],cells[t])for e,(c,t)in enumerate(edges)if s.value(gates[l][e])]for l in range(D)]
        zs=[cells[q]for q in range(n)if s.value(zero[q])];tq=next(cells[q]for q in range(n)if s.value(magic[q]));row.update(network=network,zero=zs,T_site=tq,cx=sum(map(len,network)))
        old={i for i,u in enumerate(units)if times[i]<=10 or (times[i]==11 and u.name=='CX') or (times[i]==12 and u.lines==['cx q[10],q[4];'])}
        # Retain every verification and double-cat operation, shifting them together.
        shift=D-9;newunits=[];newtimes=[]
        for i,u in enumerate(units):
            if i not in old:newunits.append(u);newtimes.append(times[i]+shift)
        for q in cells:
            lines=[f'measure q[{q}] -> c[{39+zs.index(q)}];']if q in zs else [f'reset q[{q}];',f'h q[{q}];']
            first=min([l+2 for l,L in enumerate(network)if any(q in e for e in L)]or[D+2])
            newunits.append(S.Unit(lines,[]));newtimes.append(0 if q==tq else first-1)
        newunits.append(S.Unit([f't q[{tq}];'],[]));newtimes.append(1)
        for l,L in enumerate(network):
            for c,t in L:newunits.append(S.Unit([f'cx q[{c}],q[{t}];'],[]));newtimes.append(l+2)
        text=S.emit(head,newunits,newtimes,tail);d=[0,20,7,10,3,22,21]
        (OUT/(tag+'.qasm')).write_text(text);(OUT/(tag+'.json')).write_text(json.dumps(dict(data_qubits=d,R=47+shift,pre_end=32+shift,**row),indent=2)+'\n')
        try:
            ev=Eval(text,d);row.update(correct=True,c1=float((ev.fp*ev.n_single).sum()))
        except Exception as ex:row.update(correct=False,error=str(ex))
    print(json.dumps(row,indent=2),flush=True);(OUT/(tag+'.solver.json')).write_text(json.dumps(row,indent=2)+'\n')

if __name__=='__main__':main()
