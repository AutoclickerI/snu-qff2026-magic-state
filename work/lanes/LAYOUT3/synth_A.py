import os,sys,json
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
HERE=Path(__file__).parent;import synth
cells=list(map(int,sys.argv[1].split(',')));out=Path(sys.argv[2]);depth=int(sys.argv[3]);rows=[[0,2,4,6],[1,2,5,6],[3,4,5,6],[0,1,2]]
r=synth.synth(cells,rows,cells,depth,seconds=float(sys.argv[4]),workers=8,max_cx=30)
if r is None: print('NONE');raise SystemExit(1)
ops,piv,status=r;d={'ops':ops,'pivots':piv,'cx':sum(map(len,ops)),'depth':len(ops),'cells':cells,'rows':rows,'status':status};out.write_text(json.dumps(d,indent=2)+'\n');print(d)
