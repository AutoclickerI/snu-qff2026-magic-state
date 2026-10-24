import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
os.environ['BCFB_BLUE_DB']='neighbors.sqlite'
from pathlib import Path
import json,itertools,random,time,argparse
from blue_evaluate import price,H
from build import source,B,C
p=argparse.ArgumentParser();p.add_argument('stems',nargs='+');a=p.parse_args();rng=random.Random(917)
for stem in a.stems:
 f=H/'finalists'/stem;md=json.loads(f.with_suffix('.json').read_text());d=md['prep'];opt=md['options'];context=opt['context'];src,head,us,ts,tail,ini,rem=source(context);piv=set(d['pivots']);mx=set(opt.get('mx',piv));mz=set(opt.get('mz',[q for q in B+C if us[ini[q]].name=='MEASURE']))-piv
 best=json.loads(f.with_suffix('.screen.json').read_text())['total'];rows=[];start=time.monotonic()
 variants=[('init_'+str(q),[q]) for q in B+C]+[('init_'+str(q)+'_'+str(r),[q,r]) for q,r in itertools.combinations(B+C,2)]
 for key,toggle in variants:
  xx=mx.copy();zz=mz.copy()
  for q in toggle:
   if q in piv:xx^={q}
   else:zz^={q}
  no=dict(opt,mx=sorted(xx),mz=sorted(zz));row=price(d,no,'neighbor_'+stem+'_'+key,'blue_init_neighbor',threshold=best+1e-12);rows.append(row)
 for qs in [[],*[list(qs) for n in [1,2] for qs in itertools.combinations(B+C,n)]]:
  no=dict(opt,init_checks=qs);key='check_'+('_'.join(map(str,qs)) or 'none');row=price(d,no,'neighbor_'+stem+'_'+key,'blue_check_neighbor',threshold=best+1e-12);rows.append(row)
 rec=dict(stem=stem,status='COMPLETE',prices=len(rows),seconds=time.monotonic()-start,best=min((r.get('total',1) for r in rows)),best_eligible=min((r.get('total',1) for r in rows if r.get('exp_minus_A1',0)>=.5),default=None));(H/'runs'/('neighbor_'+stem+'.receipt.json')).write_text(json.dumps(rec,indent=2));print(json.dumps(rec),flush=True)
