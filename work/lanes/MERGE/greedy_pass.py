from campaign import *
from merge_build import menu
import subprocess
from batch_price import job
SSH=['ssh','-q','-o','ControlMaster=no','-o','ControlPath=none']
def run_tasks(tasks,tag):
 # One local serial evaluator; hippo has three workers and one controller.
 lp=tasks[::4];rp=[r for k,r in enumerate(tasks) if k%4]
 manifest=H/'res'/f'{tag}_remote.json';write(manifest,rp)
 rel=['work/./lanes/MERGE/'+str(p.relative_to(H)) for p in [manifest,H/'batch_price.py',H/'ev37.py',H/'sparse_v37',H/'c']]
 subprocess.run(['rsync','-a','--exclude','.submit_credentials','--exclude','__pycache__','--relative','-e',' '.join(SSH),*rel,'hippo:'+str(ROOT/'work')+'/'],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
 out=H/'res'/f'{tag}_hippo.jsonl';remote_log=H/'logs'/f'{tag}_hippo.log'
 cmd=f'cd {ROOT}; OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 .venv/bin/python {H}/batch_price.py {manifest} 3 {out} > {remote_log} 2>&1'
 proc=subprocess.Popen([*SSH,'hippo',cmd],stdin=subprocess.DEVNULL)
 rows=[]
 with (H/'res'/f'{tag}_local.jsonl').open('a') as f:
  for t in lp:
   r=job(t);rows.append(r);f.write(json.dumps(r)+'\n');f.flush()
 code=proc.wait();assert code==0,('remote exited',code)
 subprocess.run(['rsync','-a','--exclude','.submit_credentials','-e',' '.join(SSH),'hippo:'+str(out),str(out)],check=True)
 rows.extend(json.loads(l) for l in out.read_text().splitlines())
 print(json.dumps(dict(event='batch_complete',tag=tag,count=len(rows),valid=sum('loss'in r for r in rows))),flush=True)
 return rows
def rows_for(tag):
 return [json.loads(l) for host in ['local','hippo'] for l in (H/'res'/f'{tag}_{host}.jsonl').read_text().splitlines()]
def eligible(r,b):
 if 'loss' not in r:return False
 dl=r['loss']-b['loss'];da=r['acceptance']-b['acceptance']
 return dl < -5e-14 or da>1e-6 and dl<=max(3e-8,2e-5*da)
def make_tasks(base,sets,es,tag):
 tasks=[];errors=[];seen=set()
 for ids in sets:
  try:
   c,txt=M.apply_bundle(base,[es[i] for i in ids]);s=hashlib.sha256(txt.encode()).hexdigest()
   if s in seen:continue
   seen.add(s);st=H/'c'/s[:24]
   st.with_suffix('.qasm').write_text(txt);write(st.with_suffix('.json'),dict(c['meta'],source=dict(stage=tag,edits=ids)))
   tasks.append(dict(stem=str(st.relative_to(H)),why=dict(stage=tag,edits=ids)))
  except Exception as ex:errors.append(dict(edits=ids,error=repr(ex)))
 write(H/'res'/f'{tag}_invalid.json',errors)
 return tasks
def choose(rows):return min([r for r in rows if 'loss' in r and r['acceptance']>=FLOOR],key=lambda r:(r['acceptance']*(r['loss']-TAU),r['loss']))
def greedy(scan,stem,tag):
 base=M.read(stem);b=price(stem,tag+' control');es=json.loads((H/'res'/f'{scan}_menu.json').read_text())
 singles=rows_for(scan);good=[r for r in singles if eligible(r,b)]
 ids=sorted({r['what_moved']['edits'][0] for r in good})
 for kind in ['source6','row5']:
  e=M.mk(fam='global',kind=kind);es[e['id']]=e;ids.append(e['id'])
 funded=[r for r in good if r['acceptance']>b['acceptance']+1e-6]
 buyers=[r['what_moved']['edits'][0] for r in funded]
 pilots=[]
 if scan=='cpg_scan':
  for name in ['funded_echo_local','funded_sources_local']:
   if (H/'res'/f'{name}.jsonl').exists():pilots += [json.loads(l) for l in (H/'res'/f'{name}.jsonl').read_text().splitlines()]
 current=choose([b]+singles+pilots);selected=current.get('what_moved',{}).get('edits',[]) if isinstance(current.get('what_moved'),dict) else []
 history=[]
 print(json.dumps(dict(event='greedy_start',tag=tag,relevant=len(ids),buyers=len(buyers),selected=selected,best=current['loss'])),flush=True)
 for rnd in itertools.count(1):
  moves=[{i} for i in ids]
  pair={'echoX:5_h11@10-16','rm:chk_h21_15_20_22_20_31_only22'}
  if pair.issubset(es):moves.append(pair)
  combos=sorted({tuple(sorted(set(selected)|move)) for move in moves if not move.issubset(selected)})
  tasks=make_tasks(base,combos,es,f'{tag}_{rnd}')
  rows=run_tasks(tasks,f'{tag}_{rnd}') if tasks else []
  under=sorted([r for r in rows if 'loss'in r and r['acceptance']<FLOOR and r['loss']<current['loss']],key=lambda r:r['loss'])[:5]
  if under and buyers:
   sets=sorted({tuple(sorted(set(r['what_moved']['edits'])|{i})) for r in under for i in buyers})
   tasks=make_tasks(base,sets,es,f'{tag}_{rnd}_fund')
   if tasks:rows+=run_tasks(tasks,f'{tag}_{rnd}_fund')
  best=choose([current]+rows);gain=current['loss']-best['loss'];before=current
  current=best;selected=current.get('what_moved',{}).get('edits',selected)
  event=dict(round=rnd,selected=selected,before=before['loss'],after=current['loss'],acceptance=current['acceptance'],gain=gain,stem=current['stem'])
  history.append(event);write(H/'res'/f'{tag}_history.json',history);print(json.dumps(dict(event='greedy_round',**event)),flush=True)
  if gain<1e-9:break
 st=H/'builds'/tag
 shutil.copyfile(Path(current['stem']).with_suffix('.qasm'),st.with_suffix('.qasm'))
 write(st.with_suffix('.json'),dict(data_qubits=E.D,source=dict(base=str(stem),scan=scan,edits=selected),all_orders=current))
 write(H/'res'/f'{tag}_outcome.json',dict(stem=str(st),price=current,edits=selected,rounds=history))
 return st
if __name__=='__main__':greedy(sys.argv[1],Path(sys.argv[2]),sys.argv[3])
