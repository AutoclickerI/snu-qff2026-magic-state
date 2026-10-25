from campaign import *
from merge_build import menu
def generate(stem,tag):
 c=M.read(stem);es=menu(c)
 # Include both directions of every identity-pair slot, including data pairs.
 for p in M.pairs(c,M.status(c)):
  for a,b in [(p['a'],p['b']),(p['b'],p['a'])]:
   e=M.mk(fam='pair',g=dict(kind='pair',a=a,b=b,t=p['t']));es[e['id']]=e
 write(H/'res'/f'{tag}_menu.json',es)
 tasks=[];invalid=[];seen={sha(stem)}
 for i,e in es.items():
  try:
   b,txt=M.apply_bundle(c,[e]);s=hashlib.sha256(txt.encode()).hexdigest()
   if s in seen:continue
   seen.add(s);st=H/'c'/s[:24]
   st.with_suffix('.qasm').write_text(txt);write(st.with_suffix('.json'),dict(b['meta'],source=dict(base=str(stem),edits=[i])))
   tasks.append(dict(stem=str(st.relative_to(H)),why=dict(stage=tag,base=str(stem),edits=[i])))
  except Exception as ex:invalid.append(dict(edit=i,error=repr(ex)))
 write(H/'res'/f'{tag}_invalid.json',invalid)
 write(H/'res'/f'{tag}_tasks.json',tasks)
 write(H/'res'/f'{tag}_local.json',tasks[::4]);write(H/'res'/f'{tag}_hippo.json',[r for k,r in enumerate(tasks) if k%4])
 print(json.dumps(dict(stage=tag,menu=len(es),tasks=len(tasks),invalid=len(invalid))),flush=True)
def promote(stem,name,why):
 r=price(stem,why);assert r['loss']<TAU-5e-8 and r['acceptance']>=FLOOR
 sys.path.insert(0,str(ROOT/'work'));import fast_check
 t=time.monotonic();rep=fast_check.check(Path(stem).with_suffix('.qasm').read_text(),E.D,shots=10**6,procs=1)
 verdict=dict(gates_ok=bool(rep.correct_ok),passed=bool(rep.passed),shots=10**6,seed=0,loss=float(rep.score),acceptance=float(rep.acceptance),seconds=time.monotonic()-t)
 write(H/'logs'/f'{name}.judge.json',verdict);assert rep.correct_ok,verdict
 dst=H/'cand'/name;shutil.copyfile(Path(stem).with_suffix('.qasm'),dst.with_suffix('.qasm'))
 write(dst.with_suffix('.json'),dict(r,data_qubits=E.D,judge_1e6=verdict,source=why))
 print(json.dumps(dict(event='FINALIST',path=str(dst),**r,judge=verdict)),flush=True)
if __name__=='__main__':
 if sys.argv[1]=='generate':generate(Path(sys.argv[2]),sys.argv[3])
 elif sys.argv[1]=='promote':promote(Path(sys.argv[2]),sys.argv[3],' '.join(sys.argv[4:]))
