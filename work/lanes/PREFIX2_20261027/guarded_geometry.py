"""Broaden the flagged polynomial footprint while preserving A/D and the tail."""
import os,sys,json,argparse
from pathlib import Path
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[key]='1'
import flag6 as f6
import guarded_poly as gp
import guarded_layers as gl
from qcirc import adjacent
from qtools import price
from qtools.validity import raw_check
from search_phase import singles
H=Path(__file__).resolve().parent

def configure(count):
    cells=sorted(set(f6.CELLS+[10,13]+([4] if count==12 else [])))
    assert len(cells)==count
    f6.CELLS=cells
    f6.INIT=tuple(9+f6.A.index(q) if q in f6.A else 16 if q==3 else 32 if q==7 else 0 for q in cells)
    f6.EDGES=[(a,b) for a,q in enumerate(cells) for b,r in enumerate(cells) if adjacent(q,r)]

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--cells',type=int,choices=[11,12],default=11);ap.add_argument('--layers',action='store_true');args=ap.parse_args()
    configure(args.cells);family=f'guardgeo{args.cells}'+('L' if args.layers else 'S');out=[];best=1;number=0
    for seed in range(3):
        nets=gl.search(seed,width=700,maxdepth=35) if args.layers else gp.search(seed,beam=1000,maxdepth=65,gamma=.1)
        for r in nets:r['cells']=f6.CELLS
        (H/f'{family}_network_s{seed}.json').write_text(json.dumps(nets,indent=2)+'\n')
        for net in nets[:2]:
            for mode,ps in [('first',0),('last',0),('random',1),('random',2)]:
                rec=dict(net,phase_mode=mode,phase_seed=ps)
                name=f'{family}_{number}_{mode}{ps}'
                try:
                    st=f6.build(rec,name);raw=raw_check(st.with_suffix('.qasm').read_text(),f6.D)
                    row=dict(stem=str(st),cells=args.cells,source_cx=net['depth'],checks=len(net['checkpoints']),raw=raw)
                    if raw['ok']:
                        c1,n=singles(st);row.update(c1=c1,harmful=n)
                        if c1<1e-5:
                            p=price(st,1);row.update(loss=p['loss'],acceptance=p['acceptance'])
                            if p['acceptance']>=.5002 and p['loss']<best:
                                best=p['loss'];(H/f'{family}_best.json').write_text(json.dumps(row,indent=2)+'\n')
                    print(json.dumps(row),flush=True);out.append(row)
                except Exception as ex:
                    print('ERROR',name,repr(ex),flush=True);out.append(dict(name=name,error=repr(ex)))
                (H/f'{family}_results.json').write_text(json.dumps(out,indent=2)+'\n')
            number+=1

if __name__=='__main__':main()
