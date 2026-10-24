#!/usr/bin/env python3
"""Fixed final Z-readout re-encoder. Input/output are stems; pairs u:v."""
import json,re,sys
src,out,spec=sys.argv[1:4]
L=open(src+'.qasm').read().splitlines(); pairs=[tuple(map(int,x.split(':'))) for x in spec.split(',') if x]
# locate last measure per qubit, and ensure all endpoints have same preceding barrier block
meas={}
for i,l in enumerate(L):
 m=re.match(r'measure q\[(\d+)\] -> c\[(\d+)\];',l)
 if m: meas[int(m.group(1))]=(i,int(m.group(2)))
def nextbar(i):
 j=i+1
 while j<len(L) and not L[j].startswith('barrier'): j+=1
 if j>=len(L): raise ValueError(f'no barrier after measurements {u,v}')
 return j
blocks={}
for u,v in pairs:
 if u not in meas or v not in meas: raise ValueError(f'missing measurement {u,v}')
 iu,bu=meas[u];iv,bv=meas[v]
 if nextbar(iu)!=nextbar(iv): raise ValueError(f'different measurement blocks {u,v}')
 blocks.setdefault(nextbar(iu),[]).append((u,v))
# disjoint endpoints and no source that was removed
used=[]
for u,v in pairs:
 if u==v or u in used or v in used: raise ValueError('overlapping re-encoding edges')
 used += [u,v]
# operate indices in original L; replace/remove, then insert after each block barrier
sub={}
insert={}
for b,es in blocks.items():
 moved=[]
 for u,v in es:
  iu,bu=meas[u];iv,bv=meas[v]
  L[iu]=f'cx q[{u}],q[{v}];'
  L[iv]=None
  moved += [f'measure q[{u}] -> c[{bu}];',f'measure q[{v}] -> c[{bv}];']
  sub[bv]=bu
 insert[b]=moved
# Remove deleted lines, insert moved after matching barrier. Since insertion only after barriers, no index ambiguity use one pass.
new=[]
for i,l in enumerate(L):
 if l is None: continue
 new.append(l)
 if i in insert: new.extend(insert[i])
L=new
for i,l in enumerate(L):
 if l.startswith('// DETECTOR'):
  bits=[int(x) for x in re.findall(r'c\[(\d+)\]',l)]; s=set()
  for bit in bits:
   s ^= {bit}
   if bit in sub: s ^= {sub[bit]}
  L[i]='// DETECTOR '+' '.join(f'c[{b}]' for b in sorted(s))
open(out+'.qasm','w').write('\n'.join(L)+'\n')
d=json.load(open(src+'.json'));d['source']=f'{src} with fixed final readout re-encoding {spec}';d['reencoding']=pairs
json.dump(d,open(out+'.json','w'))
