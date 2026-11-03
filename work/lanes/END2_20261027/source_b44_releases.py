"""Concrete source-only retiming requested for PREFIX2's B-ready44 model."""
import json
from pathlib import Path
from source_product_boundaries import HERE, f, save


def main():
    receipt=HERE.parent/'NATIVE2_20261027/q15_early39_cut3_release.json'
    parent=Path(json.loads(receipt.read_text())['stem'])
    ops,dets=f.parse_current(parent.with_suffix('.qasm').read_text())
    moves=[('RX',(22,),20,19),('R',(28,),20,19),('M',(28,),26,25),
           ('CX',(24,25),23,22),('CX',(24,25),24,23),
           ('CX',(19,25),25,24),('CX',(19,25),26,25),
           ('CX',(24,30),26,25),('CX',(24,25),27,26),('CX',(24,25),28,27),
           ('CX',(16,15),23,26),('CX',(16,17),24,23),('CX',(16,17),25,24),
           ('CX',(17,11),26,25),('CX',(5,11),25,26),('MX',(17,),27,26)]
    gates28=[op for op in ops if op.kind=='CX' and op.qs==(28,22) and 20<=op.time<=29]
    assert len(gates28)==7
    moves.extend(('CX',(28,22),op.time,op.time-1) for op in gates28)
    selected=[]
    for kind,qs,before,after in moves:
        found=[op for op in ops if (op.kind,op.qs,op.time)==(kind,qs,before)]
        assert len(found)==1,(kind,qs,before,found)
        selected.append((found[0],after))
    for op,after in selected:op.time=after
    changes=[dict(kind=kind,qs=list(qs),before=before,after=after)
             for kind,qs,before,after in moves]
    result=save('b44_releases',ops,dets,parent,changes)
    assert {q:result['release'][q] for q in (17,25,28)}=={17:27,25:28,28:28}
    print(json.dumps(dict(boundary=str(HERE/'prefix_b44_releases.json'),
                         release={q:result['release'][q] for q in (17,25,28)},cx=result['cx'])),flush=True)


if __name__=='__main__':main()
