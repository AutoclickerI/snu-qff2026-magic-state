import os, sys, json, hashlib, shutil, copy, re, itertools, time
from pathlib import Path
from collections import Counter
os.environ.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
sys.dont_write_bytecode=True
H=Path(__file__).resolve().parent
sys.path.insert(0,str(H))
import menu as M, ev37 as E
ROOT=H.parents[2]
TAU=json.loads((H/"v37f/base.json").read_text())["loss"]
FLOOR=.5002
def write(p,x):
 p=Path(p);t=p.with_name(p.name+'.tmp');t.write_text(json.dumps(x,indent=2)+'\n');t.replace(p)
def sha(st):return hashlib.sha256(Path(st).with_suffix('.qasm').read_bytes()).hexdigest()
def price(st,why='',log='prices',tau=None):
 tau=TAU if tau is None else tau
 st=Path(st).resolve();s=sha(st);data=json.loads(st.with_suffix('.json').read_text())['data_qubits'];cache=H/'res'/(hashlib.sha256(E.key(s,data).encode()).hexdigest()+'.json')
 r=json.loads(cache.read_text()) if cache.exists() else None
 if r is None or r.get('evaluator_hash')!=E.EVH or r.get('data_qubits')!=data:
  r=dict(E.price_stem(st),sha256=s,data_qubits=json.loads(st.with_suffix('.json').read_text())['data_qubits'],evaluator_hash=E.EVH)
  if 'loss' in r:r['J_tau']=r['acceptance']*(r['loss']-tau)
  write(cache,r)
 row=dict(r,stem=str(st),what_moved=why,tau=tau)
 if 'loss' in row:row['J_tau']=row['acceptance']*(row['loss']-tau)
 with (H/'res'/f'{log}.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
 print(json.dumps(row),flush=True)
 return row
def save(c,name,why):
 c,txt=M.normalized(M.fix(c));st=H/'builds'/name
 st.with_suffix('.qasm').write_text(txt);write(st.with_suffix('.json'),dict(c['meta'],source=why))
 return st
def snapshot(src,name):
 st=H/'builds'/name
 for x in ['.qasm','.json']:shutil.copyfile(Path(src).with_suffix(x),st.with_suffix(x))
 return st
def opkey(o):return o['t'],tuple(re.sub(r'\s+','',l) for l in o['lines'])
def delta(a,b):
 aa={opkey(o):o for o in a['ops']};bb={opkey(o):o for o in b['ops']}
 rm=[aa[k] for k in aa.keys()-bb.keys()];add=[bb[k] for k in bb.keys()-aa.keys()]
 cells=sorted({(q,o['t']) for o in rm+add for q in M.unit(o).qs})
 tr=list((Counter(a['tail'])-Counter(b['tail'])).elements());ta=list((Counter(b['tail'])-Counter(a['tail'])).elements())
 bits=sorted({int(x) for o in rm+add for l in o['lines'] for x in M.BITRE.findall(l)}|{int(x) for l in tr+ta for x in M.BITRE.findall(l)})
 return dict(remove=rm,add=add,cells=cells,bits=bits,tail_remove=tr,tail_add=ta)
def apply_delta(base,d):
 c=copy.deepcopy(base)
 for o in d['remove']:
  matches=[x for x in c['ops'] if opkey(x)==opkey(o)]
  if len(matches)!=1:raise ValueError(('missing removal',o))
  c['ops'].remove(matches[0])
 for o in d['add']:
  if opkey(o) not in [opkey(x) for x in c['ops']]:c['ops'].append(copy.deepcopy(o))
 for l in d['tail_remove']:c['tail'].remove(l)
 for l in d['tail_add']:
  if l not in c['tail']:c['tail'].append(l)
 occ={}
 for o in c['ops']:
  for q in M.unit(o).qs:
   k=q,o['t']
   if k in occ:raise ValueError(('collision',k,occ[k],o))
   occ[k]=o
 return c
def initial():
 paths={'A':ROOT/'work/lanes/MAIN/v37a','P':ROOT/'work/lanes/MAIN/v37b','G':ROOT/'work/lanes/GLOBAL/builds/bc2fix_007__S_pair_31_32_31','C':ROOT/'work/lanes/COMPLETE/builds/v37_neighbor_k27_m14'}
 plans={}
 for n,p in paths.items():
  s=snapshot(p,n);price(s,'source '+n);plans[n]=M.read(s)
 ds={n:delta(plans['A'],plans[n]) for n in ['P','G','C']}
 overlaps={}
 for x,y in itertools.combinations(ds,2):
  overlaps[x+y]=dict(cells=sorted(set(map(tuple,ds[x]['cells']))&set(map(tuple,ds[y]['cells']))),bits=sorted(set(ds[x]['bits'])&set(ds[y]['bits'])),tail_lines=sorted(set(ds[x]['tail_remove']+ds[x]['tail_add'])&set(ds[y]['tail_remove']+ds[y]['tail_add'])))
 write(H/'res/diffs_initial.json',dict(diffs=ds,overlaps=overlaps))
 print(json.dumps(dict(event='overlaps',sizes={n:{k:len(v) for k,v in d.items()} for n,d in ds.items()},overlaps=overlaps)),flush=True)
 for ns in ['PG','PC','GC','PGC']:
  c=copy.deepcopy(plans['A'])
  try:
   for n in ns:c=apply_delta(c,ds[n])
   price(save(c,ns,'direct merge '+ns),'direct merge '+ns)
  except Exception as ex:
   print(json.dumps(dict(event='merge_conflict',merge=ns,error=repr(ex))),flush=True)
if __name__=='__main__':
 if sys.argv[1]=='initial':initial()
 elif sys.argv[1]=='price':price(sys.argv[2],' '.join(sys.argv[3:]))
