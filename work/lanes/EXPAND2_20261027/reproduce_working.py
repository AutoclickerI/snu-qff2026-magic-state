"""Rebuild the verified incumbent patch from the pinned repository circuit."""
import argparse,hashlib,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'work/tools'))
sys.path.insert(0,str(ROOT/'work/lanes/END2_20261027'))
from qtools import price
from qtools.evaluator import frontend as f
from qtools.validity import raw_check
from acceptance_search import prepare,null_rows,xor_rows
from joint import emit

BASE=ROOT/'work/lanes/MAIN/v37j'
BASE_SHA='ac2d9dfbfb4967baacf85a25f2a1eaac35dd7039abe2069dc858cd5a5f4ca5cd'
OUTPUT_SHA='30964aaefc6a2180dd130640abb280d61d1e2db889eaf81c1c98533689c3478c'
DIRECTION=296877288226537078784
HERALDS=[(13,34),(31,41),(33,39)]


def build(output):
    digest=hashlib.sha256(BASE.with_suffix('.qasm').read_bytes()).hexdigest()
    if digest!=BASE_SHA:raise ValueError(f'Baseline bytes changed: {digest}')
    ops,rows,data,_,_,_=prepare(BASE)
    dets=[set(xor_rows(rows,r)) for r in null_rows([DIRECTION],len(rows))]
    bit=max(o.bit or 0 for o in ops)+1
    for i,(q,t) in enumerate(HERALDS):
        if any(o.time==t and q in o.qs for o in ops):raise ValueError(('occupied herald slot',q,t))
        ops.append(f.Op('M',(q,),t,bit+i));dets.append({bit+i})
    text=emit(ops,dets)
    digest=hashlib.sha256(text.encode()).hexdigest()
    if digest!=OUTPUT_SHA:raise ValueError(f'Reproduction differs: {digest}')
    raw=raw_check(text,data)
    if not raw['ok']:raise ValueError(raw)
    output=Path(output).resolve();output.parent.mkdir(parents=True,exist_ok=True)
    output.with_suffix('.qasm').write_text(text)
    output.with_suffix('.json').write_text(json.dumps(dict(data_qubits=data,
        source=dict(baseline=str(BASE.relative_to(ROOT)),baseline_sha256=BASE_SHA,
                    accepted_sector_basis=[DIRECTION],heralds=HERALDS)),indent=2)+'\n')
    return output,dict(qasm_sha256=digest,data_qubits=data,raw=raw,
                       cx=sum(o.kind=='CX' for o in ops),ticks=max(o.time for o in ops)+1,
                       t_gates=sum(o.kind in ('T','TDG') for o in ops))


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',default=str(HERE/'release/native_incumbent_patch'))
    ap.add_argument('--price',action='store_true');args=ap.parse_args()
    output,result=build(args.output)
    if args.price:
        exact=price(output,1)
        assert abs(exact['loss']-3.586635120011179e-5)<1e-12
        assert abs(exact['acceptance']-.5003426997728605)<1e-12
        result['exact']=exact
    print(json.dumps(dict(stem=str(output),**result),indent=2))
