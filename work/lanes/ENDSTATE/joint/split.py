"""Exact disjoint second-order pair attribution; no alteration of full score."""
import os,sys,json,collections,re,time
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
sys.dont_write_bytecode=True
H=Path(__file__).resolve().parent;ROOT=H.parents[3];sys.path[:0]=[str(ROOT/'work/lanes/EVAL'),str(ROOT/'work')]
import xtim
xtim.cache_dir=str(H/'.xtim_cache')
import exact2
from model import Basis

def split(stem):
 stem=Path(stem);plan=json.loads(stem.with_suffix('.plan.json').read_text());meta=plan['meta'];ev=exact2.Eval(stem.with_suffix('.qasm').read_text(),meta['data_qubits']);bytime={(o['t'],tuple(sorted(o['qs']))):o['region']for o in plan['ops']};regions=[];exposure=collections.Counter()
 for ch in range(len(ev.m.chans)):
  lab=ev.chan_label(ch);t=int(lab['steps'].split('..')[0]);qs=tuple(sorted(lab['qubits']))
  if lab['kind']=='idle':
   end=int(lab['steps'].split('..')[-1]);reg='round'if t>=meta['R']else'exposure';exposure[reg]+=end-t+1
  else:
   reg=bytime.get((t,qs))
   if reg is None:
    opts=[o['region']for o in plan['ops']if o['t']==t and set(qs)<=set(o['qs'])];assert len(opts)==1,(ch,lab,opts);reg=opts[0]
  regions.append(reg)
 bas=Basis();indices=[];constraints=[]
 for i,(xx,zz,c)in enumerate(ev.e.projs):
  combo=bas.express(xx|(zz<<ev.e.r))
  if combo is None:bas.add(xx|(zz<<ev.e.r));indices.append(i)
  else:
   rel=1<<i
   for j,bi in enumerate(indices):
    if combo>>j&1:rel^=1<<bi
   constraints.append(rel)
 original=ev.e.ntable;ev.e.ntable=lambda s,d:(0.,None)if any((int(d)&h).bit_count()%2 for h in constraints)else original(s,d)
 fr=[regions[int(ch)]for ch in ev.fch];r=exact2.run(ev,procs=1,keep_thr=0,third=False);pairs=collections.Counter()
 for value,i,j,*rest in r['big']:pairs[' x '.join(sorted([fr[i],fr[j]]))]+=value
 # Baseline equality is a required cross-check of the attribution engine.
 ref=json.loads(stem.with_suffix('.sens.json').read_text())if stem.with_suffix('.sens.json').exists()else None
 if ref:assert abs(ref['loss']-r['loss'])<1e-12,(ref['loss'],r['loss'])
 out=dict(second=r['loss'],first=r['loss1'],pair_classes=dict(pairs.most_common()),round_x_round=pairs['round x round'],pre_round_only=sum(v for k,v in pairs.items()if 'round'not in k),data_hops_involving=sum(v for k,v in pairs.items()if 'data_hops'in k),teleports_involving=sum(v for k,v in pairs.items()if 'bus'in k),exposure_involving=sum(v for k,v in pairs.items()if 'exposure'in k),idle_qubit_steps=dict(exposure),crosscheck_unchanged_exact=bool(ref),note='Second-order pair table. Exposure includes prefix idles and data waiting, not just prepared ancilla waiting. Marginals overlap; do not add. No measured block teleports in direct layouts. Bus instrument marginal, when present, is labelled separately.')
 stem.with_suffix('.split.json').write_text(json.dumps(out,indent=2));print(json.dumps(dict(stem=stem.name,**out)),flush=True)
if __name__=='__main__':
 for s in sys.argv[1:]:split(s)
