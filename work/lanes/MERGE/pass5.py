"""Pass5: immutable circuit/output identity, complete-circuit prices, loss-first selection."""
import os,sys,json,hashlib,copy,time,itertools,collections,shutil,contextlib,io
from pathlib import Path
from multiprocessing import get_context
os.environ.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
sys.dont_write_bytecode=True
H=Path(__file__).resolve().parent;sys.path.insert(0,str(H))
import menu as M,ev37 as E
from campaign import delta,apply_delta
from pass3 import fullmenu as old_fullmenu
import herald5 as H5
ROOT=H.parents[2];TAU=3.611954991494179e-5;FLOOR=.5002
R=H/'res37h';C=H/'v37h';CACHE=H/'cache37h'
for directory in (R,C,CACHE):directory.mkdir(exist_ok=True)
WARM=H/'res37f/basis4_trained.json'
E.configure(WARM,12);E.CDIR=C

def dump(p,x):
 p=Path(p);tmp=p.with_name(p.name+f'.tmp.{os.getpid()}');tmp.write_text(json.dumps(x,indent=2,default=lambda x:x.item())+'\n');tmp.replace(p)
def sha(st):return hashlib.sha256(Path(st).with_suffix('.qasm').read_bytes()).hexdigest()
def feasible(r):return 'loss'in r and r['acceptance']>=FLOOR
def choose(rows,current):return min([current]+[r for r in rows if feasible(r)],key=lambda r:(r['loss'],r['acceptance']*(r['loss']-current['loss'])))
def save(c,why,name=None):
 c,txt=M.normalized(M.fix(c));st=E.write_stem(txt,c['meta']['data_qubits'])
 # Source descriptions belong in receipts, not mutable identity files.
 if name:
  alias=C/name;shutil.copyfile(st.with_suffix('.qasm'),alias.with_suffix('.qasm'));dump(alias.with_suffix('.json'),dict(c['meta'],source=why))
 return st

def record(st,why,tau=TAU):
 st=Path(st);s=sha(st);data=json.loads(st.with_suffix('.json').read_text())['data_qubits'];key=E.key(s,data)
 cp=CACHE/(hashlib.sha256(key.encode()).hexdigest()+'.json')
 if cp.exists():r=json.loads(cp.read_text())
 else:
  r=dict(E.price_stem(st),sha256=s,data_qubits=data,evaluator_hash=E.EVH,cache_key=key,evaluator_basis=str(E.sw.WARM),basis_sha256=hashlib.sha256(E.sw.WARM.read_bytes()).hexdigest());dump(cp,r)
 r=dict(r,stem=str(st.resolve()),what_moved=why,tau=tau)
 if 'loss'in r:r['J_tau']=r['acceptance']*(r['loss']-tau)
 return r

def price(st,why,tau=TAU):
 r=record(st,why,tau)
 with (R/'direct.jsonl').open('a')as f:f.write(json.dumps(r)+'\n')
 print(json.dumps(r),flush=True);return r

def patch(c,d):return apply_delta(c,d)
def apply(c,es):
 c=copy.deepcopy(c)
 patches=[x['delta']for x in es if x['fam']=='patch']
 if patches:
  # Ejections are simultaneous: free every removed cell before restoring any op.
  from campaign import opkey
  merged=dict(remove=[],add=[],tail_remove=[],tail_add=[])
  for field in merged:
   seen=set()
   for d in patches:
    for x in d[field]:
     key=opkey(x)if isinstance(x,dict)else x
     if key not in seen:seen.add(key);merged[field].append(x)
  c=patch(c,merged)
 return M.apply_bundle(c,[e for e in es if e['fam']!='patch'])

def patch_edit(name,a,b):return dict(id=name,fam='patch',delta=copy.deepcopy(delta(a,b)))

BASE=None;EDITS=None;CURRENT_TAU=TAU

def init(stem,menu,tau):
 global BASE,EDITS,CURRENT_TAU
 BASE=M.read(stem);EDITS=json.loads(Path(menu).read_text());CURRENT_TAU=tau

def job(ids):
 try:
  c,txt=apply(BASE,[EDITS[i]for i in ids]);st=E.write_stem(txt,c['meta']['data_qubits'])
  return dict(record(st,dict(edits=ids),CURRENT_TAU),edits=ids)
 except Exception as ex:return dict(edits=ids,invalid=repr(ex))

