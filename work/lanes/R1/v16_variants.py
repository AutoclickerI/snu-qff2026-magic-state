import re,json,sys
from pathlib import Path
src=Path('/home/jihoon/competitions/quantumn/work/candidates/v16_bc2m.qasm').read_text().splitlines()
def make(name,drop=(),release=False):
 groups=[]; cur=[]; bars=[]; t=0
 for l in src:
  if l.startswith('barrier'):
   groups.append(cur);cur=[];bars.append(l);t+=1
   if t==33: break
  elif t<=32:cur.append(l)
 # above intentionally only prefix; append full source unchanged after barrier 33 not useful.
 out=[]; t=0
 for i,(g,b) in enumerate(zip(groups,bars)):
  out += g
  if i in drop: out.append('')
  else:
   if release:
    qs=[int(q) for q in re.findall(r'q\[(\d+)\]',b)]
    if i>=15 and 19 in qs:qs.remove(19)
    if i>=19 and 13 in qs:qs.remove(13)
    b='barrier '+','.join(f'q[{q}]' for q in qs)+';'
   out.append(b)
 if len(groups)<33: raise RuntimeError(len(groups))
 # keep suffix from the first line after the 33rd prefix barrier
 idx=0; seen=0
 for j,l in enumerate(src):
  if l.startswith('barrier'):
   seen+=1
   if seen==33: idx=j+1; break
 out += src[idx:]
 p=Path(__file__).with_name(name+'.qasm');p.write_text('\n'.join(out)+'\n')
 d=json.loads(Path('/home/jihoon/competitions/quantumn/work/candidates/v16_bc2m.json').read_text());d['source']='R1 v16 barrier variant '+name;Path(__file__).with_name(name+'.json').write_text(json.dumps(d))
for name,drop,rel in [('v16_base',(),False),('v16_drop16',(16,),False),('v16_drop3132',(31,32),False),('v16_drop163132',(16,31,32),False),('v16_release',(),True),('v16_release_drop',(16,31,32),True)]:make(name,drop,rel)
