from a34_search import *
def physical_key(stem):
 text,md,h,us,ts,tail=read(stem)
 measures=[]
 for u,t in zip(us,ts):
  for line in u.lines:
   if line.startswith('measure'):
    measures.append((t,u.qs[0],int(re.search(r'c\[(\d+)\]',line)[1])))
 assert len({c for t,q,c in measures})==len(measures),'measurement bit overwritten'
 bitmap={c:i for i,(t,q,c) in enumerate(sorted(measures))}
 def normalize(line):return re.sub(r'c\[(\d+)\]',lambda m:f'c[{bitmap[int(m[1])]}]',line)
 gates=tuple(sorted((t,tuple(normalize(l) for l in u.lines)) for u,t in zip(us,ts)))
 basis={}
 for l in tail:
  if not l.startswith('// DETECTOR'):continue
  v=sum(1<<bitmap[int(x)] for x in re.findall(r'c\[(\d+)\]',l))
  while v:
   i=v.bit_length()-1
   if i not in basis:basis[i]=v;break
   v^=basis[i]
 for i in sorted(basis):
  for j in sorted(basis):
   if j>i and basis[j]>>i&1:basis[j]^=basis[i]
 return hashlib.sha256(repr((gates,sorted(basis.values()))).encode()).hexdigest()
if __name__=='__main__':
 groups={};alias={};sources={}
 for name in ['encoders','joint']:
  for s in json.loads((D/f'{name}.json').read_text())['stems']:
   k=physical_key(H/s)
   if k in groups:alias[s]=groups[k]
   else:groups[k]=s;sources[s]=name
 (D/'physical_aliases.json').write_text(json.dumps(alias,indent=2));ss=[s for s in groups.values() if sources[s]=='joint'];(D/'joint_physical_unique.json').write_text(json.dumps(ss,indent=2));print('unique',collections.Counter(sources.values()),'aliases',len(alias))
