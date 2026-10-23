import sys,os,json,itertools
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
import merge
from layout import paths,PRE
lf,af,bf,tag=sys.argv[1:5];l=json.loads(Path(lf).read_text());aa=json.loads(Path(af).read_text());A=aa[0] if isinstance(aa,list) else aa;BC=json.loads(Path(bf).read_text())
pp=[[p for p in paths(s,abs(s//6-t//6)+abs(s%6-t%6)) if p[-1]==t] for s,t in zip(PRE,l['d'])]
anc=l['cat'];seen={anc[0]};tree=[]
while len(seen)<3:
 u,v=next((u,v) for u in seen for v in anc if v not in seen and abs(u//6-v//6)+abs(u%6-v%6)==1);tree.append((u,v));seen.add(v)
gad=dict(timing='late',M=l['M'],anc=anc,tree=tree,checks=[(q,l['a'][i],1) for q,i in zip(anc,l['M'])],mx=2)
best=None;rows=[]
for ps in itertools.product(*pp):
 dep={i:set() for i in range(7)}
 for i,p in enumerate(ps):
  for j in range(7):
   if i==j:continue
   if PRE[j] in p[1:]:dep[i].add(j)
   if l['d'][j] in p:dep[j].add(i)
 order=[]
 while len(order)<7:
  nxt=next((i for i in range(7) if i not in order and dep[i]<=set(order)),None)
  if nxt is None:break
  order.append(nxt)
 if len(order)<7:continue
 moves=[ps[i] for i in order if len(ps[i])>1]
 txt,data,R,_=merge.build({'a':A,'bc':BC},['a','bc'],l,moves,gad)
 rows.append(dict(R=R,moves=moves))
 if best is None or R<best[0]:best=(R,txt,data,moves)
assert best
R,txt,data,moves=best
Path(tag+'.qasm').write_text(txt);Path(tag+'.json').write_text(json.dumps(dict(data_qubits=data,R=R,cx=txt.count('cx '),layout=lf,A=af,BC=bf,M=l['M'],cat=anc,hops=l['hops'],helpers=l['hBC'],moves=moves),indent=2)+'\n');Path(tag+'_routes.json').write_text(json.dumps(rows,indent=2)+'\n')
print(tag,'R',R,'routes',len(rows),'range',sorted(set(r['R'] for r in rows)),flush=True)
