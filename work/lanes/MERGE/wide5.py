from pass5 import *
import signature5 as S

def relevant(r,b):
 if 'loss'not in r:return False
 dl=r['loss']-b['loss'];da=r['acceptance']-b['acceptance']
 return dl<2e-7 or (da>1e-6 and dl<=max(3e-8,2e-5*da))

def buyer(r,b):
 if 'loss'not in r:return False
 dl=r['loss']-b['loss'];da=r['acceptance']-b['acceptance']
 return da>1e-6 and dl<=max(3e-8,2e-5*da)

def initial():
 b=record(C/'base','v37h reproduction');assert abs(b['loss']-TAU)<1e-13 and abs(b['acceptance']-.5015489333258328)<1e-13
 old=json.loads((H/'res37f/wide_history.json').read_text())[1];atoms=old['atoms']
 # Keep reviewer edits ejectable as exact patches on the current circuit.
 c=M.read(C/'base')
 for name in ['reviewer:c309','reviewer:herald17']:
  d=copy.deepcopy(c)
  if name.endswith('c309'):d['tail'].remove('// DETECTOR c[309]')
  else:
   d['ops'].remove(M.op_of_bit(d,367));d['tail'].remove('// DETECTOR c[367]');M.find(d,29,17,'RESET')['t']=30
  atoms['eject5:'+name]=patch_edit('eject5:'+name,c,d)
 from judge5 import verify
 v=verify(C/'base');assert v['gates_ok'] and v['speed_ok'],v
 dump(R/'start.json',dict(price=b,atoms=atoms,judge=v))
 update_status('running',b,[],phase='v37h reproduced; first herald and detector scan')

def fresh(stem,atoms,tag):
 c=M.read(stem);es=fullmenu(c);valid={};invalid={}
 for i,e in atoms.items():
  es[i]=e
  try:apply(c,[e]);valid[i]=e
  except Exception as ex:invalid[i]=repr(ex)
 dump(R/f'{tag}_ejection_validity.json',dict(valid=list(valid),invalid=invalid))
 oldpath=R/f'{tag}_menu.json'
 if oldpath.exists():
  old=json.loads(oldpath.read_text());changed=[i for i in es.keys()&old.keys() if json.dumps(es[i],sort_keys=True)!=json.dumps(old[i],sort_keys=True)]
  assert not changed,('resumed edit identities changed',changed)
 dump(oldpath,es)
 hs,audit=H5.menu(c);ds,gap=H5.detector_menu(c,Path(stem).with_suffix('.qasm').read_text())
 dump(R/f'{tag}_herald_coverage.json',audit);dump(R/f'{tag}_detector_gap.json',gap)
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
 # Keep the complete measured buyer frontier as well as the twelve best exchange rates.
 front_buyers=frontier(buyers)
 bi=list(dict.fromkeys(bi[:12]+[r['edits'][0]for r in front_buyers]))
 under=sorted([r for r in rows if 'loss'in r and r['acceptance']<FLOOR and r['loss']<current['loss']],key=lambda r:(r['loss'],-r['acceptance']))
 seeds=frontier(under)+under[:8]+sorted(under,key=lambda r:(-r['acceptance'],r['loss']))[:8]
 seen=set();beam=[]
 for r in seeds:
  if r['sha256']not in seen:seen.add(r['sha256']);beam.append(r)
 dump(R/f'{tag}_funding_seeds.json',dict(buyers=bi,seed_frontier=frontier(under),seeds=beam))
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
  history.append(dict(depth=depth,priced=len(freshrows),feasible=sum(feasible(r)for r in freshrows),continuing=len(beam)))
 dump(R/f'{tag}_funding.json',dict(buyers=bi,levels=history,maximum_buyers=4));return extra

def select(stem,es,rows,current,atoms,tag,rnd):
 from judge5 import verify
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
 remaining=copy.deepcopy(atoms);c=M.read(stem)
 # Store exact inverses after every actually applied primitive, preserving allocated record IDs.
 patch_ids=[i for i in selected if es[i]['fam']=='patch']
 if patch_ids:
  c,_=apply(c,[es[i]for i in patch_ids])
  for i in patch_ids:
   assert i in remaining, ('unexpected non-ejection patch',i)
   remaining.pop(i)
 for e in M.canon([es[i]for i in selected if es[i]['fam']!='patch']):
  before=copy.deepcopy(c);c=M.apply_edit(c,e)
  if e.get('prepend'):
   # Existing local ejections must follow the newly inserted global tick.
   for atom in remaining.values():
    for field in ('remove','add'):
     for op in atom['delta'][field]:
      u=M.unit(op)
      if not (op['t']==0 and u.name==e['name'] and list(u.qs)==[e['q']]):op['t']+=1
    atom['delta']['cells']=[(q,t+1)for q,t in atom['delta'].get('cells',[])]
  name=f'ejectr{rnd}:'+e['id'];remaining[name]=patch_edit(name,c,before)
 if selected:
  c,txt=M.normalized(M.fix(c));assert hashlib.sha256(txt.encode()).hexdigest()==best['sha256']
 gain=float(current['loss']-best['loss']);event=dict(round=rnd,before=current,price=best,selected=selected,gain=gain,stop=gain<1e-9,atoms=remaining,rejected=rejected)
 dump(R/f'{tag}_outcome.json',event)
 if best['loss']<TAU-3e-8 and best.get('judge_1e6',{}).get('gates_ok')and best['judge_1e6']['speed_ok']:
  dest=H/'cand'/f'merge5_r{rnd}_{best["sha256"][:12]}';shutil.copyfile(Path(best['stem']).with_suffix('.qasm'),dest.with_suffix('.qasm'));dump(dest.with_suffix('.json'),dict(best,tau=TAU,J_tau=best['acceptance']*(best['loss']-TAU),source=dict(round=rnd,selected=selected)))
 print(json.dumps(dict(event='round_selected',round=rnd,gain=gain,loss=best['loss'],acceptance=best['acceptance'],stop=event['stop'],selected=selected)),flush=True)
 return event

