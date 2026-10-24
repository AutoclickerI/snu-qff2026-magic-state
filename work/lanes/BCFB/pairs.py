"""In-situ clean identities: add/delete adjacent canceling BC CX pairs.
All non-BC gates, their native times and detector records remain fixed.
"""
import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import argparse,json,itertools,hashlib,concurrent.futures
from pathlib import Path
from build import H,S,native_times,B,C
from synth import nb,verify
from scan import save_screen

def candidate(job):
 tag,text,md,change=job;return save_screen(tag,'identity_pairs',text,md,change)
def main():
 p=argparse.ArgumentParser();p.add_argument('stem');p.add_argument('--workers',type=int,default=4);p.add_argument('--commuting',action='store_true');a=p.parse_args();stem=Path(a.stem);stem=stem if stem.is_absolute() else H/a.stem
 text=stem.with_suffix('.qasm').read_text();md=json.loads(stem.with_suffix('.json').read_text());h,raw,tail=S.qasm_ops(text);u=S.fold_units(raw);ts=native_times(text,u);R=md['R'];cells=B+C
 init={q:max(i for i,x in enumerate(u) if x.qs==(q,) and ts[i]<R and x.name in ('RX','RESET','MX','MEASURE')) for q in cells};ids=[i for i,x in enumerate(u) if x.name=='CX' and ts[i]<R and set(x.qs)<=set(cells) and all(i>init[q] for q in x.qs)]
 def witness(nu,nt):
  ops=[[] for _ in range(R)]
  for x,t in zip(nu,nt):
   if x.name=='CX' and t<R and set(x.qs)<=set(cells) and all(t>ts[init[q]] for q in x.qs):ops[t].append(list(map(int,__import__('re').findall(r'q\[(\d+)\]',x.lines[0]))))
  d=dict(md['prep'],ops=[l for l in ops if l]);return d,verify(d)
 jobs=[]
 def add(nu,nt,change):
  d,v=witness(nu,nt)
  if not (v['stim_target_pass'] and v['clean_pass']):return
  txt=S.emit(h,nu,nt,tail);_,rr,_=S.qasm_ops(txt);units=S.fold_units(rr);times=native_times(txt,units);order=sorted(range(len(nu)),key=lambda i:(nt[i],i));assert [nt[i] for i in order]==times
  sig=hashlib.sha256(txt.encode()).hexdigest()[:12];tag=f'pair_{stem.name}_{sig}';nmd=dict(md,prep=d,verification=v,CX=sum(x.name=='CX' for x in nu),pair_change=change);jobs.append((tag,txt,nmd,change))
 for i in ids:
  q=u[i].qs;nexts=[j for j in ids if j>i and set(q)&set(u[j].qs)]
  if nexts and u[nexts[0]].lines==u[i].lines:
   j=nexts[0];add([x for k,x in enumerate(u) if k not in (i,j)],[t for k,t in enumerate(ts) if k not in (i,j)],dict(kind='delete',units=[i,j],times=[ts[i],ts[j]],lines=u[i].lines))
 for q in cells:
  for r in nb(q):
   if r not in cells:continue
   occ={t for x,t in zip(u,ts) if q in x.qs or r in x.qs};lo=max(ts[init[q]],ts[init[r]])+1
   free=[t for t in range(lo,R) if t not in occ]
   for t,t2 in itertools.combinations(free,2):
    if not a.commuting and t2!=t+1:continue
    good=True
    for x,tt in zip(u,ts):
     if not t<tt<t2 or not ({q,r}&set(x.qs)):continue
     if x.name!='CX':good=False;break
     c,d=map(int,__import__('re').findall(r'q\[(\d+)\]',x.lines[0]))
     if q==d or r==c:good=False;break
    if not good:continue
    op=S.Unit([f'cx q[{q}],q[{r}];'],[]);add(u+[op,op],ts+[t,t2],dict(kind='add',edge=[q,r],times=[t,t2],commuting=a.commuting))
 with concurrent.futures.ProcessPoolExecutor(max_workers=a.workers) as e:rows=list(e.map(candidate,jobs))
 out=dict(status='COMPLETE',prices=len(rows),best=min((r.get('total',1) for r in rows),default=None));(H/'runs'/f'pairs_{stem.name}.receipt.json').write_text(json.dumps(out,indent=2));print(json.dumps(out),flush=True)
if __name__=='__main__':main()
