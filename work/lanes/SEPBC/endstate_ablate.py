"""Full-circuit categorical third-order ablations and exact physical pair classes."""
from common import *
from model import Basis
import argparse,collections
def main():
 p=argparse.ArgumentParser();p.add_argument('stem',type=Path);p.add_argument('--procs',type=int,default=2);a=p.parse_args();stem=a.stem;plan=json.loads(stem.with_suffix('.plan.json').read_text());text=stem.with_suffix('.qasm').read_text();ev=exact2.Eval(text,plan['meta']['data_qubits']);flat=[(l,o['tag'])for o in plan['ops']for l in o['lines']];at=0;tags={}
 for li,line in enumerate(text.splitlines(),1):
  s=line.strip()
  if not s or s.startswith(('//','barrier','OPENQASM','include','qreg','creg')):continue
  assert s==flat[at][0],(li,s,flat[at]);tags[li]=flat[at][1];at+=1
 R=plan['meta']['R'];regions=[]
 for c,ch in enumerate(ev.m.chans):
  lab=ev.chan_label(c)
  if ch['gap']is not None:reg='pre_round_idle'if ch['gap'][1]+ch['gap'][2]<=R else'round'
  else:reg=tags[lab['line']]
  regions.append(reg)
 fp=ev.fp.copy();rows=[];experiments=[('all',lambda r:False),('no_pre_round_idle',lambda r:r=='pre_round_idle'),('no_teleport_noise',lambda r:r=='block_teleport'),('no_encoder_noise',lambda r:r.startswith('encoder')),('no_data_hop_noise',lambda r:r=='data_hops'),('no_prefix_noise',lambda r:r=='prefix'),('only_round_noise',lambda r:r!='round'),('no_idle_or_teleport',lambda r:r in('pre_round_idle','block_teleport')),('no_idle_or_encoder',lambda r:r=='pre_round_idle'or r.startswith('encoder'))]
 for label,pred in experiments:
  excluded={c for c,r in enumerate(regions)if pred(r)};ev.fp=fp.copy();ev.fp[[i for i,c in enumerate(ev.fch)if c in excluded]]=0;r=mom.evaluate(ev);r.update(label=label,channels_removed=len(excluded));rows.append(r);append_result(stem.name+':'+label,r,'Counterfactual removal of physical channels, not an attainable bound.');print(json.dumps(r),flush=True)
 ev.fp=fp
 # Exact-zero acceptance classes are omitted; all surviving physical pairs
 # still use exact2.run and its distinct-channel arithmetic.
 bas=Basis();indices=[];constraints=[]
 for i,(x,z,c)in enumerate(ev.e.projs):
  co=bas.express(x|(z<<ev.e.r))
  if co is None:bas.add(x|(z<<ev.e.r));indices.append(i)
  else:
   rel=1<<i
   for j,bi in enumerate(indices):
    if co>>j&1:rel^=1<<bi
   constraints.append(rel)
 old=ev.e.ntable;ev.e.ntable=lambda s,d:(0.,None)if any((int(d)&h).bit_count()%2 for h in constraints)else old(s,d)
 r=exact2.run(ev,a.procs,keep_thr=0);pairs=collections.Counter();examples={}
 for value,i,j,n,acc in r['big']:
  key=' x '.join(sorted([regions[int(ev.fch[i])],regions[int(ev.fch[j])]]));pairs[key]+=value
  if value>examples.get(key,[0])[0]:examples[key]=[value,ev.fault_label(i),ev.fault_label(j)]
 out=dict(regions=dict(collections.Counter(regions)),rows=rows,second=r['loss2'],pair_classes=dict(pairs.most_common()),examples=examples)
 stem.with_suffix('.ablation.json').write_text(json.dumps(out,indent=2));append_result(stem.name,out,'Complete emitted-operation provenance and pre-round idle channel split.');print('PAIRS',json.dumps(dict(pairs)),flush=True)
if __name__=='__main__':main()
