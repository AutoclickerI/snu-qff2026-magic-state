import sys,os,json
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
import sat6,ft
l=json.loads(Path(sys.argv[1]).read_text());f=Path(sys.argv[2]);d=json.loads(f.read_text());sat6.B=ft.B=l['b'];sat6.C=ft.C=l['c']
cells=l['b']+l['c'];piv=sorted(d['pivots'],key=cells.index)
s,sel,p,edges,cells,add=sat6.build(len(d['ops']),[],0,threads=1,maxcx=80,pivfix=piv)
for L,se in zip(d['ops'],sel):
 es={tuple(e) for e in L}
 for e,v in se.items():s.add_clause([v] if e in es else [-v])
ok,_=s.solve();assert ok is True;assert not ft.faults(d,cells)
d['certificate']='sat6 target subspace, real at-most-80 CX, every fixed gate; independent ft.faults zero'
f.write_text(json.dumps(d,indent=2)+'\n');print('CERTIFIED',f.name,d['cx'],flush=True)
