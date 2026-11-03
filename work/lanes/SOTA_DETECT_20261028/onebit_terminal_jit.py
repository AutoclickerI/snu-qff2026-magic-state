"""Encoded one-bit teleported terminal, ideal input/resource controls only."""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import sys,json,concurrent.futures
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[2];sys.path[:0]=[str(R/'work/lanes/FRAME20261027'),str(R/'work/lanes/CAT3_20261027'),str(R/'work/lanes/END2_20261027'),str(R/'work/tools')]
import frame_tools as ft,smallcat as s
from qtools.evaluator import sparse_walsh as sw
import tprep.qasm as jq
D=list(range(7));A=list(range(7,14));B=list(range(14,21));F=s.f
out=H/'onebit_terminal_jit';out.mkdir(exist_ok=True)
def one(axis):
 F.DATA=B;ft.OUT=out;ops=[]
 for i,q in enumerate(D):ops.append(F.Op('RX'if i in s.PIV|{2}else'R',(q,),0))
 ops += [F.Op('T',(D[2],),1),F.Op('CX',(D[2],D[4]),2),F.Op('CX',(D[2],D[5]),3)]
 for k,layer in enumerate(s.ENC):ops += [F.Op('CX',(D[a],D[b]),4+k)for a,b in layer]
 s.prep(ops,A,0,axis=='Z');s.prep(ops,B,0,axis=='X')
 for d,a,b in zip(D,A,B):
  ops.append(F.Op('CX',(a,d)if axis=='X' else(d,a),7))
  ops.append(F.Op('CX',(b,d)if axis=='X' else(d,b),8))
 for i,a in enumerate(A):ops.append(F.Op('MX' if axis=='X' else'M',(a,),8,7+i))
 for i,d in enumerate(D):ops.append(F.Op('M' if axis=='X' else'MX',(d,),9,i))
 for b in B:ops.append(F.Op('ID',(b,),9))
 dets=[{j for j in row}for row in F.SUPPORTS]+[{7+j for j in row}for row in F.SUPPORTS]
 frames={'X':(0,set(range(7))if axis=='X'else set()),'Z':(0,set(range(7))if axis=='Z'else set())}
 stem=ft.emit('ideal_'+axis,ops,dets,B,frames,{'diagnostic_only':True,'axis':axis,'scope':'ideal input/resources and noisy full terminal'})
 old=jq.adjacent
 try:
  jq.adjacent=lambda a,b:a!=b
  raw=ft.raw_check(stem.with_suffix('.qasm').read_text(),B);row={'axis':axis,'raw':raw,'scope':'perfect input/prep, actual noisy terminal gates, reads and idle channels','no_grid_claim':True,'output_idle_clocks':1,'counterfactual':'receiver first-check idle suppressed by assumed perfect JIT preparation'}
  if not raw['ok']:return row
  m,e,groups,nd,ks,psi,where=ft.prepare(stem)
  for cid,ch in enumerate(m.chans):
   if m.labels[ch['ins']].time<7:
    ch['p']=0
    for ff in groups[cid]:ff['p']=0
  c1=0.;cache={}
  for ff in m.faults:
   if not ff['p']:continue
   k=(ff['s'],ff['d'])
   if k not in cache:cache[k]=e.ntable(*k)
   _,n=cache[k]
   if n is not None:c1+=ff['p']/.001*max(0.,float(n[ff['e']]))
  compiled,elim=sw.compile_best(m,e,groups,nd,ks,save=False)
  sw._CTX.update(eng=e,ks=ks,psi=psi,where=where,compiled=compiled,elim=elim)
  try:
   rows=[sw._row(k)for k in [None]+e.keys];A0=rows[0]['value'];obs=sum(w*b*r['value'] for w,b,r in zip(e.W,e.beta,rows[1:]));loss=(A0-obs)/(2*A0)
  finally:sw._CTX.clear();sw.COLUMNS.clear()
  row.update(loss=float(loss),acceptance=float(A0),c1=c1,stem=str(stem));return row
 finally:jq.adjacent=old
if __name__=='__main__':
 with concurrent.futures.ProcessPoolExecutor(max_workers=2)as ex:rows=list(ex.map(one,['X','Z']))
 (H/'onebit_terminal_jit_results.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows,indent=2),flush=True)
