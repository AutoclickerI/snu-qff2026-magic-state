from pass4 import *
import signature4 as S

def relevant(r,b):
 if 'loss'not in r:return False
 dl=r['loss']-b['loss'];da=r['acceptance']-b['acceptance']
 return dl<2e-7 or (da>1e-6 and dl<=max(3e-8,2e-5*da))

def buyer(r,b):
 if 'loss'not in r:return False
 dl=r['loss']-b['loss'];da=r['acceptance']-b['acceptance']
 return da>1e-6 and dl<=max(3e-8,2e-5*da)

def initial():
 b=record(C/'base','initial');rs=[json.loads(x)for x in (R/'ports.jsonl').read_text().splitlines()]
 from judge4 import verify
 for r in sorted([b]+[r for r in rs if feasible(r)],key=lambda x:x['loss']):
  v=verify(r['stem'])
  if v['gates_ok']and v['speed_ok']:
   atoms=json.loads((R/'initial_ejections.json').read_text());es=json.loads((R/'ports_menu.json').read_text());base=M.read(C/'base')
   for i in r.get('edits',[]):
    c,_=apply(base,[es[i]]);e=patch_edit('eject4:'+i,c,base);atoms[e['id']]=e
   dump(R/'start.json',dict(price=r,atoms=atoms,judge=v));return
 raise RuntimeError('incumbent failed baseline judge')

def fresh(stem,atoms,tag):
 c=M.read(stem);es=fullmenu(c);valid={};invalid={}
 for i,e in atoms.items():
  es[i]=e
  try:apply(c,[e]);valid[i]=e
  except Exception as ex:invalid[i]=repr(ex)
 dump(R/f'{tag}_ejection_validity.json',dict(valid=list(valid),invalid=invalid));dump(R/f'{tag}_menu.json',es)
 return es,valid

def pairs(stem,es,rows,current,tag,workers):
 eligible=[r for r in rows if relevant(r,current)];sig=S.make(stem,eligible,tag,workers)
 by={r['edits'][0]:r for r in eligible if 'error'not in sig.get(r['edits'][0],{'error':1})}
 ids=sorted(by);tasks=set();links=[]
 # Every positive/cheap pair sharing propagated effects; nonmonotone singles get their strongest eight partners.
 good={i for i in ids if by[i]['loss']<current['loss']-5e-14 or buyer(by[i],current)}
 for i in ids:
  connected=[(S.strength(sig[i],sig[j]),j)for j in ids if i!=j]
  connected=sorted([(v,j)for v,j in connected if v>0],key=lambda x:(-x[0],by[x[1]]['loss'],x[1]))
  picked={j for _,j in connected[:8]}|{j for _,j in connected if i in good and j in good}
  for j in picked:tasks.add(tuple(sorted([i,j])))
  links.append(dict(id=i,neighbors=len(connected),selected=len(picked),single_loss=by[i]['loss']))
 dump(R/f'{tag}_interaction_graph.json',dict(eligible=len(ids),positive_or_buyers=len(good),links=links,pairs=len(tasks),policy='all interacting good pairs; strongest eight signature partners for other singles; decoder couples distinct output signatures'))
 return tasks

def contexts(stem,es,atoms,tag):
 c=M.read(stem);combos=set();details=[];original=set(es)
 # Undo selected edits, then regenerate moves that were blocked by them.
 for i,e in atoms.items():
  dropped,_=apply(c,[e]);new=fullmenu(dropped);added=[]
  for j,v in new.items():
   if j in original:continue
   if j in es and es[j]!=v:continue
   es[j]=v;added.append(j);combos.add(tuple(sorted([i,j])))
  details.append(dict(ejection=i,unlocked=added))
 # Multi-ejection moves let earlier choices be abandoned together.
 allatoms=json.loads((R/f'{tag}_all_atoms.json').read_text())
 for n in [2,3]:combos.update(tuple(sorted(x))for x in itertools.combinations(allatoms,n))
 dump(R/f'{tag}_contexts.json',details);dump(R/f'{tag}_menu.json',es)
 return combos

def fund(stem,menuf,rows,singles,current,tag,workers):
 buyers=sorted([r for r in singles if buyer(r,current)],key=lambda r:((r['loss']-current['loss'])/(r['acceptance']-current['acceptance']),r['loss']))
 # Distinct receipts can describe exactly the same buyer; keep unique whole-circuit identities.
 seen=set();bi=[]
 for r in buyers:
  if r['sha256']not in seen:seen.add(r['sha256']);bi.append(r['edits'][0])
 bi=bi[:12]
 beam=sorted([r for r in rows if 'loss'in r and r['acceptance']<FLOOR and r['loss']<current['loss']],key=lambda r:(r['loss'], -r['acceptance']))[:8]
 extra=[];history=[]
 for depth in range(1,5):
  tasks={tuple(sorted(set(r['edits'])|{i}))for r in beam for i in bi if i not in r['edits']}
  if not tasks:break
  freshrows=batch(stem,menuf,tasks,f'{tag}_fund{depth}',workers,current['loss']);extra+=freshrows
  under=[r for r in freshrows if 'loss'in r and r['acceptance']<FLOOR and r['loss']<current['loss']]
  # Retain loss and acceptance extremes plus non-dominated states, all ranked from measured full prices.
  pool=sorted(under,key=lambda r:(r['loss'],-r['acceptance']));front=[];maxa=-1
  for r in pool:
   if r['acceptance']>maxa:front.append(r);maxa=r['acceptance']
  choices=front+pool[:12]+sorted(under,key=lambda r:(-r['acceptance'],r['loss']))[:12]
  seen=set();beam=[]
  for r in choices:
   if r['sha256']not in seen:beam.append(r);seen.add(r['sha256'])
   if len(beam)>=24:break
  history.append(dict(depth=depth,priced=len(freshrows),feasible=sum(feasible(r)for r in freshrows),continuing=len(beam)))
 dump(R/f'{tag}_funding.json',dict(buyers=bi,levels=history,maximum_buyers=4));return extra

