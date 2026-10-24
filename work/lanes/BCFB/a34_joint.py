"""Joint scheduling of encoder, data coupling, and <=5-CX A decoder."""
from a34_prep import *
import pickle
from functools import lru_cache
CP={a:next(i for i,u in enumerate(us) if u.name=='CX' and u.lines[0]==f'cx q[{d}],q[{a}];' and ts[i]>=43) for a,d in zip(A,DATA)}
RELEASE={q:max(ts[i] for i,u in enumerate(us) if i not in OWN and q in u.qs and i<INIT[q]) for q in A}
EXTERIOR={a:[(i,t,u.name) for i,(u,t) in enumerate(zip(us,ts)) if i!=CP[a] and d in u.qs and t<ts[CP[a]]] for a,d in zip(A,DATA)}

@lru_cache(None)
def decoder_plan(ops,end):
 nxt={q:end for q in A};sched=[]
 for ai,bi in reversed(ops):
  a,b=A[ai],A[bi];t=min(nxt[a],nxt[b])-1
  if 16 in (a,b) and t==46:t-=1
  sched.append((t,ai,bi));nxt[a]=nxt[b]=t
 sched.reverse();times=list(ts)
 for a in A:
  at=min(ts[CP[a]],nxt[a]-1);times[CP[a]]=at
  for i,t,name in EXTERIOR[a]:
   if t>=at:
    if name=='TDG':times[i]=at-1
    else:return None
 return sched,times,{a:times[CP[a]] for a in A}

def joint(enc,ops,checks=(),reuse=(),end=47):
 piv=set(enc['pivots']);reuse=set(reuse);checks=set(checks)
 # Decoder must finish before readout. Fixed C17->A16 occupies t46.
 plan=decoder_plan(tuple(ops),end)
 if plan is None:raise ValueError('data release')
 sched,times,nxt=plan;nxt=dict(nxt);new=[];encsched=[]
 for a,b in reversed(enc['ops']):
  t=min(nxt[a],nxt[b])-1;encsched.append((a,b,t));nxt[a]=nxt[b]=t
 release=RELEASE
 for q in A:
  at=nxt[q]-1-int(q in checks)
  if q in reuse:
   if q not in piv:at-=1
   if at<release[q]:raise ValueError('init fit')
  elif at<=release[q]:raise ValueError('init fit')
 for a,b,t in encsched:new.append((cx(a,b),t))
 ntail=list(CLEAN)
 for q in A:
  at=nxt[q]-1
  if q in checks:
   bit=310+q;new.append((U(([f'h q[{q}];'] if q in piv else [])+[f'measure q[{q}] -> c[{bit}];']+([f'h q[{q}];'] if q in piv else [])),at));ntail.append(f'// DETECTOR c[{bit}]');at-=1
  if q in reuse:
   if q not in (2,14):raise ValueError('reuse')
   if q not in piv:new.append((U([f'h q[{q}];']),at));at-=1
   if at<release[q]:raise ValueError('init fit')
  else:
   if at<=release[q]:raise ValueError('init fit')
   if q in (8,16) and q not in piv:
    bit=350+q;new.append((U([f'measure q[{q}] -> c[{bit}];']),at));ntail.append(f'// DETECTOR c[{bit}]')
   else:new.append((U([f'reset q[{q}];']+([f'h q[{q}];'] if q in piv else [])),at))
 old=set(OWN)
 for i,(u,t) in enumerate(zip(us,ts)):
  if u.name in ('MX','MEASURE') and u.qs[0] in A and 14<=int(re.search(r'c\[(\d+)\]',next(l for l in u.lines if l.startswith('measure')))[1])<=20:old.add(i)
  if u.name=='CX' and (t,u.lines[0]) in ((45,'cx q[9],q[15];'),(46,'cx q[8],q[9];')):old.add(i)
 units=[u for i,u in enumerate(us) if i not in old];times=[times[i] for i in range(len(us)) if i not in old]
 ntail=[l for l in ntail if not set(map(int,re.findall(r'c\[(\d+)\]',l)))&set(range(14,21))]
 for u,t in new:units.append(u);times.append(t)
 for t,a,b in sched:units.append(cx(A[a],A[b]));times.append(t)
 zrows=[zf(z,ops) for z in Z0];flags=[i for i in range(7) if not any(z>>i&1 for z in zrows)]
 assert flags
 for i,a in enumerate(A):
  at=max(t for u,t in zip(units,times) if a in u.qs)+1
  if at>end:raise ValueError('late measurement')
  units.append(measure(a,i in flags));times.append(at)
 for z in zrows:
  outz=z
  for t,a,b in reversed(sched):
   if t>46 and outz>>b&1:outz^=1<<a
  bits=[ABITS[A[i]] for i in range(7) if z>>i&1]
  if outz>>A.index(16)&1:bits.append(24)
  ntail.append('// DETECTOR '+' '.join(f'c[{c}]' for c in bits))
 for i in flags:ntail.append(f'// DETECTOR c[{ABITS[A[i]]}]')
 hh=[re.sub(r'creg c\[\d+\]','creg c[400]',l) for l in h]
 return emit(hh,units,times,ntail,dict(kind='joint',enc=enc,checks=sorted(checks),reuse=sorted(reuse),decoder=[[A[a],A[b]] for a,b in ops],flags=[A[i] for i in flags],end=end),False)

def generate(maxg=5,prefix='joint'):
 # Enumerate encoder representatives, then exact decoder schedules. Deduplicate
 # by per-qubit schedule so commuting written orders do not multiply work.
 es=encoders();ds=list(algebra(maxg));counts=collections.Counter();seen=set();stems=[]
 for j,enc in enumerate(es):
  for ops in ds:
   for reuse in ([],[14]):
    counts['attempted']+=1
    try:text,md=joint(enc,ops,reuse=reuse)
    except (ValueError,AssertionError) as e:counts[str(e)]+=1;continue
    sha=hashlib.sha256(text.encode()).hexdigest()
    if sha in seen:continue
    seen.add(sha);stem=D/'candidates'/f'{prefix}_{len(stems):05}';stem.with_suffix('.qasm').write_text(text);stem.with_suffix('.json').write_text(json.dumps(md,indent=2));stems.append(str(stem.relative_to(H)));counts['generated']+=1
  if j%25==0:print('progress',j,dict(counts),flush=True)
 (D/(prefix+'.json')).write_text(json.dumps(dict(counts=counts,stems=stems),indent=2));print('DONE',dict(counts),flush=True)
if __name__=='__main__':generate(int(sys.argv[1]) if len(sys.argv)>1 else 5,sys.argv[2] if len(sys.argv)>2 else 'joint')
