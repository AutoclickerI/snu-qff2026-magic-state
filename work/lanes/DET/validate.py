from search import *
sys.path.insert(0,str(ROOT/'work'))
import tprep
from fast_check import check as fast_check

def emit(name,tag,kernel):
    stem=TARGETS[name]
    text=stem.with_suffix('.qasm').read_text()
    meta=json.loads(stem.with_suffix('.json').read_text())
    space=json.loads((HERE/f'{name}_space.json').read_text())
    records=records_for(kernel,space['full_records'])
    # Keep the original unchanged for the baseline paired MC comparison.
    body=text if tag=='base' else qasm_for(text,records,space)
    meta.update(detector_source=str(stem.relative_to(ROOT)),kernel=kernel,
                detector_rank=len(records),change=tag)
    out=HERE/f'{name}_{tag}'
    out.with_suffix('.qasm').write_text(body)
    out.with_suffix('.json').write_text(json.dumps(meta,indent=2))
    return out

def result(rep):
    return dict(passed=rep.passed,format_ok=rep.format_ok,class_ok=rep.class_ok,
                correct_ok=rep.correct_ok,acceptance_ok=rep.acceptance_ok,
                score=rep.score,sem=rep.sem,acceptance=rep.acceptance,
                frame=rep.frame,errors=rep.format_errors+rep.correctness_errors,
                class_error=rep.class_error)

def validate(stems,mc=False,procs=22):
    fn=HERE/('mc.jsonl' if mc else 'checks.jsonl')
    done=set()
    if fn.exists():
        done={(r['candidate'],r['seed']) for r in map(json.loads,fn.read_text().splitlines())}
    for stem in stems:
        if isinstance(stem,str):
            stem=HERE/stem
        text=stem.with_suffix('.qasm').read_text()
        data=json.loads(stem.with_suffix('.json').read_text())['data_qubits']
        for seed in ((0,1000,2000) if mc else (0,)):
            if (stem.name,seed) in done:
                continue
            t=time.time()
            if mc:
                rep=fast_check(text,data,shots=10**8,seed=seed,procs=procs)
            else:
                rep=tprep.check(text,data,shots=10**6,seed=seed)
            out=result(rep);out.update(candidate=stem.name,seed=seed,
                    shots=10**8 if mc else 10**6,seconds=time.time()-t)
            with fn.open('a') as f:
                f.write(json.dumps(out)+'\n')
            print(json.dumps(out),flush=True)
            assert rep.passed,str(rep)

if __name__=='__main__':
    if sys.argv[1]=='initial':
        stems=[]
        for name,k in [('v12',[256]),('cand2',[64])]:
            stems += [emit(name,'base',[]),emit(name,'drop_c3',k)]
        validate(stems)
    elif sys.argv[1]=='mc':
        validate(sys.argv[2:],mc=True)
    else:
        validate(sys.argv[1:])
