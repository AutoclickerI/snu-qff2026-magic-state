"""Exact 256-bin Pauli convolution, with arbitrary incoming-sector/Bloch optimization.
An independent idle channel commutes through the terminal controlled Paulis
after adding only phases to their discarded controls. This is a rigorous
relaxation for the specified stale-syndrome recovery witnesses, not every QEC.
"""
import json,math
import numpy as np
from pathlib import Path
H=Path(__file__).resolve().parent

def evaluate(n):
    p=.75*(1-(1-4*.001/3)**n)
    # bits: sx 0..2, sz 3..5, parityX 6, parityZ 7
    v=np.zeros(256);v[0]=1
    ix=np.arange(256)
    for col in range(1,8):
        x=col|64;z=(col<<3)|128
        v=(1-p)*v+p/3*(v[ix^x]+v[ix^z]+v[ix^x^z])
    moments=[]
    for sx in range(8):
        for sz in range(8):
            fx=((ix>>6)&1)^int(sx!=0)^(((ix&7)^sx)!=0)
            fz=((ix>>7)&1)^int(sz!=0)^((((ix>>3)&7)^sz)!=0)
            vx=float(v@(1-2*fz.astype(int)));vy=float(v@(1-2*(fx^fz).astype(int)))
            moments.append(dict(sector=[sx,sz],vx=vx,vy=vy,loss=(1-math.sqrt((vx*vx+vy*vy)/2))/2))
    best=min(moments,key=lambda r:r['loss'])
    origin=moments[0]
    return dict(idle_ticks=n,depolarizing_probability=p,acceptance=1.,
                optimized_all_state_lower_bound=best['loss'],minimizing_sector=best['sector'],
                perfect_T_input_loss=(2-origin['vx']-origin['vy'])/4)

if __name__=='__main__':
    rows=[evaluate(n) for n in (1,2,3,4,6)]
    for name in ('c_onehot','c_onehot_rccx','d_or_duplicate'):
        p=H/'logs'/f'{name}.scan.json'
        if p.exists():
            r=evaluate(json.loads(p.read_text())['native_depth']);r['witness']=name;rows.append(r)
    (H/'logs/wait_bounds.json').write_text(json.dumps(rows,indent=2)+'\n')
    print(json.dumps(rows),flush=True)
