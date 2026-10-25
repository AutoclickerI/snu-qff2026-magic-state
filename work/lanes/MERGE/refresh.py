from campaign import *
from merge_build import menu
def scan():
 archive={}
 for lane in ['POLISH','GLOBAL','COMPLETE']:
  rows=[]
  for f in (H.parent/lane/'cand').glob('*.json'):
   m=json.loads(f.read_text());r=m.get('all_orders',m.get('allorders',m))
   if 'loss' not in r:continue
   s=sha(f.with_suffix(''));rows.append(dict(path=str(f.with_suffix('')),loss=r['loss'],acceptance=r['acceptance'],sha256=s,metadata=m))
  archive[lane]=sorted(rows,key=lambda r:r['acceptance']*(r['loss']-TAU) if r['acceptance']>=FLOOR else 1)
 write(H/'res/final_refresh_sources.json',archive)
 return archive
def main(best):
 archive=scan();tasks=[];audit={};a=M.read(H/'builds/A');base=M.read(best)
 for lane,key in [('POLISH','P'),('GLOBAL','G'),('COMPLETE','C')]:
  r=archive[lane][0];old=next(json.loads(l) for l in (H/'res/prices.jsonl').read_text().splitlines() if Path(json.loads(l)['stem']).name==key)
  audit[lane]=dict(path=r['path'],sha256=r['sha256'],advertised_L=r['loss'],advertised_A=r['acceptance'],old_sha256=old['sha256'],newer_and_better=r['sha256']!=old['sha256'] and r['loss']<old['loss']-1e-13)
  if not audit[lane]['newer_and_better']:continue
  st=snapshot(r['path'],'refresh_'+lane);price(st,'final refresh source '+lane)
  new=M.read(st);d=delta(a,new);write(H/'res'/f'refresh_diff_{lane}.json',d)
  # Complete direct merge where there is no native footprint conflict.
  try:
   c=apply_delta(base,d);s=save(c,'refresh_direct_'+lane,'final refresh direct '+lane);tasks.append(dict(stem=str(s.relative_to(H)),why='final refresh direct '+lane))
  except Exception as ex:audit[lane]['direct_conflict']=repr(ex)
  if lane=='POLISH':
   oldp=M.read(H/'builds/P');dp=delta(oldp,new);write(H/'res/refresh_increment_POLISH.json',dp)
   try:
    c=apply_delta(base,dp);s=save(c,'refresh_polish_increment','apply newer POLISH incremental diff');tasks.append(dict(stem=str(s.relative_to(H)),why='newer POLISH incremental diff'))
   except Exception as ex:audit[lane]['increment_conflict']=repr(ex)
   ids=r['metadata'].get('moved',{}).get('edits',[]);es=menu(base);ported=[];missing=[]
   for i in ids:
    if i in es:ported.append(es[i])
    else:missing.append(i)
   audit[lane]['regenerated_available']=[e['id'] for e in ported];audit[lane]['already_changed_or_unavailable']=missing
   for e in ported:
    try:
     c,_=M.apply_bundle(base,[e]);s=save(c,'refresh_P_'+hashlib.sha256(e['id'].encode()).hexdigest()[:10],'new POLISH reapplied '+e['id']);tasks.append(dict(stem=str(s.relative_to(H)),why=dict(stage='final_refresh',edits=[e['id']])))
    except Exception as ex:audit[lane].setdefault('reapply_failures',[]).append(dict(id=e['id'],error=repr(ex)))
   # Port the new echo/check bundle together and optionally restore its old prefix source.
   echo=[e for e in ported if e['fam']=='echo' or e['id']=='rm:chk_h21_15_20_22_20_31_only22']
   if echo:
    try:
     c,_=M.apply_bundle(base,echo);s=save(c,'refresh_P_bundle','new POLISH echo/buyer bundle');tasks.append(dict(stem=str(s.relative_to(H)),why=dict(stage='final_refresh',edits=[e['id'] for e in echo])))
    except Exception as ex:audit[lane]['bundle_conflict']=repr(ex)
  else:
   audit[lane]['needs_manual_port']=True
 write(H/'res/final_refresh_audit.json',audit);write(H/'res/final_refresh_tasks.json',tasks)
 print(json.dumps(dict(event='final_refresh',audit=audit,tasks=len(tasks))),flush=True)
if __name__=='__main__':main(Path(sys.argv[1]))
