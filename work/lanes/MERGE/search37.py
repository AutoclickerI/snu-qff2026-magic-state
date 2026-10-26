from cont37 import *
def load(tag):
 p=R/f'{tag}.jsonl';return {tuple(r['edits']):r for r in (json.loads(l) for l in p.read_text().splitlines())} if p.exists() else {}
def relevant(r,b):
 if 'loss'not in r:return False
 dl=r['loss']-b['loss'];da=r['acceptance']-b['acceptance']
 return dl < -5e-14 or (da>1e-6 and dl<=max(3e-8,2e-5*da))
def connected(tag,stem):
 b=record(stem,'pair reference');c=M.read(stem);es=json.loads((R/f'{tag}_menu.json').read_text());s=load(tag+'_s1')
 ids=sorted({k[0] for k,r in s.items() if relevant(r,b)})
 seqs={q:[o['t'] for o in M.ops_on(c,q)] for q in range(36)}
 fps={i:M.footprint(c,es[i],seqs) for i in ids}
 combos=[list(p) for p in itertools.combinations(ids,2) if M.connected(fps[p[0]],fps[p[1]])]
 dump(R/f'{tag}_b2_tasks.json',combos);dump(R/f'{tag}_eligible.json',dict(ids=ids,base=b,footprints=fps))
 print(json.dumps(dict(event='connected_pairs',tag=tag,eligible=len(ids),pairs=len(combos))),flush=True)
def context(i):
 from cont37 import BASE,EDITS
 try:
  f=EDITS[i];c,_=M.apply_bundle(BASE,[f]);es=fullmenu(c);old=set(EDITS)
  # All newly unlocked additions and locally changed single-CX slots.
  cells=M.touched(BASE,f);qs={q for q,t in cells};near=qs|{p for q in qs for p in M.ADJ[q]}
  fp=M.footprint(BASE,f);lo=min(x[0] for x in fp.values())-1;hi=max(x[1] for x in fp.values())+1
  adds=[e for e in es.values() if e['fam'] in M.ADDF and (e['id']not in old or e['fam']=='cx' and (e['a']in near or e['b']in near) and lo<=e['t']<=hi)]
  return dict(id=i,additions=adds)
 except Exception as ex:return dict(id=i,error=repr(ex))
def contexts(tag,stem,workers):
 import cont37
 menuf=R/f'{tag}_menu.json';cont37.init(stem,menuf);eligible=json.loads((R/f'{tag}_eligible.json').read_text())['ids']
 freeing=[i for i in eligible if cont37.EDITS[i]['fam']in ['rm','rmcx','trade','shift','pd']]
 es=dict(cont37.EDITS);combos=[];records=[]
 with get_context('fork').Pool(workers) as pool:
  for r in pool.imap_unordered(context,freeing):
   records.append(r)
   for e in r.get('additions',[]):
    # An ID is an exact recipe, including the primitive removals on this base.
    if e['id']in es and es[e['id']]!=e:continue
    es[e['id']]=e
    if r['id']!=e['id']:combos.append(sorted([r['id'],e['id']]))
 dump(R/f'{tag}_contexts.json',records);dump(menuf,es)
 previous=json.loads((R/f'{tag}_b2_tasks.json').read_text());allpairs=sorted(set(tuple(x) for x in previous+combos))
 dump(R/f'{tag}_b2_tasks.json',allpairs)
 print(json.dumps(dict(event='context_pairs',tag=tag,freeing=len(freeing),context_pairs=len(combos),all_pairs=len(allpairs),menu=len(es))),flush=True)
