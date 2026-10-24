"""A-only v30f encoder, schedule, and post-coupling parity-check search."""
from a30_common import *
import itertools,random,hashlib,sqlite3,zlib,time,traceback,concurrent.futures,argparse
from moments_batch import evaluate,exact2

def U(lines):return S.Unit(lines,[])
def cx(a,b):
 assert abs(a//6-b//6)+abs(a%6-b%6)==1,(a,b)
 return U([f'cx q[{a}],q[{b}];'])
def mz(q,c):return U([f'measure q[{q}] -> c[{c}];'])
def mx(q,c,retain=True):return U([f'h q[{q}];',f'measure q[{q}] -> c[{c}];']+([f'h q[{q}];'] if retain else []))
def initu(q,plus):return U([f'reset q[{q}];']+([f'h q[{q}];'] if plus else []))
def finish(h,units,times,tail,md,options):
 order=sorted(range(len(units)),key=lambda i:(times[i],i));units=[units[i] for i in order];times=[times[i] for i in order]
 assert S.feasible(times,units,*S.build_dag(units))
 h=[re.sub(r'creg c\[\d+\]','creg c[400]',l) for l in h]
 text=S.emit(h,units,times,tail)
 _,raw,_=S.qasm_ops(text);fold=S.fold_units(raw)
 assert [u.lines for u in fold]==[u.lines for u in units], 'native folding changed'
 actual=native_times(text,fold)
 assert actual==times,('native times changed',[(i,a,b) for i,(a,b) in enumerate(zip(actual,times)) if a!=b][:8])
 out={k:md[k] for k in ('data_qubits',) };out.update(CX=sum(u.name=='CX' for u in units),R=options.get('R',md['R']),native_depth=max(times)+1,base='v30f',options=options)
 return text,out

def postchecks(spec,base=None):
 if base is None:text,md,h,us,ts,tail,*_=source()
 else:
  text,md=base;h,raw,tail=S.qasm_ops(text);us=S.fold_units(raw);ts=native_times(text,us)
 # Each gadget = flag, support, pre-conjugation edges, root targets, post-conjugation edges.
 selected=set(q for g in spec for q in g['support']);flags={g['flag'] for g in spec}
 assert not selected&flags
 read={q:next(i for i,(u,t) in enumerate(zip(us,ts)) if u.name=='MEASURE' and u.qs==(q,) and t>=md['R']) for q in A}
 keep=[i for i in range(len(us)) if i not in {read[q] for q in selected}]
 units=[us[i] for i in keep];times=[ts[i] for i in keep];last={q:max(t for u,t in zip(units,times) if q in u.qs) for q in A}
 def add(u,lower=0):
  t=max([lower]+[last[q]+1 for q in u.qs]);units.append(u);times.append(t)
  for q in u.qs:last[q]=t
 # Initialize all flags before gadget sequence; independent instructions can overlap.
 for f in flags:add(initu(f,True))
 for k,g in enumerate(spec):
  for a,b in g.get('pre',[]):add(cx(a,b))
  for q in g['roots']:add(cx(g['flag'],q))
  for a,b in g.get('post',[]):add(cx(a,b))
  add(mx(g['flag'],300+k,False));tail=tail+[f'// DETECTOR c[{300+k}]']
 for q in sorted(selected):add(us[read[q]])
 return finish(h,units,times,tail,md,dict(kind='post_X',gadgets=spec,R=md['R']))

def prep(enc,checks=(1,2,9),R=48,slack=None,reset_all=False):
 text,md,h,us,ts,tail,init,owned,clean=source();piv=set(enc['pivots']);ops=enc['ops']
 # Verify the isolated plus state, including all three X/Z stabilizers and logical X.
 import stim
 c=stim.Circuit();c.append('R',A);c.append('H',sorted(piv))
 for a,b in ops:c.append('CX',[a,b])
 sim=stim.TableauSimulator();sim.do(c)
 for basis,supp in [('X',[A[i] for i in row]) for row in ROWS]+[('Z',[A[i] for i in row]) for row in ROWS]+[('X',A)]:
  p=stim.PauliString(36)
  for q in supp:p[q]=basis
  assert sim.peek_observable_expectation(p)==1,('wrong encoder',basis,supp)
 keep=[i for i in range(len(us)) if i not in owned];units=[us[i] for i in keep];times=[ts[i]+(R-md['R'] if ts[i]>=md['R'] else 0) for i in keep]
 release={q:max(ts[i] for i in keep if q in us[i].qs and i<init[q]) for q in A}
 nextt={q:R for q in A};new=[];slack=slack or {}
 for k,(a,b) in reversed(list(enumerate(ops))):
  t=min(nextt[a],nextt[b])-1-int(slack.get(str(k),0));new.append((cx(a,b),t));nextt[a]=nextt[b]=t
 for q in A:
  t=nextt[q]-1
  if q in checks:new.append((mx(q,310+q) if q in piv else mz(q,310+q),t));clean.append(f'// DETECTOR c[{310+q}]');t-=1
  if not reset_all and q in (8,16) and q not in piv:
   new.append((mz(q,350+q),t));clean.append(f'// DETECTOR c[{350+q}]')
  else:new.append((initu(q,q in piv),t))
  if t<=release[q]:raise ValueError(f'prep does not fit: q{q} init {t} release {release[q]}')
 for u,t in new:units.append(u);times.append(t)
 return finish(h,units,times,clean,md,dict(kind='encoder',encoder=enc,checks=list(checks),R=R,slack=slack,reset_all=reset_all))

def rowkey(rows):
 rr=list(rows)
 for i in range(3):
  j=min(range(i,3),key=lambda j:(rr[j]&-rr[j]).bit_length());rr[i],rr[j]=rr[j],rr[i];b=rr[i]&-rr[i]
  for j in range(3):
   if j!=i and rr[j]&b:rr[j]^=rr[i]
 return sum(r<<(7*i) for i,r in enumerate(rr))
def library():
 info=json.loads((D/'inputs/library_input.json').read_text());out=[]
 for kind in ['library_encoders','library_depth_encoders']:
  lib=json.loads((D/'inputs'/f'{kind}.json').read_text())
  for emb in info['embeddings']:
   sid,*qs=emb
   if set(qs)!=set(A):continue
   p=[qs.index(q) for q in A];cid=info['targets'].index(rowkey([sum(1<<p[i] for i in row) for row in ROWS]))
   e=lib[sid][cid]
   out.append(dict(name=f'{kind}_{sid}_{cid}_{qs[0]}',pivots=[qs[i] for i in range(7) if i not in e['pivots']],ops=[[qs[b],qs[a]] for a,b in e['ops']]))
 text,md,h,us,ts,tail,init,owned,clean=source()
 out.append(dict(name='source',pivots=[1,2,9,15],ops=[list(edge(us[i])) for i in sorted(owned) if us[i].name=='CX']))
 seen=set();unique=[]
 for e in out:
  key=json.dumps([sorted(e['pivots']),e['ops']])
  if key not in seen:seen.add(key);unique.append(e)
 return unique

def reordered(e,rng):
 ops=e['ops'];pred=[{j for j in range(i) if ops[j][0]==ops[i][1] or ops[j][1]==ops[i][0]} for i in range(len(ops))]
 left=set(range(len(ops)));order=[]
 while left:
  ready=[i for i in left if not pred[i]&left];i=rng.choice(ready);order.append(i);left.remove(i)
 return dict(e,name=e['name']+'_order',ops=[ops[i] for i in order])

def tasks(mode):
 if mode=='post':
  for perm in itertools.permutations([9,14,16]):
   a=dict(flag=15,support=[9,14,16],roots=list(perm));yield dict(kind='post',spec=[a])
  b=dict(flag=2,support=[1,8,14],pre=[[8,14]],roots=[8,1],post=[[8,14]])
  # Avoid direct CX2->1 before inverse conjugation only if disjoint dependency requires; all commute here.
  for roots in ([8,1],[1,8]):
   b=dict(b,roots=roots);yield dict(kind='post',spec=[b])
   for perm in itertools.permutations([9,14,16]):
    a=dict(flag=15,support=[9,14,16],roots=list(perm))
    yield dict(kind='post',spec=[a,b]);yield dict(kind='post',spec=[b,a])
 elif mode=='acheck':
  for k,e in enumerate(json.loads((D/'inputs/acheck_encoders.json').read_text())):
   e=dict(name=f'acheck_{k}',pivots=e['pivots'],ops=[ab for layer in e['ops'] for ab in layer])
   for checks in [[],[1,2,9],e['pivots'],A]:
    for R in range(48,53):yield dict(kind='prep',enc=e,checks=checks,R=R)
 elif mode=='library':
  rng=random.Random(3401)
  for e in library():
   variants=[e]+[reordered(e,rng) for _ in range(15)]
   for v in variants:
    for checks in [[],[1,2,9],v['pivots'],A]:
     for R in range(48,52):yield dict(kind='prep',enc=v,checks=checks,R=R)

def work(t):
 start=time.monotonic()
 try:
  if t['kind']=='post':text,md=postchecks(t['spec'])
  else:text,md=prep(t['enc'],t['checks'],t['R'],t.get('slack'),t.get('reset_all',False))
  digest=hashlib.sha256(text.encode()).hexdigest();ev=exact2.Eval(text,md['data_qubits']);c1=float(ev.fp@ev.n_single)
  if abs(c1)>=1e-12:r=dict(status='INVALID_C1',c1=c1)
  else:r=dict(evaluate(ev),status='SCREENED')
  r.update(CX=md['CX'],R=md['R'],native_depth=md['native_depth'],sha=digest,seconds=time.monotonic()-start)
  return r,text,md,t
 except Exception as e:return dict(status='INVALID',error=repr(e),trace=traceback.format_exc(),seconds=time.monotonic()-start),None,None,t

def run(mode,procs):
 db=sqlite3.connect(D/f'{mode}.sqlite');db.execute('create table if not exists results(id integer primary key, row text, witness blob, qasm blob, md text)')
 best=1.;seen=set();count=0
 with concurrent.futures.ProcessPoolExecutor(max_workers=procs) as pool:
  for r,text,md,t in pool.map(work,tasks(mode),chunksize=1):
   if r.get('sha') in seen:continue
   if r.get('sha'):seen.add(r['sha'])
   count+=1
   db.execute('insert into results values(?,?,?,?,?)',(count,json.dumps(r),zlib.compress(json.dumps(t).encode()),zlib.compress(text.encode()) if text else None,json.dumps(md)))
   if count%20==0:db.commit();print('COUNT',count,flush=True)
   if r.get('exp_minus_A1',0)>=.5002 and r.get('total',1)<best:
    best=r['total'];stem=D/'finalists'/f'a30_{mode}_{count:05}'
    stem.with_suffix('.qasm').write_text(text);stem.with_suffix('.json').write_text(json.dumps(md,indent=2));stem.with_suffix('.screen.json').write_text(json.dumps(r,indent=2));print('BEST',stem.name,json.dumps(r),flush=True)
 db.commit();print('DONE',mode,count,best,flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['post','library','acheck']);p.add_argument('--procs',type=int,default=8);a=p.parse_args();run(a.mode,a.procs)
