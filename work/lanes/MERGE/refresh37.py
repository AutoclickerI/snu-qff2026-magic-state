from cont37 import *
def flatten(obj):
 if isinstance(obj,dict):
  if 'loss'in obj and 'acceptance'in obj:yield obj
  elif 'experiments'in obj:yield from flatten(obj['experiments'])
  else:
   for x in obj.values():
    if isinstance(x,(dict,list)):yield from flatten(x)
 elif isinstance(obj,list):
  for x in obj:yield from flatten(x)
def source_path(folder,r,fallback=None):
 val=r.get('path',r.get('stem',r.get('qasm_path',fallback)))
 if val is None:return None
 p=Path(val)
 if not p.is_absolute():p=folder/p
 return p.with_suffix('')
def grid_ok(st):
 import re
 for line in st.with_suffix('.qasm').read_text().splitlines():
  if line.strip().startswith('cx '):
   q=list(map(int,re.findall(r'q\[(\d+)\]',line)))
   if len(q)!=2 or abs(q[0]//6-q[1]//6)+abs(q[0]%6-q[1]%6)!=1:return False
 return True
def scan():
 out={}
 for lane in ['POLISH','GLOBAL','SQUARE','ENDSEARCH']:
  folder=H.parent/lane;entries=[];source=folder/'results.json';ledger=json.loads(source.read_text())
  for r in flatten(ledger):
   st=source_path(folder,r)
   if st is None or not st.with_suffix('.qasm').exists():continue
   entries.append(dict(r,stem=str(st),origin='results'))
  for f in (folder/'cand').glob('*.json'):
   m=json.loads(f.read_text());r=m.get('all_orders',m.get('allorders',m))
   if 'loss'in r and 'acceptance'in r:entries.append(dict(r,stem=str(f.with_suffix('')),origin='cand',metadata=m))
  bysha={};excluded=collections.Counter()
  for r in sorted(entries,key=lambda r:r['loss']):
   if r['acceptance']<FLOOR:excluded['acceptance']+=1;continue
   if r.get('phantom') or r.get('metadata',{}).get('grid_free'):excluded['grid_free_or_phantom']+=1;continue
   st=Path(r['stem'])
   if not grid_ok(st):excluded['nonadjacent_CX']+=1;continue
   s=sha(st);r['sha256']=s
   if s not in bysha or r['origin']=='cand':bysha[s]=r
  physical=sorted(bysha.values(),key=lambda r:r['loss'])
  out[lane]=dict(results_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),results_entries=len(ledger),observed=len(entries),excluded=dict(excluded),best=physical[:4])
 dump(R/'refresh_sources.json',out);return out
def main(stem):
 sources=scan();base=M.read(stem);es=fullmenu(base);added=[];audit={};tasks=[]
 prior=json.loads((H/'res/final_refresh_sources.json').read_text())
 # The previous GLOBAL merge used a stronger build than its published cand/ copy.
 grow=next(json.loads(l) for l in (H/'res/prices.jsonl').read_text().splitlines() if Path(json.loads(l)['stem']).name=='G')
 prior['GLOBAL']=[dict(loss=grow['loss'],sha256=grow['sha256'])]
 for lane,pack in sources.items():
  if not pack['best']:audit[lane]=dict(status='no saved grid-valid candidate at acceptance floor');continue
  r=pack['best'][0];old=prior.get(lane,[{}])[0]
  audit[lane]=dict(best=r['stem'],loss=r['loss'],acceptance=r['acceptance'],sha256=r['sha256'],previous_loss=old.get('loss'))
  if lane in ['POLISH','GLOBAL'] and old.get('loss') is not None and r['loss']>=old['loss']-1e-13:
   audit[lane]['status']='no improvement over previous lane snapshot';continue
  if lane in ['SQUARE','ENDSEARCH'] and r['loss']>=TAU:
   audit[lane]['status']='best admissible saved build loses to v37c';continue
  st=C/('refresh_'+lane)
  shutil.copyfile(Path(r['stem']).with_suffix('.qasm'),st.with_suffix('.qasm'))
  if Path(r['stem']).with_suffix('.json').exists():shutil.copyfile(Path(r['stem']).with_suffix('.json'),st.with_suffix('.json'))
  else:
   dq=r.get('data_qubits',r.get('metadata',{}).get('data_qubits'))
   if dq is None:
    audit[lane]['status']='source has no ordered data mapping';continue
   dump(st.with_suffix('.json'),dict(data_qubits=dq))
  reproduced=price(st,dict(kind='source refresh reproduction',lane=lane))
  audit[lane]['reproduced']=reproduced
  if not feasible(reproduced):audit[lane]['status']='source fails exact reproduction/acceptance';continue
  if old.get('loss') is not None and reproduced['loss']>=old['loss']-1e-13:
   audit[lane]['status']='reproduced full circuit does not improve prior source';continue
  new=M.read(st)
  from campaign import delta,apply_delta
  d=delta(M.read(H/'builds/A'),new);dump(R/f'refresh_{lane}_diff.json',d)
  try:
   v=apply_delta(base,d);s=save(v,'refresh_direct_'+lane,dict(kind='direct source merge',lane=lane));price(s,dict(kind='direct source merge',lane=lane));audit[lane]['direct']=str(s)
  except Exception as ex:audit[lane]['direct_conflict']=repr(ex)
  if lane=='POLISH':
   meta=r.get('metadata',json.loads(st.with_suffix('.json').read_text()));ids=meta.get('moved',{}).get('edits',[])
   if not ids:
    ids=next((a.get('moved',[]) for a in r.get('aliases',[]) if isinstance(a.get('moved'),list)),[])
   available=[i for i in ids if i in es];audit[lane]['available']=available;audit[lane]['changed_or_consumed']=[i for i in ids if i not in es]
   tasks += [[i] for i in available]
   tasks += [list(p) for p in itertools.combinations(available,2) if M.connected(M.footprint(base,es[p[0]]),M.footprint(base,es[p[1]]))]
   added+=available;audit[lane]['status']='reapplied surviving recipes and connected pairs'
  else:audit[lane]['status']='manual transport required' if 'direct_conflict'in audit[lane] else 'direct merge priced'
 dump(R/'refresh_menu.json',es);dump(R/'refresh_tasks.json',sorted(set(tuple(t) for t in tasks)));dump(R/'refresh_audit.json',audit)
 print(json.dumps(dict(event='refresh',audit=audit,tasks=len(tasks))),flush=True)
if __name__=='__main__':main(Path(sys.argv[1]))
