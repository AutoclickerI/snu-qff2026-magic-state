"""SAT resynthesis of a time window, with exact target space, FT CEGAR and CX cap."""
import sys,os,json,time
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
import sat6,ft
layout,prep,start,width,shrink,cap=sys.argv[1:7];start=int(start);width=int(width);shrink=int(shrink);cap=int(cap)
l=json.loads(Path(layout).read_text());d=json.loads(Path(prep).read_text());sat6.B=ft.B=l['b'];sat6.C=ft.C=l['c']
old=d['ops'];end=min(start+width,len(old));D=len(old)-shrink;assert end-start>shrink
cells=l['b']+l['c']+l['hBC'];piv=sorted(d['pivots'],key=cells.index)
s,sel,p,edges,cells,add_fault=sat6.build(D,l['hBC'],0,threads=1,maxcx=cap,pivfix=piv)
for t,se in enumerate(sel):
 if t<start:fix=old[t]
 elif t>=end-shrink:fix=old[t+shrink]
 else:continue
 es={tuple(e) for e in fix}
 for e,v in se.items():s.add_clause([v] if e in es else [-v])
added=set();beg=time.time();it=0
while True:
 ok,model=s.solve(time_limit=float(os.environ.get('SAT_SECONDS','60')));it+=1
 if ok is not True:print('STATUS',ok,'iters',it,'seconds',time.time()-beg,flush=True);break
 ops=[[list(e) for e in edges if model[se[e]]] for se in sel];new=dict(ops=ops,pivots=piv,cx=sum(map(len,ops)),depth=D,cap=cap,layout=layout,source=prep,window=[start,end,shrink])
 bad=[(t,q) for t,q,_ in ft.faults(new,cells)];print('ITER',it,'cx',new['cx'],'bad',len(bad),time.time()-beg,flush=True)
 if not bad:
  assert new['cx']<=cap
  out=Path(prep).with_name(Path(prep).stem+f'_w{start}_{width}_{shrink}_k{cap}.json');out.write_text(json.dumps(new,indent=2)+'\n');print('VALIDATED',out,flush=True);break
 for t,q in bad:
  if (t,q) not in added:add_fault(t,q);added.add((t,q))