def greedy_prepare(tag,stem,roundnum):
 single=load(tag+'_s1');pairs=load(tag+'_b2');base=record(stem,'greedy base');historyf=R/f'{tag}_history.json'
 history=json.loads(historyf.read_text()) if historyf.exists() else []
 current=history[-1]['price'] if history else base;selected=history[-1]['selected'] if history else []
 moves=[set(k) for k,r in {**single,**pairs}.items() if 'loss'in r and r['loss']<base['loss']-5e-14]
 buyers=[set(k) for k,r in single.items() if 'loss'in r and r['acceptance']>base['acceptance']+1e-6 and relevant(r,base)]
 moves+=buyers
 combos=sorted({tuple(sorted(set(selected)|m)) for m in moves if not m<=set(selected)})
 dump(R/f'{tag}_g{roundnum}_tasks.json',combos)
 dump(R/f'{tag}_g{roundnum}_state.json',dict(base=str(Path(stem).resolve()),current=current,selected=selected,moves=len(moves),buyers=[sorted(x) for x in buyers]))
 print(json.dumps(dict(event='greedy_prepare',round=roundnum,tasks=len(combos),moves=len(moves),selected=selected,current_loss=current['loss'])),flush=True)
def fund_prepare(tag,roundnum):
 state=json.loads((R/f'{tag}_g{roundnum}_state.json').read_text());rows=list(load(f'{tag}_g{roundnum}').values());current=state['current']
 under=sorted([r for r in rows if 'loss'in r and r['acceptance']<FLOOR and r['loss']<current['loss']],key=lambda r:r['loss'])[:5]
 combos=sorted({tuple(sorted(set(r['edits'])|set(b))) for r in under for b in state['buyers'] if not set(b)<=set(r['edits'])})
 dump(R/f'{tag}_g{roundnum}_fund_tasks.json',combos)
 print(json.dumps(dict(event='fund_prepare',round=roundnum,under=len(under),tasks=len(combos))),flush=True)
def select(tag,roundnum):
 from judge37 import verify
 state=json.loads((R/f'{tag}_g{roundnum}_state.json').read_text());current=state['current'];selected=state['selected'];es=json.loads((R/f'{tag}_menu.json').read_text())
 rows=list(load(f'{tag}_g{roundnum}').values())+list(load(f'{tag}_g{roundnum}_fund').values())
 rows=sorted([r for r in rows if feasible(r) and rank(r)<rank(current)-5e-14],key=rank)
 rejected=[];best=current
 for r in rows:
  jf=R/f"judge_{r['sha256']}.json"
  v=json.loads(jf.read_text()) if jf.exists() else verify(Path(r['stem']))
  if not(v.get('gates_ok') and v.get('speed_ok')):
   rejected.append(dict(sha256=r['sha256'],judge=v));continue
  best=r;selected=r['edits'];break
 gain=current['loss']-best['loss'];event=dict(round=roundnum,selected=selected,price=best,loss_gain=gain,J_before=rank(current),J_after=rank(best),stop=bool(gain<1e-9),runtime_rejections=rejected)
 hf=R/f'{tag}_history.json';history=json.loads(hf.read_text()) if hf.exists() else [];history.append(event);dump(hf,history)
 if best['loss']<TAU-3e-8 and best is not current:
  v=json.loads((R/f"judge_{best['sha256']}.json").read_text());p=H/'cand'/f'{tag}_g{roundnum}_{best["sha256"][:12]}'
  shutil.copyfile(Path(best['stem']).with_suffix('.qasm'),p.with_suffix('.qasm'));c=M.read(best['stem'])
  dump(p.with_suffix('.json'),dict(best,judge_1e6=v,cx=sum(M.unit(o).name=='CX' for o in c['ops']),native_depth=M.depth(c),source=dict(base=state['base'],edits=selected)))
 print(json.dumps(dict(event='greedy_select',**event)),flush=True)
 return event
if __name__=='__main__':
 cmd=sys.argv[1];tag=sys.argv[2]
 if cmd=='pairs':connected(tag,Path(sys.argv[3]))
 elif cmd=='contexts':contexts(tag,Path(sys.argv[3]),int(sys.argv[4]))
 elif cmd=='prepare':greedy_prepare(tag,Path(sys.argv[3]),int(sys.argv[4]))
 elif cmd=='fund':fund_prepare(tag,int(sys.argv[3]))
 elif cmd=='select':select(tag,int(sys.argv[3]))
