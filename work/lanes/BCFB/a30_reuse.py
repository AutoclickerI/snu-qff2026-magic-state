"""Library A encoders with measured input reuse and explicit native folding."""
from a30_search import *
import stim

def make(t):
 e=t['enc'];R=t['R'];piv=set(e['pivots']);reuse=set(t['reuse']);checks=t['checks'];hop=t.get('hop',0)
 text,md,h,us,ts,tail,init,owned,clean=source();keep=[i for i in range(len(us)) if i not in owned];units=[];times=[];index={}
 for i in keep:
  u=us[i];at=ts[i]+(R-48 if ts[i]>=48 else 0)
  if 2 in reuse and i==max(k for k in range(init[2]) if 2 in us[k].qs):
   assert u.name=='MX';u=U(u.lines+[f'h q[2];'] if len(u.lines)==2 else u.lines)
  if hop and (u.qs==(22,) and u.name=='RESET' and ts[i]>34 or u.name=='CX' and set(u.qs)=={16,22}):at-=hop
  index[i]=len(units);units.append(u);times.append(at)
 release={q:max(times[index[i]] for i in keep if q in us[i].qs and i<init[q]) for q in A};nextt={q:R for q in A};new=[]
 for a,b in reversed(e['ops']):
  at=min(nextt[a],nextt[b])-1;new.append((cx(a,b),at));nextt[a]=nextt[b]=at
 for q in A:
  at=nextt[q]-1
  if q in checks:new.append((mx(q,310+q) if q in piv else mz(q,310+q),at));clean.append(f'// DETECTOR c[{310+q}]');at-=1
  if q in reuse:
   if q==2:
    if q not in piv:raise ValueError('q2 reuse expects X')
   elif q in (1,8,9,15,16):
    if q in piv:new.append((U([f'h q[{q}];']),at));at-=1
   else:raise ValueError('unsupported reuse basis')
   if at<release[q]:raise ValueError('reuse does not fit')
  else:
   if at<=release[q]:raise ValueError('init does not fit')
   if q in (8,16) and q not in piv:new.append((mz(q,350+q),at));clean.append(f'// DETECTOR c[{350+q}]')
   else:new.append((initu(q,q in piv),at))
 for u,at in new:units.append(u);times.append(at)
 return finish(h,units,times,clean,md,dict(kind='reuse',spec=t,R=R))
def candidates():
 es=library()+[dict(name=f'acheck_{k}',pivots=e['pivots'],ops=[ab for L in e['ops'] for ab in L]) for k,e in enumerate(json.loads((D/'inputs/acheck_encoders.json').read_text()))]
 for e in es:
  for reuse in [[],[2],[8],[16],[1,2],[1,2,8,16],[1,2,8,9,15,16]]:
   if 2 in reuse and 2 not in e['pivots']:continue
   for checks in [[],[q for q in (1,2,9) if q not in reuse],e['pivots']]:
    for R in [48,49,50]:yield dict(enc=e,reuse=reuse,checks=checks,R=R)
 # Early release of A16 is an actual transplant including the existing data hop.
 for e in library():
  for hop in [1,2,3]:
   for reuse in [[],[2],[16],[1,2,8,16]]:
    if 2 in reuse and 2 not in e['pivots']:continue
    for checks in [[],[1,2,9],e['pivots']]:yield dict(enc=e,reuse=reuse,checks=checks,R=48,hop=hop)
def worker(t):
 try:
  text,md=make(t);ev=exact2.Eval(text,md['data_qubits']);assert ev.e.A0>1-1e-10;c1=float(ev.fp@ev.n_single)
  r=dict(evaluate(ev),status='SCREENED') if abs(c1)<1e-12 else dict(c1=c1,status='INVALID_C1');r.update(CX=md['CX'],R=md['R'],native_depth=md['native_depth']);return r,text,md,t
 except Exception as e:return dict(status='INVALID',error=repr(e)),None,None,t
def main(procs):
 db=sqlite3.connect(D/'reuse.sqlite');db.execute('create table if not exists results(id integer primary key,row text,witness blob,qasm blob,md text)');n=0;best=1.
 with concurrent.futures.ProcessPoolExecutor(max_workers=procs) as pool:
  for r,text,md,t in pool.map(worker,candidates(),chunksize=4):
   n+=1;db.execute('insert into results values(?,?,?,?,?)',(n,json.dumps(r),zlib.compress(json.dumps(t).encode()),zlib.compress(text.encode()) if text else None,json.dumps(md)))
   if n%500==0:db.commit();print('COUNT',n,flush=True)
   if r.get('exp_minus_A1',0)>=.5002 and r.get('total',1)<best:
    best=r['total'];stem=D/'finalists'/f'a30_reuse_{n:05}';stem.with_suffix('.qasm').write_text(text);stem.with_suffix('.json').write_text(json.dumps(md,indent=2));stem.with_suffix('.screen.json').write_text(json.dumps(r,indent=2));print('BEST',stem.name,json.dumps(r),flush=True)
 db.commit();print('DONE',n,best,flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--procs',type=int,default=12);main(p.parse_args().procs)
