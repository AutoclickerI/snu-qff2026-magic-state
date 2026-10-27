"""Replace selected data idle slots with native, heralded identity interactions."""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='1'
import argparse,contextlib,copy,io,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'work/tools'))
sys.path.insert(0,str(ROOT/'work/lanes/END2_20261027'))
sys.path.insert(0,str(ROOT/'work/lanes/PREFIX2_20261027'))
sys.path.insert(0,str(ROOT/'work/lanes/REBUILD20261027'))
from qtools import write_stem
from qtools.evaluator import frontend as f
from qtools.validity import raw_check
from joint import emit
from record_contract import singles
from pairs import audit


def make(stem,link=False,which=3):
    stem=Path(stem);data=json.loads(stem.with_suffix('.json').read_text())['data_qubits']
    ops,dets=f.parse_current(stem.with_suffix('.qasm').read_text())
    occupied={(o.time,q) for o in ops for q in o.qs}
    nextbit=max(o.bit or 0 for o in ops)+1;added=[]
    pairs=[(6,0,37),(2,1,40)]
    for index,(d,q,reset) in enumerate(pairs):
        if not which>>index&1:continue
        assert not any((t,q) in occupied for t in range(reset,48)),(q,reset)
        added.append(f.Op('RX',(q,),reset))
        for t in range(reset+1,47):
            if (t,d) in occupied or (link and t==45):continue
            added.append(f.Op('CX',(d,q),t))
        added.append(f.Op('MX',(q,),47,nextbit));dets.append({nextbit});nextbit+=1
    if link:
        assert which==3
        added.append(f.Op('CX',(1,0),45))
    ops+=added;ops.sort(key=lambda o:o.time)
    text=emit(ops,dets);raw=raw_check(text,data)
    assert raw['ok'],raw
    out=write_stem(text,data,HERE/'parked',f'{stem.name}_w{which}_l{int(link)}',
                   source=dict(base=str(stem),added=[dict(kind=o.kind,qs=o.qs,time=o.time,bit=o.bit)for o in added]))
    f.DATA=data
    single=singles(f.make_model(*f.parse_current(text)))
    with contextlib.redirect_stdout(io.StringIO()):
        pair=audit(out)
    return dict(stem=str(out),base=str(stem),which=which,link=link,raw=raw,c1=single['c1'],c2=pair['c2'],
                cx=sum(o.kind=='CX' for o in ops),ticks=max(o.time for o in ops)+1,
                added_cx=sum(o.kind=='CX' for o in added))


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('stem');args=ap.parse_args()
    results=[]
    for which,link in [(1,False),(2,False),(3,False),(3,True)]:
        result=make(args.stem,link,which);results.append(result)
        (HERE/'parked_results.json').write_text(json.dumps(results,indent=2)+'\n')
        print(json.dumps(result),flush=True)
