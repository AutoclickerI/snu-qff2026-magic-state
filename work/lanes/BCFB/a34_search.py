"""A-only destructive CSS decoder enumeration on frozen v34m.
CNOTs operate after each touched A qubit's D coupling. Z checks are conjugated
exactly; C17->A16 is retained and its measured Z correction is propagated.
"""
import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
import json,re,itertools,hashlib,collections
H=Path(__file__).resolve().parent;ROOT=H.parents[2];D=H/'a34'
sys.path[:0]=[str(H),str(ROOT/'work/lanes/EVAL')]
import schedule as S
from util import native_times
A=[1,14,8,9,2,16,15];DATA=[0,20,7,10,3,22,21];ABITS=dict(zip(A,range(14,21)))
ROWS=[[0,2,4,6],[1,2,5,6],[3,4,5,6]]
EDGES=[(a,b) for a in range(7) for b in range(7) if abs(A[a]//6-A[b]//6)+abs(A[a]%6-A[b]%6)==1]
Z0=tuple(sum(1<<i for i in row) for row in ROWS)

def U(lines):return S.Unit(lines,[])
def cx(a,b):return U([f'cx q[{a}],q[{b}];'])
def measure(q,x):return U(([f'h q[{q}];'] if x else [])+[f'measure q[{q}] -> c[{ABITS[q]}];']+([f'h q[{q}];'] if x else []))
def zf(v,ops):
 for a,b in ops:
  if v>>b&1:v^=1<<a
 return v

def read(stem):
 text=Path(str(stem)+'.qasm').read_text();md=json.loads(Path(str(stem)+'.json').read_text());h,raw,tail=S.qasm_ops(text);us=S.fold_units(raw);ts=native_times(text,us)
 return text,md,h,us,ts,tail

def emit(h,us,ts,tail,options,check_native=True):
 ids=sorted(range(len(us)),key=lambda i:(ts[i],i));us=[us[i] for i in ids];ts=[ts[i] for i in ids]
 assert S.feasible(ts,us,*S.build_dag(us)),'overlapping schedule'
 text=S.emit(h,us,ts,tail)
 if check_native:
  _,raw,_=S.qasm_ops(text);fold=S.fold_units(raw)
  assert [u.lines for u in us]==[u.lines for u in fold],'fold mismatch'
  assert ts==native_times(text,fold),'native time mismatch'
 return text,dict(data_qubits=DATA,CX=sum(u.name=='CX' for u in us),R=45,native_depth=max(ts)+1,base='MAIN/v34m',options=options)

BASE=read(D/'inputs/v34m')

def decoder(ops,flags=None,end=47,timing='latest',moves=True,source=BASE):
 text,md,h,us,ts,tail=source
 old=set()
 for i,(u,t) in enumerate(zip(us,ts)):
  if u.name in ('MX','MEASURE') and u.qs[0] in A and 14<=int(re.search(r'c\[(\d+)\]',next(l for l in u.lines if l.startswith('measure')))[1])<=20:old.add(i)
  if u.name=='CX' and (t,u.lines[0]) in ((45,'cx q[9],q[15];'),(46,'cx q[8],q[9];')):old.add(i)
 tail=[l for l in tail if not set(map(int,re.findall(r'c\[(\d+)\]',l)))&set(range(14,21))]
 cp={a:next(i for i,u in enumerate(us) if u.name=='CX' and u.lines[0]==f'cx q[{d}],q[{a}];' and ts[i]>=43) for a,d in zip(A,DATA)}
 early={a:max(t for i,(u,t) in enumerate(zip(us,ts)) if i not in old and i!=cp[a] and a in u.qs and t<ts[cp[a]])+1 for a in A}
 # Backward latest fit, retaining fixed external C17->16 at t46.
 nxt={a:end for a in A};sched=[]
 for ai,bi in reversed(ops):
  a,b=A[ai],A[bi];t=min(nxt[a],nxt[b])-1
  if 16 in (a,b) and t==46:t-=1
  sched.append((t,ai,bi));nxt[a]=nxt[b]=t
 sched.reverse();newts=list(ts)
 for a,d in zip(A,DATA):
  first=nxt[a];t=min(ts[cp[a]],first-1)
  if not moves and t!=ts[cp[a]]:raise ValueError('coupling move needed')
  if t<early[a]:raise ValueError('before A encoding')
  # Preserve all exterior operations. q10 TDG can move when advancing its coupling.
  exterior=[(i,at) for i,(u,at) in enumerate(zip(us,ts)) if d in u.qs and i!=cp[a] and at<ts[cp[a]]]
  for i,at in exterior:
   if at>=t:
    if d==10 and us[i].name=='TDG':newts[i]=t-1
    else:raise ValueError('before data release')
  newts[cp[a]]=t
 zrows=[zf(z,ops) for z in Z0];zero=[i for i in range(7) if not any(z>>i&1 for z in zrows)]
 if flags is None:flags=zero
 if not flags or not set(flags)<=set(zero):raise ValueError('no X readout')
 units=[u for i,u in enumerate(us) if i not in old];times=[newts[i] for i in range(len(us)) if i not in old]
 for t,a,b in sched:units.append(cx(A[a],A[b]));times.append(t)
 for i,a in enumerate(A):
  last=max(t for u,t in zip(units,times) if a in u.qs)
  mt=last+1 if timing=='latest' else end
  if mt>end:raise ValueError('late readout')
  units.append(measure(a,i in flags));times.append(mt)
 # Correction from the retained C17 classical Z readout, inserted at t46.
 for z in zrows:
  outz=z
  for t,a,b in reversed(sched):
   if t>46 and outz>>b&1:outz^=1<<a
  bits=[ABITS[A[i]] for i in range(7) if z>>i&1]
  if outz>>A.index(16)&1:bits.append(24)
  tail.append('// DETECTOR '+' '.join(f'c[{c}]' for c in bits))
 for i in flags:tail.append(f'// DETECTOR c[{ABITS[A[i]]}]')
 xp=[]
 for i in flags:
  x=1<<i
  for a,b in reversed(ops):
   if x>>a&1:x^=1<<b
  xp.append([A[j] for j in range(7) if x>>j&1])
 return emit(h,units,times,tail,dict(kind='decoder',ops=[[A[a],A[b]] for a,b in ops],schedule=[[t,A[a],A[b]] for t,a,b in sched],flags=[A[i] for i in flags],flag_X_supports=xp,couplings={a:newts[cp[a]] for a in A},end=end,timing=timing),False)

def algebra(maxg):
 # Only disjoint gates are order-equivalent under the noisy schedule. Gates
 # sharing a control or target commute ideally but can propagate noise differently.
 counts=collections.Counter()
 def rec(seq,zs):
  if seq and not (zs[0]|zs[1]|zs[2])==127:
   counts[len(seq)]+=1;yield tuple(seq)
  if len(seq)==maxg:return
  for e,(a,b) in enumerate(EDGES):
   if seq:
    pa,pb=seq[-1]
    if (a,b)==(pa,pb):continue
    if len({a,b,pa,pb})==4 and (a,b)<(pa,pb):continue
   yield from rec(seq+[(a,b)],tuple(z^(1<<a) if z>>b&1 else z for z in zs))
 yield from rec([],Z0)
 print('algebra_counts',dict(counts),flush=True)

def generate(maxg=5,end=47):
 seen=set();counts=collections.Counter();out=[]
 for ops in algebra(maxg):
  counts['algebra']+=1
  try:text,md=decoder(ops,end=end)
  except (ValueError,AssertionError) as e:counts[str(e)]+=1;continue
  sha=hashlib.sha256(text.encode()).hexdigest()
  if sha in seen:continue
  seen.add(sha);counts['generated']+=1
  stem=D/'candidates'/f'dec{end}_{len(out):05}'
  stem.with_suffix('.qasm').write_text(text);stem.with_suffix('.json').write_text(json.dumps(md,indent=2));out.append(str(stem.relative_to(H)))
 (D/f'decoders_{end}.json').write_text(json.dumps(dict(counts=counts,stems=out),indent=2));print(json.dumps(dict(counts=counts,stems=len(out))),flush=True)
if __name__=='__main__':generate(int(sys.argv[1]) if len(sys.argv)>1 else 5,int(sys.argv[2]) if len(sys.argv)>2 else 47)
