"""Transplant prior A encoder witnesses with actual v34m release/deadline times."""
from a34_search import *
import stim,random
text,md,h,us,ts,tail=BASE
want={1:(38,'RX'),14:(39,'RESET'),8:(38,'MEASURE'),9:(38,'RX'),2:(37,'RX'),16:(41,'MEASURE'),15:(39,'RX')}
INIT={q:next(i for i,(u,t) in enumerate(zip(us,ts)) if u.qs==(q,) and (t,u.name)==v) for q,v in want.items()}
OWN={i for i,u in enumerate(us) if ts[i]<45 and set(u.qs)<=set(A) and all(i>=INIT[q] for q in u.qs)}
assert sum(us[i].name=='CX' for i in OWN)==11
oldbits={int(re.search(r'c\[(\d+)\]',next(l for l in us[i].lines if l.startswith('measure')))[1]) for i in OWN if us[i].name in ('MX','MEASURE')}
CLEAN=[l for l in tail if not set(map(int,re.findall(r'c\[(\d+)\]',l)))&oldbits]

def enc_check(enc):
 sim=stim.TableauSimulator();sim.reset(*A);sim.h(*enc['pivots'])
 for a,b in enc['ops']:sim.cx(a,b)
 for basis,rows in [('X',ROWS+[list(range(7))]),('Z',ROWS)]:
  for row in rows:
   p=stim.PauliString(36)
   for i in row:p[A[i]]=basis
   assert sim.peek_observable_expectation(p)==1,'invalid encoder'

def prep(enc,checks=(1,2,9),reuse=(),early=0,slack=None):
 enc_check(enc);piv=set(enc['pivots']);reuse=set(reuse);checks=set(checks);slack=slack or {}
 keep=[i for i in range(len(us)) if i not in OWN];units=[us[i] for i in keep];times=[ts[i] for i in keep];ntail=list(CLEAN)
 # Per-qubit deadline is its first outgoing D coupling, not a single nominal R.
 nxt={q:min(t for u,t in zip(units,times) if q in u.qs and t>=44)-early for q in A}
 release={q:max(ts[i] for i in keep if q in us[i].qs and i<INIT[q]) for q in A}
 fresh=[]
 for k,(a,b) in reversed(list(enumerate(enc['ops']))):
  at=min(nxt[a],nxt[b])-1-slack.get(k,0);fresh.append((cx(a,b),at));nxt[a]=nxt[b]=at
 for q in A:
  at=nxt[q]-1
  if q in checks:
   bit=310+q;l=([f'h q[{q}];'] if q in piv else [])+[f'measure q[{q}] -> c[{bit}];']+([f'h q[{q}];'] if q in piv else [])
   fresh.append((U(l),at));ntail.append(f'// DETECTOR c[{bit}]');at-=1
  if q in reuse:
   if q not in (2,14):raise ValueError('reuse limited to prior speed-safe measured plus states')
   if q not in piv:fresh.append((U([f'h q[{q}];']),at));at-=1
   if at<release[q]:raise ValueError('reuse does not fit')
  else:
   if at<=release[q]:raise ValueError('init does not fit')
   if q in (8,16) and q not in piv:
    bit=350+q;fresh.append((U([f'measure q[{q}] -> c[{bit}];']),at));ntail.append(f'// DETECTOR c[{bit}]')
   else:fresh.append((U([f'reset q[{q}];']+([f'h q[{q}];'] if q in piv else [])),at))
 for u,t in fresh:units.append(u);times.append(t)
 hh=[re.sub(r'creg c\[\d+\]','creg c[400]',l) for l in h]
 return emit(hh,units,times,ntail,dict(kind='prep',enc=enc,checks=sorted(checks),reuse=sorted(reuse),early=early,slack=slack),False)

def encoders():
 from a30_search import library
 out=library()
 for k,e in enumerate(json.loads((H/'a30/inputs/acheck_encoders.json').read_text())):
  out.append(dict(name=f'acheck_{k}',pivots=e['pivots'],ops=[ab for layer in e['ops'] for ab in layer]))
 for p in (H/'a30/finalists').glob('*.json'):
  if any(x in p.name for x in ('.exact.','.screen.','.speed.','.verification.','.allorders.','.judge.','.moments.')):continue
  try:
   m=json.loads(p.read_text());e=m['options']['spec']['enc'];out.append(e)
  except (KeyError,TypeError):pass
 seen=set();unique=[]
 for e in out:
  key=json.dumps([sorted(e['pivots']),e['ops']])
  if key not in seen:seen.add(key);unique.append(e)
 return unique

def generate(mode='encoders'):
 seen=set();counts=collections.Counter();out=[];tasks=[]
 if mode=='encoders':
  for enc in encoders():
   for reuse in ([],[14]):
    for checks in ([1,2,9],[],enc['pivots']):tasks.append((enc,checks,reuse,0,{}))
 elif mode=='prior':
  for name in ('a30_fastpick_feedback_neighbors_05085','a30_fastpick_feedback_neighbors_05061','a30_fbn_00549','a30_fb_s810_00837'):
   p=H/'a30/finalists'/name;m=json.loads(p.with_suffix('.json').read_text());s=m['options'].get('spec',m['options']);e=s.get('enc',s.get('encoder'))
   for reuse in ([],[14]):
    for checks in (s['checks'],[1,2,9],[],e['pivots']):
     for early in (0,1):tasks.append((e,checks,reuse,early,{}))
 else:raise ValueError(mode)
 for enc,checks,reuse,early,slack in tasks:
  counts['attempted']+=1
  try:text,md=prep(enc,checks,reuse,early,slack)
  except (ValueError,AssertionError) as ex:counts[str(ex)]+=1;continue
  sha=hashlib.sha256(text.encode()).hexdigest()
  if sha in seen:continue
  seen.add(sha);counts['generated']+=1
  stem=D/'candidates'/f'{mode}_{len(out):05}';stem.with_suffix('.qasm').write_text(text);stem.with_suffix('.json').write_text(json.dumps(md,indent=2));out.append(str(stem.relative_to(H)))
 (D/f'{mode}.json').write_text(json.dumps(dict(counts=counts,stems=out),indent=2));print(json.dumps(dict(counts=counts,stems=len(out))),flush=True)
if __name__=='__main__':generate(sys.argv[1] if len(sys.argv)>1 else 'encoders')
