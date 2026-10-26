"""Pass4: immutable circuit/output identity, complete-circuit prices, loss-first selection."""
import os,sys,json,hashlib,copy,time,itertools,collections,shutil,contextlib,io
from pathlib import Path
from multiprocessing import get_context
os.environ.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
sys.dont_write_bytecode=True
H=Path(__file__).resolve().parent;sys.path.insert(0,str(H))
import menu as M,ev37 as E
from campaign import delta,apply_delta
from pass3 import fullmenu
ROOT=H.parents[2];TAU=3.6305606234064893e-5;FLOOR=.5002
R=H/'res37f';C=H/'v37f';CACHE=H/'cache37f'
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

def patch_edit(name,a,b):return dict(id=name,fam='patch',delta=delta(a,b))

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
 tasks=sorted({tuple(sorted(x))for x in tasks});out=R/f'{tag}.jsonl'
 done={tuple(r['edits']):r for r in map(json.loads,out.read_text().splitlines())}if out.exists()else{}
 todo=[x for x in tasks if x not in done];init(stem,menu,tau);start=time.monotonic()
 dump(R/f'{tag}_tasks.json',tasks)
 with out.open('a')as f,get_context('fork').Pool(workers)as pool:
  for k,r in enumerate(pool.imap_unordered(job,todo,chunksize=1),1):
   r['stage']=tag;done[tuple(r['edits'])]=r;f.write(json.dumps(r)+'\n');f.flush()
   if k%100==0 or k==len(todo):print(json.dumps(dict(event='batch',stage=tag,done=k,total=len(todo),seconds=time.monotonic()-start)),flush=True)
 return [done[x]for x in tasks]

def ports():
 b=M.read(C/'base');es={};audit=[]
 for q,t,drop in [(12,34,None),(25,37,(25,31))]:
  c=copy.deepcopy(b);bit=M.bit(c)
  if drop:c['ops'].remove(M.find(c,t,list(drop),'CX'))
  c['ops'].append(dict(t=t,lines=[f'measure q[{q}] -> c[{bit}];']));c['tail'].append(f'// DETECTOR c[{bit}]')
  e=patch_edit(f'PREPFREE:M{q}@{t}',b,c);es[e['id']]=e
 # A measurement allocates a distinct classical bit for combined proposals.
 for e in es.values():
  if 'M25' in e['id']:
   for o in e['delta']['add']:o['lines']=[l.replace(f'c[{M.bit(b)}]',f'c[{M.bit(b)+1}]')for l in o['lines']]
   e['delta']['tail_add']=[l.replace(f'c[{M.bit(b)}]',f'c[{M.bit(b)+1}]')for l in e['delta']['tail_add']]
 d=json.loads((R/'polish_delta.json').read_text())
 groups=[('P:11_5',[5,11]),('P:2_3',[2,3]),('P:20_21',[20,21])]
 for name,qs in groups:
  dd=dict(remove=[o for o in d['remove']if set(M.unit(o).qs)==set(qs)],add=[o for o in d['add']if set(M.unit(o).qs)==set(qs)],tail_remove=[],tail_add=[])
  try:patch(b,dd);es[name]=dict(id=name,fam='patch',delta=dd)
  except Exception as ex:audit.append(dict(name=name,error=repr(ex)))
 dump(R/'ports_menu.json',es);dump(R/'ports_audit.json',audit)
 tasks=[list(p)for n in range(len(es)+1)for p in itertools.combinations(es,n)]
 dump(R/'ports_tasks.json',tasks)
 # Historical selected edits are invertible patches on the actual current schedule.
 root=M.read(H/'v37d/bc3_7');olds=json.loads((H/'res37d/bc3polish_menu.json').read_text());selected=json.loads((C/'base.json').read_text())['edits'];full,_=M.apply_bundle(root,[olds[i]for i in selected]);assert delta(full,b)['remove']==[]
 atoms={}
 for i in selected:
  minus,_=M.apply_bundle(root,[olds[j]for j in selected if j!=i]);e=patch_edit('eject3:'+i,full,minus);atoms[e['id']]=e
 dump(R/'initial_ejections.json',atoms)
 print(json.dumps(dict(event='ports_built',edits=list(es),invalid=audit,ejections=len(atoms))),flush=True)

if __name__=='__main__':
 if sys.argv[1]=='ports':ports()
 elif sys.argv[1]=='initial':
  price(C/'base','v37f reproduction');rows=batch(C/'base',R/'ports_menu.json',json.loads((R/'ports_tasks.json').read_text()),'ports',int(sys.argv[2]));dump(R/'ports_outcome.json',dict(best=choose(rows,record(C/'base','control')),count=len(rows)))
