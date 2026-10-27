"""Screen transversal Clifford echoes occupying existing data idle slots.

Both pulses are real native noisy one-qubit gates. The clock is unchanged;
their depolarizing channels replace idle channels of the same strength.
Raw correctness and the fixed decoder's single-fault behavior are checked.
"""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='1'
import argparse,contextlib,copy,hashlib,io,json,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'work/tools'))
sys.path.insert(0,str(ROOT/'work/lanes/END2_20261027'))
sys.path.insert(0,str(ROOT/'work/lanes/PREFIX2_20261027'))
sys.path.insert(0,str(ROOT/'work/lanes/REBUILD20261027'))
import frontend_axis as f
from qtools import write_stem
from qtools.validity import raw_check
from qtools.pricing import _calculate
from qtools.evaluator import sparse_walsh as sw
from joint import emit
import pairs
import record_contract


def exact(stem):
    stem=Path(stem);data=json.loads(stem.with_suffix('.json').read_text())['data_qubits']
    previous=sw.fa,sw.parse_current
    try:
        sw.fa=f;sw.parse_current=f.parse_current
        result=_calculate(stem.with_suffix('.qasm').read_bytes(),data,1,save_basis=False)
    finally:sw.fa,sw.parse_current=previous
    result.update(frontend='lane-local S/Sdg/SX/SXdg with pinned contraction',
                  frontend_sha256=hashlib.sha256(Path(f.__file__).read_bytes()).hexdigest())
    return result


def main():
    ap=argparse.ArgumentParser();ap.add_argument('stem');ap.add_argument('--first',type=int,default=40)
    ap.add_argument('--last',type=int,default=47);ap.add_argument('--price',action='store_true')
    ap.add_argument('--output',type=Path)
    args=ap.parse_args();base=Path(args.stem).resolve()
    data=json.loads(base.with_suffix('.json').read_text())['data_qubits']
    original,dets=f.parse_current(base.with_suffix('.qasm').read_text())
    for t in [args.first,args.last]:
        assert not any(o.time==t and set(o.qs)&set(data) for o in original),('occupied data pulse slot',t)
    pairs.fa=f;record_contract.fa=f;f.DATA=list(data)
    folder=args.output or HERE/'axis_echo';folder.mkdir(parents=True,exist_ok=True)
    with contextlib.redirect_stdout(io.StringIO()):
        control=pairs.audit(base,folder/'control_pairs.json')
    rows=[dict(kind='control',stem=str(base),c2=control['c2'])]
    print(json.dumps(rows[0]),flush=True)
    for gate,inverse in [('H','H'),('S','SDG'),('SDG','S'),('SX','SXDG'),('SXDG','SX')]:
        ops=copy.deepcopy(original)
        ops += [f.Op(gate,(q,),args.first) for q in data]
        ops += [f.Op(inverse,(q,),args.last) for q in data]
        ops.sort(key=lambda o:o.time)
        text=emit(ops,dets);raw=raw_check(text,data)
        stem=write_stem(text,data,folder,gate.lower(),source=dict(base=str(base),pulses=[[gate,args.first],[inverse,args.last]],
                         noise_scope='All native gates, preparation, measurement and idle noise; each pulse occupies a prior idle slot.'))
        result=dict(kind=gate,stem=str(stem),raw=raw,cx=sum(o.kind=='CX'for o in ops),ticks=max(o.time for o in ops)+1)
        if raw['ok']:
            single=record_contract.singles(f.make_model(*f.parse_current(text)))
            result['c1']=single['c1'];result['harmful_single_count']=len(single['harmful_faults'])
            if single['c1']<1e-10:
                with contextlib.redirect_stdout(io.StringIO()):
                    pair=pairs.audit(stem,stem.with_suffix('.pairs.json'))
                result['c2']=pair['c2']
                if args.price and pair['c2']<control['c2']-.1:
                    result['exact']=exact(stem)
        rows.append(result)
        (folder/'results.json').write_text(json.dumps(rows,indent=2)+'\n')
        print(json.dumps(result),flush=True)


if __name__=='__main__':main()
