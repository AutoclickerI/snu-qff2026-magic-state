"""Rebuild the native phase improvement from the pinned literal incumbent."""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='1'
import argparse,hashlib,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'work/tools'))
sys.path.insert(0,str(ROOT/'work/lanes/END2_20261027'))
sys.path.insert(0,str(ROOT/'work/lanes/REBUILD20261027'))
from qtools.validity import raw_check
from joint import emit
import frontend_axis as f
import record_contract
from axis_echo import exact

BASE_SHA='ac2d9dfbfb4967baacf85a25f2a1eaac35dd7039abe2069dc858cd5a5f4ca5cd'
OUTPUT_SHA='e29ed657cbfcdacb4c41e3cbd07e3d1307f1a7f19972785c8ab25c616d1aa8d8'
LATE_SHA='bcd6a3fdb6133c5b687993fb10c57c002e13f3e873f05981c48100ba10065b08'


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--price',action='store_true')
    ap.add_argument('--late',action='store_true',help='Use the slightly better S12@45 placement.')
    args=ap.parse_args();positive_time=45 if args.late else 39
    expected=LATE_SHA if args.late else OUTPUT_SHA
    base=ROOT/'work/lanes/MAIN/v37j'
    source=base.with_suffix('.qasm').read_bytes()
    assert hashlib.sha256(source).hexdigest()==BASE_SHA,'Different baseline'
    data=json.loads(base.with_suffix('.json').read_text())['data_qubits']
    ops,dets=f.parse_current(source.decode())
    assert all(not ((o.time==39 and 5 in o.qs) or (o.time==positive_time and 12 in o.qs)) for o in ops),'Pulse slot occupied'
    ops += [f.Op('SDG',(5,),39),f.Op('S',(12,),positive_time)]
    ops.sort(key=lambda o:o.time)
    text=emit(ops,dets);sha=hashlib.sha256(text.encode()).hexdigest()
    assert sha==expected,(sha,expected)
    target=HERE/('release_phase/native_incumbent_phase_late' if args.late else 'release_phase/native_incumbent_phase')
    assert target.with_suffix('.qasm').read_text()==text,'Release file differs from reconstruction'
    raw=raw_check(text,data);assert raw['ok'],raw
    f.DATA=data;record_contract.fa=f
    singles=record_contract.singles(f.make_model(*f.parse_current(text)))
    assert singles['c1']<1e-10,singles
    result=dict(baseline_sha256=BASE_SHA,qasm_sha256=sha,data_qubits=data,raw=raw,
        singles=singles,cx=sum(o.kind=='CX' for o in ops),ticks=max(o.time for o in ops)+1,
        changes=[dict(kind='SDG',qubit=5,tick=39),dict(kind='S',qubit=12,tick=positive_time)],
        detector_policy='Exactly the original detector rows and measurement records.',
        noise_scope='Real noisy native Clifford pulses replace existing idle channels at the same clock.',
        frontend_sha256=hashlib.sha256(Path(f.__file__).read_bytes()).hexdigest())
    if args.price:result['exact']=exact(target)
    receipt=HERE/('release_phase/reproduction_late.json' if args.late else 'release_phase/reproduction.json')
    receipt.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