def run(workers):
 H5.MENU_WORKERS=workers
 if not (R/'start.json').exists():initial()
 start=json.loads((R/'start.json').read_text());hf=R/'wide_history.json';history=json.loads(hf.read_text())if hf.exists()else[]
 if history and history[-1]['stop']:return history[-1]
 current=history[-1]['price']if history else start['price'];atoms=history[-1]['atoms']if history else start['atoms']
 for rnd in itertools.count(len(history)+1):
  tag=f'wide_r{rnd}';stem=current['stem']
  from specialize5 import specialize
  specialize(stem,current)
  es,valid=fresh(stem,atoms,tag);dump(R/f'{tag}_all_atoms.json',atoms);menuf=R/f'{tag}_menu.json'
  print(json.dumps(dict(event='round_start',round=rnd,menu=len(es),ejections=len(valid),loss=current['loss'],acceptance=current['acceptance'])),flush=True)
  special=[i for i,e in es.items() if e['fam'] in ('herald','detparity')]
  early_tasks={(i,) for i in special}
  dets=[i for i in special if es[i]['fam']=='detparity']
  for n in range(2,min(len(dets),8)+1):early_tasks.update(itertools.combinations(dets,n))
  # All herald/detector pairs, irrespective of their single loss or second-order mass.
  special_pairs=set(itertools.combinations(special,2))
  early=batch(stem,menuf,early_tasks,tag+'_herald_det_singles',workers,current['loss'])
  checkpoint(early,current,tag)
  if current['loss']-choose(early,current)['loss']>=1e-9:
   event=select(stem,es,early,current,atoms,tag,rnd)
   if event['gain']>=1e-9:
    event['phase']='strong herald/detector improvement before full singles';history.append(event);dump(hf,history);update_status('running',event['price'],history,phase=event['phase'])
    current=event['price'];atoms=event['atoms'];continue
  singles=batch(stem,menuf,[[i]for i in es],tag+'_singles',workers,current['loss'])
  checkpoint(early+singles,current,tag)
  partial=R/f'{tag}_joint.jsonl'
  pilot=[json.loads(x)for x in (R/'pilot_r1_fund.jsonl').read_text().splitlines()]if rnd==1 and (R/'pilot_r1_fund.jsonl').exists()else[]
  pre_funded=fund(stem,menuf,early+singles,singles,current,tag+'_single',workers)
  known=early+singles+pre_funded+pilot+([json.loads(x)for x in partial.read_text().splitlines()]if partial.exists()else[])
  quick=choose(known,current)
  if current['loss']-quick['loss']>=1e-9:
   # Commit the strong whole-circuit gain before rebuilding a large interaction graph.
   event=select(stem,es,known,current,atoms,tag,rnd)
   if event['gain']>=1e-9:
    event['phase']='strong improvement before expanded scan';history.append(event);dump(hf,history);update_status('running',event['price'],history,phase='strong improvement; rebuilding grammar')
    current=event['price'];atoms=event['atoms'];continue
  herald_pairs=batch(stem,menuf,special_pairs,tag+'_herald_det',workers,current['loss'])
  pairtasks=pairs(stem,es,singles,current,tag,workers);pairtasks|=contexts(stem,es,valid,tag)
  joint=batch(stem,menuf,pairtasks,tag+'_joint',workers,current['loss'])
  rows=early+singles+herald_pairs+joint;rows+=fund(stem,menuf,rows,singles,current,tag,workers);rows+=pre_funded
  event=select(stem,es,rows,current,atoms,tag,rnd);event['phase']='complete widened neighborhood';history.append(event);dump(hf,history);update_status('complete' if event['stop'] else 'running',event['price'],history,phase='complete widened neighborhood')
  current=event['price'];atoms=event['atoms']
  if event['stop']:dump(R/'wide_outcome.json',dict(complete=True,price=current,rounds=len(history),last_gain=event['gain']));return event


