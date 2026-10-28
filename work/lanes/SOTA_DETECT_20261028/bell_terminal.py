"""Encoded-Bell terminal, ideal input and perfect instantaneous resource diagnostic.
Only the Bell measurement layer, final reads, and output idle channels are noisy.
No locality, resource cost, or operational noise exemption claimed for a real circuit.
"""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import sys,json,math
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[2];sys.path[:0]=[str(R/'work/lanes/FRAME20261027'),str(R/'work/lanes/CAT3_20261027'),str(R/'work/lanes/END2_20261027'),str(R/'work/tools')]
import frame_tools as ft,smallcat as s
from qtools.evaluator import sparse_walsh as sw
import tprep.qasm as jq
ft.OUT=H/'bell_terminal';ft.OUT.mkdir(exist_ok=True)
D=list(range(7));B=list(range(7,14));C=list(range(14,21));F=s.f;F.DATA=B
ops=[]
for i,q in enumerate(D):ops.append(F.Op('RX' if i in s.PIV|{2}else'R',(q,),0))
ops += [F.Op('T',(D[2],),1),F.Op('CX',(D[2],D[4]),2),F.Op('CX',(D[2],D[5]),3)]
for k,layer in enumerate(s.ENC):ops += [F.Op('CX',(D[a],D[b]),4+k)for a,b in layer]
s.prep(ops,B,0,True);s.prep(ops,C,0,False)
ops += [F.Op('CX',(b,c),4)for b,c in zip(B,C)]
ops += [F.Op('CX',(c,d),7)for c,d in zip(C,D)]
ops += [F.Op('ID',(b,),7)for b in B]
ops += [F.Op('M',(d,),8,i)for i,d in enumerate(D)]
ops += [F.Op('MX',(c,),8,7+i)for i,c in enumerate(C)]
ops += [F.Op('ID',(b,),8)for b in B]
ops.sort(key=lambda x:x.time)
dets=[{j for j in row}for row in F.SUPPORTS]+[{7+j for j in row}for row in F.SUPPORTS]
frames={'X':(0,set(range(7))),'Z':(0,set(range(7,14)))}
stem=ft.emit('ideal_bell',ops,dets,B,frames,{'diagnostic_only':True,'scope':'ideal resource and input, noisy terminal only; explicit output idles'})
old=jq.adjacent
try:
 jq.adjacent=lambda a,b:a!=b
 raw=ft.raw_check(stem.with_suffix('.qasm').read_text(),B);print('RAW',json.dumps(raw),flush=True)
 if not raw['ok']:raise RuntimeError('raw output or detectors invalid')
 m,eng,groups,nd,ks,psi,where=ft.prepare(stem)
 for cid,ch in enumerate(m.chans):
  if m.labels[ch['ins']].time<7:
   ch['p']=0
   for ff in groups[cid]:ff['p']=0
 # Explicit identity operations at 7 and 8 force real terminal output noise;
 # channels attached to the pre-terminal gates have been zeroed above.
 first=0.;cache={}
 for ff in m.faults:
  if not ff['p']:continue
  k=(ff['s'],ff['d'])
  if k not in cache:cache[k]=eng.ntable(*k)
  _,nn=cache[k]
  if nn is not None:first+=ff['p']/.001*max(0,float(nn[ff['e']]))
 compiled,elim=sw.compile_best(m,eng,groups,nd,ks,save=False)
 sw._CTX.update(eng=eng,ks=ks,psi=psi,where=where,compiled=compiled,elim=elim)
 try:
  rows=[sw._row(k)for k in [None]+eng.keys];A=rows[0]['value'];obs=sum(w*b*r['value'] for w,b,r in zip(eng.W,eng.beta,rows[1:]));loss=(A-obs)/(2*A)
 finally:sw._CTX.clear();sw.COLUMNS.clear()
 result={'scope':'ideal logicalT and instantaneous perfect Bell resource; C->D gate, C/D measurement, and both output B idle clocks noisy','raw':raw,'loss':float(loss),'acceptance':float(A),'single_fault_coefficient':first,'clocks_removed':list(range(7)),'output_idles':2,'no_grid_claim':True,'stem':str(stem)}
 (H/'bell_terminal_result.json').write_text(json.dumps(result,indent=2)+'\n');print('RESULT',json.dumps(result),flush=True)
finally:jq.adjacent=old
