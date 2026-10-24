"""Stagger A's data coupling/readout after each endpoint's last encoder use."""
from a30_search import *
from a30_local import buildlocal

def make(spec):
 if spec.get('local') is not None:text,md=buildlocal(spec['local']);h,raw,tail=S.qasm_ops(text);us=S.fold_units(raw);ts=native_times(text,us)
 else:text,md,h,us,ts,tail,*_=source()
 coupling={q:next(i for i,u in enumerate(us) if u.name=='CX' and edge(u)==(d,q) and ts[i]==48) for d,q in zip(DATA,A)}
 read={q:next(i for i,u in enumerate(us) if u.name=='MEASURE' and u.qs==(q,) and ts[i]>=48) for q in A}
 for q,t in spec['couplings'].items():
  q=int(q);ts[coupling[q]]=t
  if q!=16:ts[read[q]]=t+1
 # Retain source per-wire order except unrelated units can interleave.
 pred,succ=S.build_dag(us)
 assert S.feasible(ts,us,pred,succ),'wire order'
 return finish(h,us,ts,tail,md,dict(kind='stagger',spec=spec,R=48))
def tasks():
 for t9 in range(43,49):
  for t15 in range(47,49):
   for t16 in range(46,49):yield dict(couplings={9:t9,15:t15,16:t16})
 # Move q9's complete start one native tick earlier, plus A8's MZ initialization.
 _,_,_,us,ts,_,init,owned,_=source()
 for delta in (1,2):
  shift={str(i):-delta for i in owned if us[i].qs==(9,) or (us[i].name=='CX' and edge(us[i])==(9,8)) or i==init[8]}
  for t9 in range(43-delta,49):
   for t15 in (47,48):
    yield dict(couplings={9:t9,15:t15,16:46},local=dict(shift=shift,remove=[],init={},extra=[]))
def worker(spec):
 try:
  text,md=make(spec);ev=exact2.Eval(text,md['data_qubits']);assert ev.e.A0>1-1e-10;c1=float(ev.fp@ev.n_single)
  r=dict(evaluate(ev),status='SCREENED') if abs(c1)<1e-12 else dict(c1=c1,status='INVALID_C1')
  r.update(CX=md['CX'],R=md['R'],native_depth=md['native_depth']);return r,text,md,spec
 except Exception as e:return dict(status='INVALID',error=repr(e)),None,None,spec
def main(procs):
 db=sqlite3.connect(D/'stagger.sqlite');db.execute('create table if not exists results(id integer primary key,row text,witness blob,qasm blob,md text)');best=1.;n=0
 with concurrent.futures.ProcessPoolExecutor(max_workers=procs) as pool:
  for r,text,md,spec in pool.map(worker,tasks()):
   n+=1;db.execute('insert into results values(?,?,?,?,?)',(n,json.dumps(r),zlib.compress(json.dumps(spec).encode()),zlib.compress(text.encode()) if text else None,json.dumps(md)))
   if r.get('exp_minus_A1',0)>=.5002 and r.get('total',1)<best:
    best=r['total'];stem=D/'finalists'/f'a30_stagger_{n:04}';stem.with_suffix('.qasm').write_text(text);stem.with_suffix('.json').write_text(json.dumps(md,indent=2));stem.with_suffix('.screen.json').write_text(json.dumps(r,indent=2));print('BEST',stem.name,json.dumps(r),flush=True)
 db.commit();print('DONE',n,best,flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--procs',type=int,default=8);main(p.parse_args().procs)