def select(stem,es,rows,current,atoms,tag,rnd):
 from judge4 import verify
 ranked=sorted([current]+[r for r in rows if feasible(r)],key=lambda r:(r['loss'],r['acceptance']*(r['loss']-current['loss'])))
 rejected=[];seen=set()
 for r in ranked:
  if r['sha256']in seen:continue
  seen.add(r['sha256'])
  if r['sha256']==current['sha256']:best=current;break
  judge=verify(r['stem'])
  if judge['gates_ok']and judge['speed_ok']:best=dict(r,judge_1e6=judge);break
  rejected.append(dict(sha256=r['sha256'],loss=r['loss'],judge=judge))
 selected=best.get('edits',[])if best['sha256']!=current['sha256']else[]
 remaining=dict(atoms);c=M.read(stem)
 # Store exact inverses after every actually applied primitive, preserving allocated record IDs.
 patch_ids=[i for i in selected if es[i]['fam']=='patch']
 if patch_ids:
  c,_=apply(c,[es[i]for i in patch_ids])
  for i in patch_ids:
   assert i in remaining, ('unexpected non-ejection patch',i)
   remaining.pop(i)
 for e in M.canon([es[i]for i in selected if es[i]['fam']!='patch']):
  before=copy.deepcopy(c);c=M.apply_edit(c,e);name=f'ejectr{rnd}:'+e['id'];remaining[name]=patch_edit(name,c,before)
 if selected:
  c,txt=M.normalized(M.fix(c));assert hashlib.sha256(txt.encode()).hexdigest()==best['sha256']
 gain=float(current['loss']-best['loss']);event=dict(round=rnd,before=current,price=best,selected=selected,gain=gain,stop=gain<1e-9,atoms=remaining,rejected=rejected)
 dump(R/f'{tag}_outcome.json',event)
 if best['loss']<TAU-3e-8 and best.get('judge_1e6',{}).get('gates_ok')and best['judge_1e6']['speed_ok']:
  dest=H/'cand'/f'merge4_r{rnd}_{best["sha256"][:12]}';shutil.copyfile(Path(best['stem']).with_suffix('.qasm'),dest.with_suffix('.qasm'));dump(dest.with_suffix('.json'),dict(best,tau=TAU,J_tau=best['acceptance']*(best['loss']-TAU),source=dict(round=rnd,selected=selected)))
 print(json.dumps(dict(event='round_selected',round=rnd,gain=gain,loss=best['loss'],acceptance=best['acceptance'],stop=event['stop'],selected=selected)),flush=True)
 return event

def run(workers):
 if not (R/'start.json').exists():initial()
 start=json.loads((R/'start.json').read_text());hf=R/'wide_history.json';history=json.loads(hf.read_text())if hf.exists()else[]
 if history and history[-1]['stop']:return history[-1]
 current=history[-1]['price']if history else start['price'];atoms=history[-1]['atoms']if history else start['atoms']
 for rnd in itertools.count(len(history)+1):
  tag=f'wide_r{rnd}';stem=current['stem']
  from specialize4 import specialize
  specialize(stem,current)
  es,valid=fresh(stem,atoms,tag);dump(R/f'{tag}_all_atoms.json',atoms);menuf=R/f'{tag}_menu.json'
  print(json.dumps(dict(event='round_start',round=rnd,menu=len(es),ejections=len(valid),loss=current['loss'],acceptance=current['acceptance'])),flush=True)
  singles=batch(stem,menuf,[[i]for i in es],tag+'_singles',workers,current['loss'])
  partial=R/f'{tag}_joint.jsonl'
  known=singles+([json.loads(x)for x in partial.read_text().splitlines()]if partial.exists()else[])
  quick=choose(known,current)
  if current['loss']-quick['loss']>=1e-9:
   # Commit the strong whole-circuit gain before rebuilding a large interaction graph.
   event=select(stem,es,known,current,atoms,tag,rnd)
   if event['gain']>=1e-9:
    event['phase']='strong improvement before expanded scan';history.append(event);dump(hf,history)
    current=event['price'];atoms=event['atoms'];continue
  pairtasks=pairs(stem,es,singles,current,tag,workers);pairtasks|=contexts(stem,es,valid,tag)
  joint=batch(stem,menuf,pairtasks,tag+'_joint',workers,current['loss'])
  rows=singles+joint;rows+=fund(stem,menuf,rows,singles,current,tag,workers)
  event=select(stem,es,rows,current,atoms,tag,rnd);event['phase']='complete widened neighborhood';history.append(event);dump(hf,history)
  current=event['price'];atoms=event['atoms']
  if event['stop']:dump(R/'wide_outcome.json',dict(complete=True,price=current,rounds=len(history),last_gain=event['gain']));return event

if __name__=='__main__':run(int(sys.argv[1]))