def batch(stem,menu,tasks,tag,workers,tau=TAU):
 tasks=sorted({tuple(sorted(x))for x in tasks},key=lambda x:(len(x),x));out=R/f'{tag}.jsonl'
 done={tuple(r['edits']):r for r in map(json.loads,out.read_text().splitlines())}if out.exists()else{}
 todo=[x for x in tasks if x not in done];init(stem,menu,tau);start=time.monotonic()
 dump(R/f'{tag}_tasks.json',tasks)
 with out.open('a')as f,get_context('fork').Pool(workers)as pool:
  for k,r in enumerate(pool.imap_unordered(job,todo,chunksize=1),1):
   r['stage']=tag;done[tuple(r['edits'])]=r;f.write(json.dumps(r)+'\n');f.flush()
   if feasible(r) and r['loss']<TAU-3e-8:publish(r)
   if k%25==0 or k==len(todo):print(json.dumps(dict(event='batch',stage=tag,done=k,total=len(todo),seconds=time.monotonic()-start)),flush=True)
 return [done[x]for x in tasks]

PUBLISHED_LOSS=min([TAU-3e-8]+[r['loss'] for p in (H/'cand').glob('merge5_live_*.json') if (r:=json.loads(p.read_text())).get('status')=='finalist'])
def publish(r):
 global PUBLISHED_LOSS
 if r['loss']>=PUBLISHED_LOSS:return
 # Keep a concrete artifact as soon as the exact price qualifies; then verify it.
 st=Path(r['stem']);dest=H/'cand'/f'merge5_live_{r["sha256"][:12]}'
 shutil.copyfile(st.with_suffix('.qasm'),dest.with_suffix('.qasm'));dump(dest.with_suffix('.json'),dict(r,status='exact finalist; judge pending'))
 from judge5 import verify
 j=verify(st);dump(dest.with_suffix('.json'),dict(r,judge_1e6=j,status='finalist' if j['gates_ok'] and j['speed_ok'] else 'judge rejected'))
 if j['gates_ok'] and j['speed_ok']:PUBLISHED_LOSS=r['loss']
 print(json.dumps(dict(event='candidate_published',stem=str(dest),loss=r['loss'],acceptance=r['acceptance'],gates_ok=j['gates_ok'],judge_ratio=j.get('ratio'),speed_ok=j['speed_ok'])),flush=True)

def fullmenu(c):
 es=old_fullmenu(c);hs,audit=H5.menu(c);es.update(hs)
 # GLOBAL's residual reversal is identified by its checked readout, not an absolute tick.
 try:
  m=M.op_of_bit(c,365);previous=[o for o in M.ops_on(c,25)if o['t']<m['t']]
  o=previous[-1]
  if M.unit(o).name=='CX' and tuple(M.cx_qs(o))==(25,24):
   e=M.mk(fam='rev',a=25,b=24,t=o['t']);es[e['id']]=e
 except (StopIteration,IndexError):pass
 # Keep the pass-4 compound covariant when a herald inserts a global initial tick.
 for o in c['ops']:
  if M.unit(o).name!='RESET' or M.unit(o).qs!=(23,):continue
  off=o['t']-29
  for switch in (False,True):
   remove=any(p['t']==29+off and p['lines']==['cx q[28],q[22];']for p in c['ops'])
   e=M.mk(fam='polishguard',switch21=switch,remove28=remove);e['offset']=off;e['id']+=':native'+str(o['t'])
   try:M.apply_bundle(c,[e]);es[e['id']]=e
   except M.Invalid as ex:
    with (R/'native_macro_rejections.jsonl').open('a')as f:f.write(json.dumps(dict(edit=e,invalid=repr(ex)))+'\n')
 _,txt=M.normalized(M.fix(copy.deepcopy(c)));ds,gap=H5.detector_menu(c,txt);es.update(ds)
 return es

if __name__=='__main__':
 if sys.argv[1]=='control':
  r=price(C/'base','v37h reproduction',TAU)
  assert abs(r['loss']-TAU)<1e-13 and abs(r['acceptance']-.5015489333258328)<1e-13,r
  dump(R/'baseline.json',r)
