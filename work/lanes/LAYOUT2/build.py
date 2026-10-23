import sys,os,json,re
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
import merge,ft
layout,af,bf,tag=sys.argv[1:5]
l=json.loads(Path(layout).read_text());A=json.loads(Path(af).read_text());BC=json.loads(Path(bf).read_text())
if isinstance(A,list):A=A[int(sys.argv[5]) if len(sys.argv)>5 else 0]
if isinstance(BC,list):BC=BC[0]
assert all(A['danger_vector_units'][j+1]==0 for j in l['M'])
ft.B=l['b'];ft.C=l['c'];assert not ft.faults(BC)
anc=l['cat'];root=anc[0];seen={root};tree=[]
while len(seen)<len(anc):
 e=next((u,v) for u in seen for v in anc if v not in seen and abs(u//6-v//6)+abs(u%6-v%6)==1)
 tree.append(e);seen.add(e[1])
gad=dict(timing='late',M=l['M'],anc=anc,tree=tree,checks=[(u,l['a'][j],1) for u,j in zip(anc,l['M'])],mx=2)
gad['early_other']=bool(os.environ.get('A_EARLY'))
text,data,R,pre=merge.build({'a':A,'bc':BC},['a','bc'],l,l['moves'],gad)
Path(tag+'.qasm').write_text(text);Path(tag+'.json').write_text(json.dumps(dict(data_qubits=data,layout=layout,A=af,BC=bf,R=R,hops=l['hops'],helpers=l['hBC'],M=l['M'],cat=anc,cx=text.count('cx ')),indent=2)+'\n')
print(tag,'R',R,'CX',text.count('cx '),'BClayers',len(BC['ops']),flush=True)
