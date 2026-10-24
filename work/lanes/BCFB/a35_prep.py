"""v35b A preparation instruments. No c1 or minimum-fault-loss pruning."""
import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
import json,re,hashlib,itertools,collections,ast
H=Path(__file__).resolve().parent;D=H/'a35';ROOT=H.parents[2]
sys.path[:0]=[str(H),str(ROOT/'work/lanes/EVAL')]
from a34_search import A,DATA,U,cx,read,S,native_times
from a34_dedup import physical_key
text,md,h,us,ts,tail=BASE=read(D/'inputs/v35b')
RELEASE={1:37,14:37,8:35,9:37,2:37,16:36,15:39};OLDPLUS={2,14}
OWN={i for i,(u,t) in enumerate(zip(us,ts)) if (u.name=='CX' and 38<=t<=43 and set(u.qs)<=set(A)) or (u.qs==(8,) and t in (36,37)) or (u.qs==(14,) and t==38) or (u.qs==(1,) and t in (38,40)) or (u.qs==(2,) and t in (38,39)) or (u.qs==(16,) and t==40)}
assert sum(us[i].name=='CX' for i in OWN)==11
oldbits={int(re.search(r'c\[(\d+)\]',next(l for l in us[i].lines if l.startswith('measure')))[1]) for i in OWN if us[i].name in ('MX','MEASURE')}
CLEAN=[l for l in tail if not set(map(int,re.findall(r'c\[(\d+)\]',l)))&oldbits]
assert oldbits=={272,60,180,55},oldbits
p=ROOT/'work/lanes/EXENC/exenc.py';node=next(n for n in ast.parse(p.read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='score');ns={};exec(compile(ast.Module(body=[node],type_ignores=[]),str(p),'exec'),ns);proxy=ns['score']
def finish(units,times,detectors,options):
 ids=sorted(range(len(units)),key=lambda i:(times[i],i));units=[units[i] for i in ids];times=[times[i] for i in ids]
 assert S.feasible(times,units,*S.build_dag(units)),'schedule overlap'
 header=[re.sub(r'creg c\[\d+\]','creg c[800]',l) for l in h];s=S.emit(header,units,times,detectors)
 return s,dict(data_qubits=DATA,CX=sum(u.name=='CX' for u in units),R=44+options.get('delay',0),native_depth=max(times)+1,base='MAIN/v35b',options=options)
def make(enc,checks=(),reuse_plus=(14,),basis_change='reset',delay=0,early16=False):
 piv=set(enc['pivots']);checks=set(checks);reuse_plus=set(reuse_plus)
 keep=[i for i in range(len(us)) if i not in OWN];units=[us[i] for i in keep];times=[ts[i]+(delay if ts[i]>=43 else 0) for i in keep];detectors=list(CLEAN)
 nxt={q:(43 if q in (9,15) else 44)+delay for q in A};new=[]
 ops=enc['ops'];flat=[ab for layer in ops for ab in layer] if ops and isinstance(ops[0][0],list) else ops
 for a,b in reversed(flat):
  at=min(nxt[a],nxt[b])-1;new.append((cx(a,b),at));nxt[a]=nxt[b]=at
 for q in A:
  at=nxt[q]-1;plus=q in piv;matches=plus==(q in OLDPLUS)
  check=q in checks
  if check:
   if matches and at==RELEASE[q] and q!=16:
    # The preserved old measured state and its standalone detector serve this check.
    pass
   else:
    if at<=RELEASE[q]:raise ValueError('check before release')
    bit=600+q;ls=([f'h q[{q}];'] if plus else [])+[f'measure q[{q}] -> c[{bit}];']+([f'h q[{q}];'] if plus else [])
    new.append((U(ls),at));detectors.append(f'// DETECTOR c[{bit}]');at-=1
  reuse=matches and (not plus or q in reuse_plus)
  if reuse:
   if at<RELEASE[q]:raise ValueError('reuse before release')
  else:
   if at<=RELEASE[q]:raise ValueError('initialization before release')
   if basis_change=='H' and not matches:ls=[f'h q[{q}];']
   else:ls=[f'reset q[{q}];']+([f'h q[{q}];'] if plus else [])
   new.append((U(ls),at))
 if early16:
  if any(16 in u.qs and at==37 for u,at in new):raise ValueError('early16 overlap')
  new.append((U(['measure q[16] -> c[650];']),37));detectors.append('// DETECTOR c[650]')
 for u,at in new:units.append(u);times.append(at)
 return finish(units,times,detectors,dict(kind='flag_conditioned_A',enc=enc,checks=sorted(checks),reuse_plus=sorted(reuse_plus),basis_change=basis_change,delay=delay,early16=early16))

def encoders():
 out=[]
 for p in (D/'exenc').glob('native_paths_*.jsonl'):
  for j,l in enumerate(p.open()):e=json.loads(l)['circuit'];out.append(dict(name=f'exenc_{p.stem}_{j}',pivots=e['pivots'],ops=e['ops']))
 for p in (ROOT/'work/lanes/ACHECK').glob('enc_[0-9][0-9][0-9].json'):
  o=json.loads(p.read_text())
  if 'encoder' in o:out.append(dict(name=p.stem,pivots=o['encoder']['pivots'],ops=o['encoder']['ops']))
 for j,e in enumerate(json.loads((H/'a30/inputs/acheck_encoders.json').read_text())):
  out.append(dict(name=f'acheck_cache_{j}',pivots=e['pivots'],ops=e['ops']))
 for name in ['zreuse_00006','earlyflags_00003','encoders_00014','encoders_00013']:
  m=json.loads((H/'a34/candidates'/name).with_suffix('.json').read_text());o=m['options'];e=o.get('enc') or o.get('parent_options',{}).get('enc')
  if not e and 'source' in o:e=json.loads((H/'a34/candidates'/o['source']).with_suffix('.json').read_text())['options']['enc']
  out.append(dict(e,name='a34_'+name))
 seen=set();unique=[]
 for e in out:
  flat=[ab for layer in e['ops'] for ab in layer] if isinstance(e['ops'][0][0],list) else e['ops'];key=json.dumps([sorted(e['pivots']),flat])
  if key not in seen:seen.add(key);unique.append(e)
 return unique

def asap_layers(ops):
 if isinstance(ops[0][0],list):return ops
 ready={q:0 for q in A};layers=[]
 for a,b in ops:
  t=max(ready[a],ready[b]);ready[a]=ready[b]=t+1
  while len(layers)<=t:layers.append([])
  layers[t].append([a,b])
 return layers

def generate():
 encs=encoders();stems=[];seen=set();count=collections.Counter();rank=[]
 for enc in encs:
  layers=asap_layers(enc['ops']);v=proxy(layers,enc['pivots'],A,A);rank.append(dict(name=enc['name'],blind=v[3]+v[4]+v[7],detected=sum(v)-v[3]-v[4]-v[7],vector=v,CX=sum(map(len,layers)),depth=len(layers)))
  for checks in [[],[1,2,8,16],A,enc['pivots'],[1,2,9,16]]:
   for reuse in [[],[14],[2,14]]:
    for basis in ['reset','H']:
     count['attempted']+=1
     try:s,m=make(enc,checks,reuse,basis)
     except (ValueError,AssertionError) as ex:count[str(ex)]+=1;continue
     stem=D/'candidates'/f'enc_{len(stems):05}';stem.with_suffix('.qasm').write_text(s);stem.with_suffix('.json').write_text(json.dumps(m,indent=2))
     try:key=physical_key(stem)
     except Exception:raise
     if key in seen:stem.with_suffix('.qasm').unlink();stem.with_suffix('.json').unlink();continue
     seen.add(key);stems.append(str(stem.relative_to(H)));count['generated']+=1
 # Explicitly price the delayed a34 port, preserving the entire terminal instrument.
 for e in [e for e in encs if e['name'].startswith('a34_')]:
  for delay in [1]:
   count['attempted']+=1
   try:s,m=make(e,A,[14],'reset',delay)
   except (ValueError,AssertionError) as ex:count[str(ex)]+=1;continue
   stem=D/'candidates'/f'enc_{len(stems):05}';stem.with_suffix('.qasm').write_text(s);stem.with_suffix('.json').write_text(json.dumps(m,indent=2));key=physical_key(stem)
   if key in seen:stem.with_suffix('.qasm').unlink();stem.with_suffix('.json').unlink();continue
   seen.add(key);stems.append(str(stem.relative_to(H)));count['generated']+=1
 (D/'encoder_ranking.json').write_text(json.dumps(rank,indent=2));(D/'encoders.json').write_text(json.dumps(dict(counts=count,stems=stems),indent=2));print('DONE',len(encs),dict(count),flush=True)
if __name__=='__main__':generate()
