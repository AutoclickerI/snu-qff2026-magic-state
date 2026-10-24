"""Full-context timing/check coordinate search; exact Fourier prices every move."""
from a30_search import *
import math
BASE=source()

def original():
 text,md,h,us,ts,tail,init,owned,clean=BASE
 return dict(shift={},remove=[],init={},extra=[])

def buildlocal(opt):
 text,md,h,us,ts,tail,init,owned,clean=BASE;units=[];times=[];tail=list(tail)
 shifts={int(k):v for k,v in opt.get('shift',{}).items()};remove=set(opt.get('remove',[]));modes={int(k):v for k,v in opt.get('init',{}).items()}
 oldbits=set();prev_fix=set()
 for q,mode in modes.items():
  if mode=='reuse' and q in (2,):
   i=max(i for i in range(init[q]) if q in us[i].qs);assert us[i].name=='MX';prev_fix.add(i)
 for i,u in enumerate(us):
  if i in remove:
   if u.name in ('MX','MEASURE'):oldbits.add(bit(u))
   continue
  if i in prev_fix and len(u.lines)==2:u=U(u.lines+[f'h q[{u.qs[0]}];'])
  if i in init.values():
   q=u.qs[0];mode=modes.get(q,'keep')
   if mode!='keep':
    if u.name in ('MX','MEASURE'):oldbits.add(bit(u))
    plus=q in [1,2,9,15]
    if mode=='reset':u=initu(q,plus)
    elif mode=='measure':u=mx(q,330+q) if plus else mz(q,330+q);tail.append(f'// DETECTOR c[{330+q}]')
    elif mode=='reuse':
     if q in [1,9,15]:u=U([f'h q[{q}];'])
     elif q in [2,8,14,16]:continue
     else:raise ValueError(mode)
    else:raise ValueError(mode)
  units.append(u);times.append(ts[i]+shifts.get(i,0))
 tail=[l for l in tail if not (set(map(int,BITS.findall(l)))&oldbits)]
 for q,t,pauli in opt.get('extra',[]):
  units.append(mx(q,370+q) if pauli=='X' else mz(q,370+q));times.append(t);tail.append(f'// DETECTOR c[{370+q}]')
 # Preserve every source per-wire order; sorting by changed time must never swap dependent gates.
 pred,succ=S.build_dag(units[:len(units)-len(opt.get('extra',[]))] if opt.get('extra') else units)
 for i,ps in enumerate(pred):
  for j in ps:
   if times[i]<=times[j]:raise ValueError('source wire order')
 return finish(h,units,times,tail,md,dict(kind='local',edit=opt,R=48))

def price_local(opt):
 try:
  text,md=buildlocal(opt);ev=exact2.Eval(text,md['data_qubits']);c1=float(ev.fp@ev.n_single)
  if abs(c1)>=1e-12:r=dict(status='INVALID_C1',c1=c1)
  else:r=dict(evaluate(ev),status='SCREENED')
  r.update(CX=md['CX'],R=md['R'],native_depth=md['native_depth'],sha=hashlib.sha256(text.encode()).hexdigest())
  return r,text,md,opt
 except Exception as e:return dict(status='INVALID',error=repr(e)),None,None,opt

def neighbors(o,wide=False):
 _,_,_,us,ts,tail,init,owned,_=BASE
 for i in sorted(owned):
  if i in o['remove']:continue
  for d in (-2,-1,1,2) if wide else (-1,1):
   z=json.loads(json.dumps(o));z['shift'][str(i)]=z['shift'].get(str(i),0)+d;yield z
  if us[i].name in ('MX','MEASURE') and i not in init.values():
   z=json.loads(json.dumps(o));z['remove'].append(i);yield z
 for q in A:
  for mode in ['keep','reset','measure','reuse']:
   if o['init'].get(str(q),'keep')==mode:continue
   z=json.loads(json.dumps(o));z['init'][str(q)]=mode;yield z
  for t in range(ts[init[q]],48):
   if q in [x[0] for x in o['extra']]:continue
   for pauli in ['X','Z']:
    z=json.loads(json.dumps(o));z['extra'].append([q,t,pauli]);yield z

def main(procs):
 db=sqlite3.connect(D/'local.sqlite');db.execute('create table if not exists results(id integer primary key,row text,witness blob,qasm blob,md text)')
 seen=set();best=5.8239331514201564e-5;current=original();n=0;rounds=0
 with concurrent.futures.ProcessPoolExecutor(max_workers=procs) as pool:
  while True:
   rounds+=1;improvement=None
   opts=[]
   for o in neighbors(current,True):
    k=json.dumps(o,sort_keys=True)
    if k not in seen:seen.add(k);opts.append(o)
   for r,text,md,o in pool.map(price_local,opts):
    n+=1;db.execute('insert into results values(?,?,?,?,?)',(n,json.dumps(r),zlib.compress(json.dumps(o).encode()),zlib.compress(text.encode()) if text else None,json.dumps(md)))
    if r.get('exp_minus_A1',0)>=.5002 and r.get('total',1)<best-1e-13:
     best=r['total'];improvement=o;stem=D/'finalists'/f'a30_local_{n:05}'
     stem.with_suffix('.qasm').write_text(text);stem.with_suffix('.json').write_text(json.dumps(md,indent=2));stem.with_suffix('.screen.json').write_text(json.dumps(r,indent=2));print('BEST',stem.name,json.dumps(r),flush=True)
   db.commit();print('ROUND',rounds,n,best,flush=True)
   if improvement is None:break
   current=improvement
 (D/'runs/local.receipt.json').write_text(json.dumps(dict(rounds=rounds,priced=n,best=best,status='LOCAL_OPTIMUM'),indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--procs',type=int,default=8);main(p.parse_args().procs)
