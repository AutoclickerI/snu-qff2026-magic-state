"""Region removal changes noise probabilities only, including exact idle composition."""
from regions import *
import contextlib,io,argparse
sys.path.insert(0,str(V/'sparse'));import sparse_walsh as sw
def masked(original,schedule,keep):
 def run(text,p,*args,**kw):
  prog,blocks=original(text,p,*args,**kw);_,steps,gaps=schedule(text);idle=collections.defaultdict(list)
  for i,q,first,n in gaps:idle[i].append((q,first,n))
  for i,(ins,block)in enumerate(zip(prog,blocks)):
   t=min((s for _,s in steps[i]),default=0);ni=len(idle[i]);start=len(block)-ni
   for j,line in enumerate(block):
    if '('not in line or not line.startswith(('DEPOLARIZE','X_ERROR','Z_ERROR')):continue
    if j>=start and ni:
     q,first,n=idle[i][j-start];count=sum(region([q],tt,True)in keep for tt in range(first,first+n))
     if count!=n:block[j]=re.sub(r'\([^)]*\)',f'({.75*(1-(1-4*p/3)**count)})',line,count=1)
    elif region(ins.qubits,t)not in keep:block[j]=re.sub(r'\([^)]*\)','(0)',line,count=1)
  return prog,blocks
 return run
def price(label,procs):
 keep=set(REGIONS)if label=='all'else({label[5:]}if label.startswith('only_')else set(REGIONS)-{label[3:]});old=sw.fa.noise_blocks
 sw.fa.noise_blocks=masked(old,sw.fa.schedule,keep);od=V/'ledger'/label;od.mkdir(parents=True,exist_ok=True);sw.__file__=str(od/'sparse_walsh.py')
 try:
  with(od/'sparse.log').open('w')as f,contextlib.redirect_stdout(f):r=sw.run(V/'base',72,True,procs=procs)
 finally:sw.fa.noise_blocks=old
 r['label']=label;(V/'ledger'/f'{label}.json').write_text(json.dumps(r,indent=2));print(label,r['loss'],r['acceptance'],flush=True)
 publish();return r
def publish():
 files=list((V/'ledger').glob('*.json'));rows=[r for f in files if'label'in(r:=json.loads(f.read_text()))];base=next((r for r in rows if r['label']=='all'),None)
 if base is None:return
 rows.sort(key=lambda r:base['loss']-r['loss'],reverse=True);out=['# v36a all-orders noise ledger','','Removal gains overlap and are not additive. The circuit, detector predicate and all outcomes are unchanged; only the selected noise is disabled.','',f'Baseline: 1−F={base["loss"]:.12e}, acceptance={base["acceptance"]:.12f}.','','| Removed region | Loss after removal | Loss saved | Acceptance after removal |','|---|---:|---:|---:|']
 for r in rows:
  if r['label'].startswith('no_'):out.append(f'| {r["label"][3:]} | {r["loss"]:.12e} | {base["loss"]-r["loss"]:.12e} | {r["acceptance"]:.9f} |')
 out+=['','Definitions: `ledger/regions.json`. Full73-moment receipts are saved per removal. The top physical-pair classes are generated independently.','']
 (V/'LEDGER.md').write_text('\n'.join(out));p=H/'REPORT.md';text=p.read_text();tail=text.split('<!-- integration -->',1)[-1]if'<!-- integration -->'in text else'';p.write_text('Status: RUNNING — P75 integration on v36a; acceptance floor0.5002.\n\n'+'\n'.join(out)+'\n<!-- integration -->\n'+tail)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--procs',type=int,default=6);p.add_argument('labels',nargs='*');a=p.parse_args();(V/'ledger').mkdir(exist_ok=True);(V/'ledger/regions.json').write_text(json.dumps(manifest(),indent=2))
 for label in a.labels or['all']+['no_'+r for r in REGIONS]:
  if(V/'ledger'/f'{label}.json').exists():publish();continue
  price(label,a.procs)
