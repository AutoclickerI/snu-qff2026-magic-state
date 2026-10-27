"""Independent Stim oracle for the lane-local native S/Sdg propagation."""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import hashlib,json,random,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'work/tools'))
import stim
import frontend_clifford as f
from qtools.version import EVALUATOR_VERSION,evaluator_version

def pauli(qs,chars):
    p=stim.PauliString(36)
    for q,ch in zip(qs,chars):p[q]=ch
    return p

def compact(p):
    xs,zs=p.to_numpy();x=sum(int(v)<<i for i,v in enumerate(xs));z=sum(int(v)<<i for i,v in enumerate(zs))
    return x,z

def from_compact(v):
    x,z,co=v;p=stim.PauliString(36)
    for q in range(36):p[q]='I' if not ((x|z)>>q&1) else ('Y' if (x&z)>>q&1 else 'X' if x>>q&1 else 'Z')
    co=complex(co)*((-1j)**((x&z).bit_count()))
    assert abs(co.imag)<1e-12 and abs(abs(co.real)-1)<1e-12
    return p*(1 if co.real>0 else -1)

def main():
    st=time.perf_counter();rng=random.Random(82117);f.DATA=list(range(7));faults=observables=0
    edges=[(q,q+1) for q in range(36) if q%6<5]+[(q,q+6) for q in range(30)]
    for seed in range(20):
        ops=[];tab=stim.Tableau(36);inverses=[tab.inverse()]
        for t in range(64):
            kind=rng.choice(['H','S','SDG','CX'])
            qs=tuple(rng.choice(edges)) if kind=='CX' else (rng.randrange(36),)
            if kind=='CX' and rng.randrange(2):qs=tuple(reversed(qs))
            ops.append(f.Op(kind,qs,t))
            tab.append(stim.Tableau.from_named_gate({'SDG':'S_DAG'}.get(kind,kind)),list(qs))
            inverses.append(tab.inverse())
        model=f.make_model(ops,[])
        native,_=f.native_text(ops);prog,blocks=f.noise_blocks(native,.001,first_order=True)
        gatepos=[block.index(ins.text) for ins,block in zip(prog,blocks)]
        for fault in model.faults:
            i=fault['ins'];after=fault['jl']>gatepos[i]
            p=inverses[i+int(after)](pauli(fault['qs'],fault['pauli']))
            assert compact(p)==(fault['x'],fault['z']),(seed,fault,p)
            faults+=1
        for key,v in model.Q.items():
            typ,a,b=key;p=stim.PauliString(36)
            for j,support in enumerate(f.SUPPORTS):
                if a>>j&1:p*=pauli(sorted(support),'X'*4)
                if b>>j&1:p*=pauli(sorted(support),'Z'*4)
            p*=pauli(range(7),typ*7)
            expected=inverses[-1](p)
            assert from_compact(v)==expected,(seed,key,from_compact(v),expected)
            observables+=1
    assert evaluator_version()==EVALUATOR_VERSION
    out=dict(ok=True,random_clifford_circuits=20,native_gates_per_circuit=64,
        fault_propagations_compared=faults,signed_observables_compared=observables,
        oracle=f'Stim {stim.__version__} inverse Clifford tableaux',
        shared_evaluator_version=EVALUATOR_VERSION,
        frontend_sha256=hashlib.sha256(Path(f.__file__).read_bytes()).hexdigest(),
        seconds=time.perf_counter()-st)
    Path(__file__).with_name('clifford_frontend_verification.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2),flush=True)

if __name__=='__main__':main()
