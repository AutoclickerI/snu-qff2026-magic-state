"""Score exact resource phase symmetries in their complete native circuit.

Candidates contain physical S/Sdg pulses in existing idle slots. The input
certificate is only a generator: official raw-state replay and a complete
mixed-Pauli single-fault audit independently gate the order-two calculation.
"""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='1'
import argparse,contextlib,copy,io,json,sys,time
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'work/tools'))
sys.path.insert(0,str(ROOT/'work/lanes/END2_20261027'))
sys.path.insert(0,str(ROOT/'work/lanes/PREFIX2_20261027'))
sys.path.insert(0,str(ROOT/'work/lanes/REBUILD20261027'))
from qtools import write_stem
from qtools.validity import raw_check
from joint import emit
import frontend_axis as f
import record_contract,pairs


def score(job):
    base,candidate,folder=job;base=Path(base);folder=Path(folder)
    data=json.loads(base.with_suffix('.json').read_text())['data_qubits']
    ops,dets=f.parse_current(base.with_suffix('.qasm').read_text())
    occupied={(o.time,q) for o in ops for q in o.qs}
    result=dict(name=candidate['name'],operations=candidate['operations'])
    for row in candidate['operations']:
        assert row['kind'] in ('S','SDG')
        assert len(row['qs'])==1
        key=(row['time'],row['qs'][0])
        if key in occupied:
            return dict(**result,excluded='occupied pulse slot',slot=key)
        occupied.add(key)
        ops.append(f.Op(row['kind'],tuple(row['qs']),row['time']))
    ops.sort(key=lambda o:o.time)
    text=emit(ops,dets);raw=raw_check(text,data)
    result['raw']=raw
    stem=write_stem(text,data,folder,candidate['name'],source=dict(parent=str(base),phase_symmetry=candidate,
                   noise_scope='All gates noisy; native pulses replace existing idle channels.'))
    result['stem']=str(stem)
    if raw['ok']:
        f.DATA=data;record_contract.fa=f;pairs.fa=f
        single=record_contract.singles(f.make_model(*f.parse_current(text)))
        result.update(c1=single['c1'],harmful_single_count=len(single['harmful_faults']))
        if single['c1']<1e-10:
            with contextlib.redirect_stdout(io.StringIO()):
                pair=pairs.audit(stem,stem.with_suffix('.pairs.json'))
            result['c2']=pair['c2']
    return result


def main():
    ap=argparse.ArgumentParser();ap.add_argument('base',type=Path);ap.add_argument('candidates',type=Path)
    ap.add_argument('--output',type=Path,default=HERE/'phase_screen')
    ap.add_argument('--workers',type=int,default=2);ap.add_argument('--start',type=int,default=0)
    ap.add_argument('--limit',type=int)
    args=ap.parse_args();doc=json.loads(args.candidates.read_text())
    candidates=doc['candidates'] if isinstance(doc,dict) else doc
    candidates=candidates[args.start:None if args.limit is None else args.start+args.limit]
    args.output.mkdir(parents=True,exist_ok=True)
    results=[];start=time.perf_counter()
    jobs=[(str(args.base.resolve()),r,str(args.output.resolve())) for r in candidates]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for result in pool.map(score,jobs):
            results.append(result)
            (args.output/'results.json').write_text(json.dumps(dict(base=str(args.base),candidates_file=str(args.candidates),
                seconds=time.perf_counter()-start,results=results),indent=2)+'\n')
            print(json.dumps({k:result.get(k) for k in ('name','c1','c2','excluded')}),flush=True)
    print(json.dumps(dict(completed=len(results),seconds=time.perf_counter()-start)),flush=True)


if __name__=='__main__':main()
