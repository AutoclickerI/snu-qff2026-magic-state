"""C2 readout ideal-input control; all final native CX/read/output idle noise real."""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import json,sys
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[2];sys.path[:0]=[str(R/'work/lanes/FRAME20261027'),str(R/'work/lanes/EXPAND2_20261027'),str(R/'work/tools')]
import frontend_axis as f,frame_tools as ft
from qtools.evaluator import sparse_walsh as sw
import tprep.qasm as jq
ft.f=f;sw.fa=f;sw.parse_current=f.parse_current;ft.OUT=H
D=[6,20,19,10,2,22,16];K=[7,14,13,9,8,21,15];f.DATA=D
PIV={0,1,3};ENC=[[(0,2),(1,5),(3,6)],[(0,4),(1,6),(3,5)],[(0,6),(1,2),(3,4)]]
assert all(abs(d//6-k//6)+abs(d%6-k%6)==1 for d,k in zip(D,K))

def run(mode):
 ops=[f.Op('RX' if i in PIV|{2} else 'R',(q,),0)for i,q in enumerate(D)]
 ops += [f.Op('T',(D[2],),1),f.Op('CX',(D[2],D[4]),2),f.Op('CX',(D[2],D[5]),3)]
 for t,layer in enumerate(ENC,4):ops += [f.Op('CX',(D[a],D[b]),t)for a,b in layer]
 ops += [f.Op('R' if mode=='Xrep' else 'RX',(q,),6)for q in K]
 ops += [f.Op('CX',(d,k)if mode=='Xrep' else(k,d),7)for d,k in zip(D,K)]
 ops += [f.Op('CX',(d,k)if mode=='Xrep' else(k,d),8)for d,k in zip(D,K)]
 ops += [f.Op('M' if mode=='Xrep' else 'MX',(k,),9,i)for i,k in enumerate(K)]
 ops += [f.Op('ID',(d,),9)for d in D]
 ops.sort(key=lambda o:o.time);ds=[{i}for i in range(7)]
 stem=ft.emit('ideal_'+mode,ops,ds,D,metadata={'scope':'ideal input and perfect C2 encoder, actual native decoding CX, K read, D read-clock idles','mode':mode,'input_prep_ideal_through_clock':7,'native_terminal':True})
 old=jq.adjacent
 try:
  jq.adjacent=lambda a,b:a!=b
  raw=ft.raw_check(stem.with_suffix('.qasm').read_text(),D)
  print('RAW',mode,json.dumps(raw),flush=True)
  if not raw['ok']:return
  m,e,groups,nd,ks,psi,where=ft.prepare(stem)
  for cid,ch in enumerate(m.chans):
   if m.labels[ch['ins']].time<8:
    ch['p']=0
    for ff in groups[cid]:ff['p']=0
  _,_,gaps=f.schedule(m.native)
  resized=[]
  for ins,q,start,n in gaps:
   remove=len(set(range(start,start+n))&set(range(8)))
   if not remove or m.labels[ins].time<8:continue
   matches=[(cid,ch)for cid,ch in enumerate(m.chans)if ch['ins']==ins and ch['qs']==[q]and ch['name']=='DEPOLARIZE1']
   assert matches
   cid,ch=max(matches,key=lambda item:item[1]['jl']);oldp=ch['p'];assert abs(oldp-.75*(1-(1-4*.001/3)**n))<1e-12
   ch['p']=.75*(1-(1-4*.001/3)**(n-remove))
   for ff in groups[cid]:ff['p']=ch['p']/3
   resized.append({'q':q,'clock':m.labels[ins].time,'old_wait':n,'new_wait':n-remove})
  c1=0.;cache={};harm=[]
  for ff in m.faults:
   if not ff['p']:continue
   key=ff['s'],ff['d']
   if key not in cache:cache[key]=e.ntable(*key)
   _,n=cache[key];v=0 if n is None else max(0.,float(n[ff['e']]))
   if v>1e-12:c1+=ff['p']/.001*v;harm.append({'label':ff['label'],'value':v})
  compiled,elim=sw.compile_best(m,e,groups,nd,ks,save=False)
  sw._CTX.update(eng=e,ks=ks,psi=psi,where=where,compiled=compiled,elim=elim)
  try:
   rows=[sw._row(k)for k in [None]+e.keys];a=rows[0]['value'];obs=sum(w*b*r['value']for w,b,r in zip(e.W,e.beta,rows[1:]));loss=(a-obs)/(2*a)
  finally:sw._CTX.clear();sw.COLUMNS.clear()
  out={'mode':mode,'scope':'counterfactual perfect encoded logical T and perfect C2 code input; native final inverse CX, K reads and D idle during read are noisy','raw':raw,'loss':float(loss),'acceptance':float(a),'c1':c1,'harmful_singles':harm,'removed_artificial_idle':resized,'source_prep_clocks_exempt':list(range(8)),'kernel_omission_sum':sum(v['absolute_kernel_omission_bound']for v in rows)}
  stem.with_suffix('.diagnostic.json').write_text(json.dumps(out,indent=2)+'\n');print('RESULT',json.dumps({k:v for k,v in out.items()if k not in ('harmful_singles','removed_artificial_idle')}),flush=True)
 finally:jq.adjacent=old
if __name__=='__main__':
 for mode in ('Xrep','Zrep'):run(mode)
