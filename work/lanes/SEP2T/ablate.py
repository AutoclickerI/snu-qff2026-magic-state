"""Native-schedule loss attribution for interleaved separate-block circuits.

All pre-round idle noise is its own region; post-round data idle belongs to the
round. Operation noise follows preserved operation provenance, not a time cut.
Regions are zeroed in the exact model; these are ablations, not submissions.
"""
import os,sys,json,argparse,collections,math
from pathlib import Path
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];os.chdir(HERE)
sys.path[:0]=[str(ROOT/'work/lanes/EVAL'),str(ROOT/'work')]
import exact2,xtim
xtim.cache_dir=str(HERE/'.xtim_cache')

def main(a):
 stem=Path(a.stem);meta=json.loads(stem.with_suffix('.json').read_text());units=json.loads(stem.with_suffix('.units.json').read_text());text=stem.with_suffix('.qasm').read_text()
 if a.fast:
  sys.path.insert(0,str(ROOT/'work/lanes/TREP2'))
  from fast_third import third_order
  exact2.third_order=third_order
 ev=exact2.Eval(text,meta['data_qubits']);base=ev.fp.copy();opmap={(u['t'],tuple(sorted(u['qs']))):('round' if u['region']=='round_a' else u['region']) for u in units};regions={};counts=collections.Counter()
 for c,ch in enumerate(ev.m.chans):
  lab=ev.chan_label(c);st=int(lab['steps'].split('..')[0])
  if ch['gap'] is not None:reg='round' if st>=meta['R_native'] else 'idle'
  else:
   qs=tuple(sorted(lab['qubits']));reg=opmap.get((st,qs))
   if reg is None:
    choices=[u['region'] for u in units if u['t']==st and set(qs)<=set(u['qs'])]
    assert len(choices)==1,(c,lab,choices);reg='round' if choices[0]=='round_a' else choices[0]
  regions[c]=reg;counts[reg]+=1
 regs=sorted(set(regions.values()));fr=[regions[int(c)] for c in ev.fch];rows=[]
 for removed in [None]+regs:
  ev.fp=base.copy()
  if removed is not None:ev.fp[[i for i,r in enumerate(fr) if r==removed]]=0
  r=exact2.run(ev,a.procs,third=True)
  third=exact2.third_order(ev,a.procs)[0]+r['t3bc'] if abs(r['loss1'])<1e-12 else None
  row=dict(noiseless=removed,c1=r['loss1'],second=r['loss'],third=third,total=r['loss']+third if third is not None else None,exp_A1=math.exp(-r['A1']))
  if removed is None and a.fast:
   reference=json.loads(stem.with_suffix('.score.json').read_text())['total'];assert abs(row['total']-reference)<1e-9,(row,reference)
  rows.append(row);stem.with_suffix('.ablation.json').write_text(json.dumps(dict(regions=counts,rows=rows),indent=1));print(row,flush=True)
 if a.pairs:
  ev.fp=base.copy();r=exact2.run(ev,a.procs,keep_thr=0);by=collections.Counter()
  for value,i,j,*rest in r['big']:by[' x '.join(sorted([fr[i],fr[j]]))]+=value
  stem.with_suffix('.pairs.json').write_text(json.dumps(dict(second=r['loss'],pairs=by),indent=1));print(by,flush=True)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('stem');p.add_argument('--procs',type=int,default=2);p.add_argument('--pairs',action='store_true');p.add_argument('--fast',action='store_true');main(p.parse_args())
