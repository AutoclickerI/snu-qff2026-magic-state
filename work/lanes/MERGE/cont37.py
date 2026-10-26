"""v37c continuation: saved exact prices, native edit jobs and explicit receipts."""
import os,sys,json,hashlib,copy,time,itertools,collections,shutil,contextlib,io
from pathlib import Path
from multiprocessing import get_context
os.environ.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
sys.dont_write_bytecode=True
H=Path(__file__).resolve().parent;sys.path.insert(0,str(H))
import menu as M,ev37 as E
TAU=3.6904034715818095e-5;FLOOR=.5002;ROOT=H.parents[2]
R=H/'res37c';C=H/'v37c';CACHE=H/'cache37c'
def dump(p,x):
 p=Path(p);tmp=p.with_name(p.name+f'.tmp.{os.getpid()}');tmp.write_text(json.dumps(x,indent=2,default=lambda x:x.item())+'\n');tmp.replace(p)
def sha(st):return hashlib.sha256(Path(st).with_suffix('.qasm').read_bytes()).hexdigest()
def rank(r):return r['acceptance']*(r['loss']-TAU)
def feasible(r):return 'loss'in r and r['acceptance']>=FLOOR
def save(c,name,why):
 c,txt=M.normalized(M.fix(c));s=C/name
 s.with_suffix('.qasm').write_text(txt);dump(s.with_suffix('.json'),dict(c['meta'],source=why));return s
def record(st,why):
 st=Path(st);s=sha(st);data=json.loads(st.with_suffix('.json').read_text())['data_qubits']
 key=E.key(s,data);cp=CACHE/(hashlib.sha256(key.encode()).hexdigest()+'.json')
 if cp.exists():r=json.loads(cp.read_text())
 else:
  r=dict(E.price_stem(st),sha256=s,data_qubits=data,evaluator_hash=E.EVH,cache_key=key)
  dump(cp,r)
 r=dict(r,stem=str(st.resolve()),what_moved=why,tau=TAU)
 if 'loss'in r:r['J_tau']=rank(r)
 return r
def price(st,why):
 r=record(st,why)
 with (R/'direct.jsonl').open('a') as f:f.write(json.dumps(r)+'\n')
 print(json.dumps(r),flush=True);return r
def fullmenu(c):
 st=M.status(c);es=M.removals(c)+M.trades(c)+M.shifts(c)+M.cx_adds(c,st)+M.gadget_adds(c,st)
 es={e['id']:e for e in es}
 for p in M.pairs(c,st):
  for a,b in [(p['a'],p['b']),(p['b'],p['a'])]:
   e=M.mk(fam='pair',g=dict(kind='pair',a=a,b=b,t=p['t']));es[e['id']]=e
 try:
  o=M.op_of_bit(c,321)
  if o['t']==37 and M.free_at(c,9,38) and M.free_at(c,10,37):
   e=M.mk(fam='ajoint');es[e['id']]=e
 except StopIteration:pass
 if (R/'polish_transport.json').exists():
  for switch in [False,True]:
   remove28=any(o['t']==29 and o['lines']==['cx q[28],q[22];'] for o in c['ops'])
   e=M.mk(fam='polishguard',switch21=switch,remove28=remove28)
   try:M.apply_bundle(c,[e]);es[e['id']]=e
   except M.Invalid:pass
 return es
BASE=None;EDITS=None
def init(stem,menu):
 global BASE,EDITS
 BASE=M.read(stem);EDITS=json.loads(Path(menu).read_text())
def work(ids):
 try:
  c,txt=M.apply_bundle(BASE,[EDITS[i] for i in ids]);s=hashlib.sha256(txt.encode()).hexdigest();st=C/s[:24]
  if not st.with_suffix('.qasm').exists():
   st.with_suffix('.qasm').write_text(txt);dump(st.with_suffix('.json'),dict(c['meta'],source=dict(edits=ids)))
  return dict(record(st,dict(edits=ids)),edits=ids)
 except Exception as ex:return dict(edits=ids,invalid=repr(ex))
def batch(stem,menuf,tasksf,tag,workers):
 tasks=json.loads(Path(tasksf).read_text());out=R/f'{tag}.jsonl'
 done={tuple(r['edits']):r for r in (json.loads(l) for l in out.read_text().splitlines())} if out.exists() else {}
 tasks=[list(t) for t in dict.fromkeys(tuple(sorted(t)) for t in tasks) if tuple(sorted(t)) not in done]
 init(stem,menuf);start=time.monotonic()
 with out.open('a') as f,get_context('fork').Pool(workers) as pool:
  for k,r in enumerate(pool.imap_unordered(work,tasks,chunksize=1),1):
   r['stage']=tag;r['evaluator_hash']=E.EVH;f.write(json.dumps(r)+'\n');f.flush()
   if k%100==0 or k==len(tasks):print(json.dumps(dict(stage=tag,completed=k,total=len(tasks),seconds=time.monotonic()-start)),flush=True)
 return out
def prep(stem,tag):
 c=M.read(stem);es=fullmenu(c);dump(R/f'{tag}_menu.json',es);dump(R/f'{tag}_tasks.json',[[i] for i in es])
 print(json.dumps(dict(event='menu',tag=tag,count=len(es),families=dict(collections.Counter(e['fam'] for e in es.values())))),flush=True)
def ajoint():
 b=M.read(C/'base');audit=[];tasks=[]
 # AJOINT's full two-guard recipe needs two free slots before M9.
 # v37c has removed both guards and A9 prep advanced to39; test the legal one-guard transport and matched controls.
 for mt in [37,38]:
  for gt in [None,37,38]:
   if gt==mt:continue
   c=copy.deepcopy(b);o=M.op_of_bit(c,321);o['t']=mt
   if gt is not None:c['ops'].append(dict(t=gt,lines=['cx q[9],q[10];']))
   name=f'ajoint_m{mt}_g{gt}';why=dict(kind='AJOINT R45 transport',measure321=mt,cx9_10=gt,A9prep=39)
   try:s=save(c,name,why);price(s,why);tasks.append(str(s))
   except Exception as ex:audit.append(dict(name=name,error=repr(ex)))
 dump(R/'ajoint_ports.json',dict(candidates=tasks,invalid=audit))
if __name__=='__main__':
 cmd=sys.argv[1]
 if cmd=='price':price(Path(sys.argv[2]),' '.join(sys.argv[3:]))
 elif cmd=='menu':prep(Path(sys.argv[2]),sys.argv[3])
 elif cmd=='ajoint':ajoint()
 elif cmd=='batch':batch(Path(sys.argv[2]),Path(sys.argv[3]),Path(sys.argv[4]),sys.argv[5],int(sys.argv[6]))
