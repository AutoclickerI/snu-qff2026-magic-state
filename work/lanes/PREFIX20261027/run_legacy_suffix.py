import sys,json,argparse
from pathlib import Path
import synth
from qcirc import parse
synth.A=[1,14,8,9,2,16,15]
synth.D=[0,20,7,10,3,22,21]
synth.B=[6,26,13,11,4,23,27]
synth.CELLS=[1,2,3,7,8,9,14,15,16]
FLAG=3;ZERO=7
synth.INIT=tuple((9+synth.A.index(q)) if q in synth.A else 16 if q==FLAG else 0 for q in synth.CELLS)
synth.EDGES=[(i,j) for i,a in enumerate(synth.CELLS) for j,b in enumerate(synth.CELLS) if synth.adjacent(a,b)]
def suffix():
    p=synth.ROOT/'work/lanes/T14'
    units,dets=parse((p/'t14a.qasm').read_text())
    stage=json.loads((p/'t14a.stage.json').read_text())
    prekeys={(u['t'],u['k'],tuple(u['q'])) for u in stage}
    pre={i for i,u in enumerate(units) if (u['t'],u['k'],u['q']) in prekeys}
    pb={units[i]['b'] for i in pre if units[i]['b'] is not None}
    suf=[dict(u) for i,u in enumerate(units) if i not in pre]
    ds=[d for d in dets if not(set(d)&pb)]
    assert sum(u['k']=='CX' for u in suf)==98
    return units,suf,ds,pre
synth.split_suffix=suffix
# Generalized build uses these instead of hard-coded helper cells.
synth.FLAG=FLAG;synth.ZERO=ZERO
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--seed',type=int,default=0);a.add_argument('--functional',type=int,default=8);a.add_argument('--beam',type=int,default=500);a.add_argument('--depth',type=int,default=60);x=a.parse_args()
    r=synth.synth(x.seed,x.functional,x.beam,x.depth)
    print('result',r,flush=True)
    if r:
        n=f'legacy_{x.functional}_{x.seed}'
        (synth.HERE/f'{n}.network.json').write_text(json.dumps(r,indent=2))
        print('candidate',synth.build(r,n),flush=True)