def frontier(rows):
 out=[];maxa=-1;seen=set()
 for r in sorted([r for r in rows if 'loss'in r],key=lambda r:(r['loss'],-r['acceptance'])):
  if r['sha256'] in seen:continue
  seen.add(r['sha256'])
  if r['acceptance']>maxa:out.append(r);maxa=r['acceptance']
 return out

def checkpoint(rows,current,tag):
 dump(R/f'{tag}_pareto.json',frontier(rows+[current]))
 numerical=choose(rows,current)
 if numerical['loss']<TAU-3e-8 and numerical['sha256']!=current['sha256']:
  from judge5 import verify
  dest=H/'cand'/f'merge5_live_{numerical["sha256"][:12]}'
  shutil.copyfile(Path(numerical['stem']).with_suffix('.qasm'),dest.with_suffix('.qasm'))
  dump(dest.with_suffix('.json'),dict(numerical,status='exact finalist; judge pending',qualifies_vs_v37h=True))
  judge=verify(numerical['stem']);dump(dest.with_suffix('.json'),dict(numerical,judge_1e6=judge,status='finalist' if judge['gates_ok'] and judge['speed_ok'] else 'judge rejected',qualifies_vs_v37h=bool(judge['gates_ok'] and judge['speed_ok'])))
 history=json.loads((R/'wide_history.json').read_text())if (R/'wide_history.json').exists()else[]
 update_status('running',current,history,phase=tag+' partial scans completed; convergence pending',numerical=numerical)

def update_status(status,best,history,phase='',numerical=None):
 receipts=sorted(R.glob('*.jsonl'));rows=[];index={}
 for p in receipts:
  for line_no,line in enumerate(p.read_text().splitlines(),1):
   r=json.loads(line)
   if 'sha256' not in r:continue
   rows.append(r);index[r['sha256']]=dict((k,r[k])for k in ('stem','data_qubits','loss','acceptance','error')if k in r)
   index[r['sha256']]['receipt']=str(p.relative_to(H))+':'+str(line_no)
 dump(R/'pareto.json',frontier(rows+[best]))
 result=dict(status=status,phase=phase,baseline_loss=TAU,baseline_acceptance=.5015489333258328,best=best,numerical=numerical,history='res37h/wide_history.json',receipts=[str(p.relative_to(H))for p in receipts],priced_qasm=index,previous_results='archive/results_pass4.json')
 dump(H/'results.json',result)
 gapfiles=sorted(R.glob('*_detector_gap.json'));gap=json.loads(gapfiles[-1].read_text())if gapfiles else None
 lines=['# MERGE — pass 5 on v37h','',f'Status: {status}. {phase}.',f'Baseline reproduced: L={TAU:.17g}, A=0.5015489333258328; six raw output stabilizers +1.',f'Current selected: L={best["loss"]:.17g}, A={best["acceptance"]:.17g}; SHA256 `{best["sha256"]}`.',f'Gain from v37h: {TAU-best["loss"]:.12g}; finalist threshold >3e-8; exact acceptance floor 0.5002.',f'Full receipts: res37h/*.jsonl ({len(rows)}); saved circuits v37h/; new artifacts cand/merge5_*.',f'Detector surrogate latest: {json.dumps(gap)}' if gap else 'Detector span scan pending.', 'Every reset/RX has a herald attempt; busy cells use predecessor cascades and CP-SAT commuting reschedules (at most eight moved CX/M units, +/-2 ticks). Echo/check ejections unlock otherwise blocked heralds. Initial preparations get a prepended tick.', 'Redundant repeated preparations also allow replacing the later preparation with a matching measurement of the earlier one.', 'Every detector subset (up to eight residual directions) and every herald/detector pair is exact-priced without second-order pruning.', 'Pass-4 moves, historical ejections and signature pairs are retained. Funding uses up to four buyers and preserves the full measured buyer and seed Pareto fronts; intermediate frontiers are not truncated.', 'Selection: minimum exact loss among feasible judge-valid builds. Tau follows the current circuit. Judge uses 1e6 shots, one process, paired with v37h on hippo; time penalty is reported for main-session expected-key selection.', 'Reviewer screens located at MAIN/spec/reviewer17/results/ (the supplied unz path was stale); no reviewer code executed.', 'Decisions apply to this pass only; no standing rule changed. No submission, commit, push, subagent or other-lane write.', 'Checked: saved QASM/output identities, all-orders raw code-space assertion and exact acceptance. Final completion and any unverified scope are stated below.']
 for e in history:lines.append(f'Round {e["round"]}: gain={e["gain"]:.12g}, L={e["price"]["loss"]:.17g}, A={e["price"]["acceptance"]:.17g}; selected={e["selected"]}; phase={e["phase"]}.')
 (H/'REPORT.md').write_text('\n'.join(lines)+'\n')

if __name__=='__main__':
 print(json.dumps(dict(event='main_started',pid=os.getpid(),workers=int(sys.argv[1]))),flush=True)
 run(int(sys.argv[1]))
