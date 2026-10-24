"""In-preparation A flag windows and internal X-parity checks."""
from a30_search import *
import stim

def buildflag(t):
 e=t['enc'];f=t['flag'];piv=set(e['pivots']);events=[];R=t['R']
 if t['kind']=='window':
  a,b=t['window'];q=t['target']
  for i,ab in enumerate(e['ops']):
   if i==a:events.append(cx(f,q))
   if i==b:events += [cx(f,q),mx(f,300)]
   events.append(cx(*ab))
 else:
  for i,ab in enumerate(e['ops']):
   if i==t['boundary']:
    events += [cx(f,q) for q in t['support']]+[mx(f,300)]
    if f not in piv:events.append(initu(f,False))
   events.append(cx(*ab))
 # Independently verify every ideal flag is deterministic and final A state is unchanged.
 sim=stim.TableauSimulator();sim.reset(*A);sim.h(*sorted(piv|{f}))
 for u in events:
  if u.name=='CX':sim.cx(*edge(u))
  elif u.name=='MX':
   ps=stim.PauliString(36);ps[f]='X';assert sim.peek_observable_expectation(ps)==1,'random flag';sim.postselect_x(f,desired_value=False)
  elif u.name=='RESET':sim.reset(f)
  else:raise ValueError(u.name)
 for basis,supp in [('X',[A[i] for i in row]) for row in ROWS]+[('Z',[A[i] for i in row]) for row in ROWS]+[('X',A)]:
  ps=stim.PauliString(36)
  for q in supp:ps[q]=basis
  assert sim.peek_observable_expectation(ps)==1,'wrong flagged state'
 text,md,h,us,ts,tail,init,owned,clean=source();keep=[i for i in range(len(us)) if i not in owned]
 units=[us[i] for i in keep];times=[ts[i]+(R-48 if ts[i]>=48 else 0) for i in keep]
 release={q:max(ts[i] for i in keep if q in us[i].qs and i<init[q]) for q in A};nextt={q:R for q in A};new=[]
 for u in reversed(events):
  at=min(nextt[q] for q in u.qs)-1;new.append((u,at))
  for q in u.qs:nextt[q]=at
 clean+=['// DETECTOR c[300]']
 for q in A:
  at=nextt[q]-1;plus=q in piv or q==f
  if q in t.get('checks',[]):new.append((mx(q,310+q) if plus else mz(q,310+q),at));clean.append(f'// DETECTOR c[{310+q}]');at-=1
  if at<=release[q]:raise ValueError('flag does not fit')
  if q in (8,16) and not plus:new.append((mz(q,350+q),at));clean.append(f'// DETECTOR c[{350+q}]')
  else:new.append((initu(q,plus),at))
 for u,at in new:units.append(u);times.append(at)
 return finish(h,units,times,clean,md,dict(kind='internal_flag',spec=t,R=R))

def candidates():
 enc=library()+[dict(name=f'acheck_{k}',pivots=e['pivots'],ops=[ab for L in e['ops'] for ab in L]) for k,e in enumerate(json.loads((D/'inputs/acheck_encoders.json').read_text()))]
 for e in enc:
  ops=e['ops']
  # Single target, two-CX window. f has not yet joined the encoder.
  for f in e['pivots']:
   first=next((i for i,ab in enumerate(ops) if f in ab),len(ops))
   for q in A:
    if abs(q//6-f//6)+abs(q%6-f%6)!=1:continue
    for a in range(first):
     v={q}
     for b in range(a+1,first+1):
      u,w=ops[b-1]
      if u in v:v.symmetric_difference_update({w})
      if v!={q} or not any(q in ab for ab in ops[a:b]):continue
      for R in [48,49,50,51]:
       yield dict(kind='window',enc=e,flag=f,target=q,window=[a,b],R=R,checks=[])
  # Three-CX star using the internal A15 input before it joins the encoder.
  f=15;first=next((i for i,ab in enumerate(ops) if f in ab),len(ops));vec=[{p} for p in e['pivots']]
  for i in range(first+1):
   span={frozenset()}
   for v in vec:span|={frozenset(set(w)^v) for w in list(span)}
   if i and frozenset({9,14,16}) in span:
    for order in itertools.permutations([9,14,16]):
     for R in [48,49,50,51]:yield dict(kind='star',enc=e,flag=f,support=order,boundary=i,R=R,checks=[])
   if i<first:
    u,w=ops[i]
    for v in vec:
     if u in v:v.symmetric_difference_update({w})

def worker(t):
 try:
  text,md=buildflag(t);ev=exact2.Eval(text,md['data_qubits']);assert ev.e.A0>1-1e-10
  c1=float(ev.fp@ev.n_single)
  r=dict(evaluate(ev),status='SCREENED') if abs(c1)<1e-12 else dict(c1=c1,status='INVALID_C1')
  r.update(CX=md['CX'],R=md['R'],native_depth=md['native_depth'],sha=hashlib.sha256(text.encode()).hexdigest());return r,text,md,t
 except Exception as e:return dict(status='INVALID',error=repr(e)),None,None,t

def main(procs):
 db=sqlite3.connect(D/'flags.sqlite');db.execute('create table if not exists results(id integer primary key,row text,witness blob,qasm blob,md text)');best=1.;n=0;seen=set()
 with concurrent.futures.ProcessPoolExecutor(max_workers=procs) as pool:
  for r,text,md,t in pool.map(worker,candidates(),chunksize=8):
   if r.get('sha') in seen:continue
   if r.get('sha'):seen.add(r['sha'])
   n+=1;db.execute('insert into results values(?,?,?,?,?)',(n,json.dumps(r),zlib.compress(json.dumps(t).encode()),zlib.compress(text.encode()) if text else None,json.dumps(md)))
   if n%500==0:db.commit();print('COUNT',n,flush=True)
   if r.get('exp_minus_A1',0)>=.5002 and r.get('total',1)<best:
    best=r['total'];stem=D/'finalists'/f'a30_flag_{n:06}';stem.with_suffix('.qasm').write_text(text);stem.with_suffix('.json').write_text(json.dumps(md,indent=2));stem.with_suffix('.screen.json').write_text(json.dumps(r,indent=2));print('BEST',stem.name,json.dumps(r),flush=True)
 db.commit();print('DONE',n,best,flush=True);(D/'runs/flags.receipt.json').write_text(json.dumps(dict(priced=n,best=best,status='COMPLETED'),indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--procs',type=int,default=8);main(p.parse_args().procs)
