from core import *
from build import insert_block
from qcirc import Circ
import cultiv_port
def tile(mask,mode):
 p=Circ();p.nbits=64;cultiv_port.superdense_cycle(p,z_first=True)
 data=set(PD);anc=[{1,2},{13,14},{9,10}];selected=set.union(*[anc[k]for k in range(3)if mask>>k&1])
 out=Circ();out.nbits=p.nbits;bits=set()
 for op,sop in zip(p.ops,p.sops):
  kind,qs,bit=sop
  if not (set(qs)-data)<=selected:continue
  if kind=='cx'and len(set(qs)&data)==1:
   isz=qs[0]in data
   if (isz and mode=='x')or(not isz and mode=='z'):continue
  out.ops.append(op);out.sops.append(sop)
  if bit is not None:bits.add(bit)
 # Circ.ops contains folded Hs not in sops, so regenerate from structured ops.
 out.ops=[]
 for kind,qs,b in out.sops:
  q=qs[0]
  if kind=='RX':out.ops += [f'reset q[{q}];',f'h q[{q}];']
  elif kind=='R':out.ops += [f'reset q[{q}];']
  elif kind=='cx':out.ops += [f'cx q[{qs[0]}],q[{qs[1]}];']
  elif kind=='MX':out.ops += [f'h q[{q}];',f'measure q[{q}] -> c[{b}];']
  elif kind=='M':out.ops += [f'measure q[{q}] -> c[{b}];']
  else:raise ValueError(kind)
 out.detectors=[d for d in p.detectors if set(d)<=bits]
 return out
def main():
 base=provenance(read(BASE));jobs=[]
 for mask in (1,2,4,3,5,6):
  for mode in ('x','z','xz'):
   p=tile(mask,mode)
   for where in (77,129):
    c=insert_block(base,p,where)
    if where==129 and mask&4:
     inds=[i for i,u in enumerate(c['u'])if u.name in('MX','MEASURE')and u.qs==(10,)and c['tags'][i]!='suffix']
     for i in inds:
      if c['u'][i].name=='MX':c['u'][i]=Unit(c['u'][i].lines[:2])
     add(c,inds[-1]+1,['reset q[10];','h q[10];'])
    name=f'partial_{mask}_{mode}_{where}'
    try:
     c=placement(c,mode='alap');stem=save(c,name,f'extra tile mask {mask}, {mode} stabilizers at boundary {where}');jobs.append(dict(stem=str(stem),change=c['meta']['change']))
    except Exception as e:print('BUILD ERROR',name,e,flush=True)
 (OUT/'partial_manifest.json').write_text(json.dumps(jobs,indent=2)+'\n')
if __name__=='__main__':main()
