"""Record native timing, complete judge gates, and physical T-axis fault protection."""
import os,sys,json,itertools,re
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'work/lanes/SCHED'),str(ROOT/'work/lanes/EVAL'),str(ROOT/'work')]
import schedule as S
from util import native_times
from model import Model,Basis,comm
from engine import Engine
import tprep

def main(name):
    stem=OUT/name;text=stem.with_suffix('.qasm').read_text();meta=json.loads(stem.with_suffix('.json').read_text());data=meta['data_qubits']
    m=Model(text,data);e=Engine(m);b=Basis();bf=Basis()
    for x,z,*_ in m.rots:b.add(x);bf.add(x|(z<<m.n))
    def fault(coords):
        x=z=0
        for i in coords:x^=m.rots[i][0];z^=m.rots[i][1]
        d=sum(comm(x,z,q[0],q[1])<<j for j,q in enumerate(m.proj_m));sig=sum(comm(x,z,q[0],q[1])<<j for j,q in enumerate(m.sig_e));acc,nt=e.ntable(0,d)
        return 0.0 if nt is None else float(nt[sig])
    bad1=[i for i in range(15)if fault([i])>1e-12];bad2=[(i,j)for i,j in itertools.combinations(range(15),2)if fault([i,j])>1e-12]
    h,r,t=S.qasm_ops(text);units=S.fold_units(r);times=native_times(text,units)
    R=max(t for u,t in zip(units,times)if u.lines==['cx q[0],q[1];']);pe=max(t for u,t in zip(units,times)if u.name in ('T','TDG'))
    meta.update(R=R,pre_end=pe,native_depth=max(times)+1,full_cx=sum(u.name=='CX'for u in units))
    stem.with_suffix('.json').write_text(json.dumps(meta,indent=2)+'\n')
    preids=set(meta.get('prefix_unit_indices',[i for i,t in enumerate(times)if t<=pe]))
    result=dict(state_rank=len(b.vecs),pauli_rank=len(bf.vecs),axis_coordinates=[b.express(r[0])for r in m.rots],bad_phase_singles=bad1,bad_phase_pairs=bad2,
                commuting=all(comm(a[0],a[1],c[0],c[1])==0 for a,c in itertools.combinations(m.rots,2)),R=R,pre_end=pe,native_depth=max(times)+1,
                full_cx=meta['full_cx'],pre_cx=sum(units[i].name=='CX'for i in preids),
                release={q:max(times[i]for i in preids if q in units[i].qs)+1 for q in [1,6,13,2,9,14]})
    chk=tprep.check(text,data,shots=10**6,seed=0)
    result['check']=dict(passed=chk.passed,format=chk.format_ok,correctness=chk.correct_ok,klass=chk.class_ok,acceptance_ok=chk.acceptance_ok,acceptance=chk.acceptance,score=chk.score,sem=chk.sem,n_2q=chk.n_2q,
                         format_errors=chk.format_errors,correctness_errors=chk.correctness_errors,class_error=chk.class_error)
    (OUT/(name+'.check.json')).write_text(json.dumps(result,indent=2)+'\n');print(name,json.dumps(result),flush=True)

if __name__=='__main__':
    for name in sys.argv[1:]:main(name)
