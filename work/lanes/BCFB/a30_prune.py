"""Remove only checksum-verified archived bulk; preserve all verified finalists."""
from a30_common import *
import hashlib,shutil
A=json.loads((H/'ARCHIVE_AUDIT.json').read_text());assert A['status']=='PASS';assert hashlib.sha256((H/'witnesses.tar.xz').read_bytes()).hexdigest()==A['sha256']
verified=json.loads((D/'verified_finalists.json').read_text());newkeep={r['stem'] for r in verified};oldkeep={p.name[:-len('.mc.json')] for p in (H/'blue/finalists').glob('*.mc.json') if len(json.loads(p.read_text()).get('seeds',[]))==3}
# Keep full all-orders receipts with retained finalists, not loose candidate collections.
summary=json.loads((D/'allorders_summary.json').read_text())
for r in verified:
 match=next(x for x in summary if x['sha256']==r['sha256'])
 source=D/'sparse'/(match['stem']+'_canonical_sparse_result.json')
 if source.exists():shutil.copy2(source,D/'finalists'/(r['stem']+'.allorders.json'))
keep_a30={'attribution_verified.json','search_summary.json','allorders_summary.json','verified_finalists.json','geometry_audit.json','sparse_copy_hashes.json','base_reference_allorders.json','process_exit_audit.json','delivery_audit.json','slow_exclusions.json','search_budget_summary.json','fault_class_mechanism.json'}
keep_blue={'base_prices.json','base_redraws.json','redraw_summary.json','cache_audit.json','cache_restart.json','finalist_recommendation.json'}
deleted=[]
for rel,m in A['manifest'].items():
 p=H/rel
 if not p.exists():continue
 if hashlib.sha256(p.read_bytes()).hexdigest()!=m['sha256']:continue # regenerated summaries are retained
 parts=Path(rel).parts;remove=False
 if parts[0]=='a30':
  if len(parts)>1 and parts[1]=='finalists':remove=not any(p.name==s+'.qasm' or p.name.startswith(s+'.') for s in newkeep)
  elif len(parts)>1 and parts[1]=='sparse':remove=p.name.endswith('_result.json')
  elif len(parts)>1 and parts[1]=='runs':remove=not(p.name.startswith('feedback_81') and p.name.endswith('.receipt.json')) and p.name not in ('baseline_exact.log','baseline_allorders.log','slow_gate_stop.json')
  else:remove=p.name not in keep_a30
 elif parts[0]=='blue':
  if len(parts)>1 and parts[1]=='finalists':remove=not any(p.name.startswith(s+'.') for s in oldkeep)
  elif len(parts)>1 and parts[1]=='inputs':remove=False
  else:remove=p.name not in keep_blue
 elif rel=='search.csv':remove=True
 if remove:p.unlink();deleted.append(rel)
for cache in [D/'.xtim_cache',H/'blue/.xtim_cache']:
 if cache.exists():shutil.rmtree(cache)
receipt=dict(status='PASS',archive_sha256=A['sha256'],deleted=deleted,new_finalists=sorted(newkeep),blue_finalists=sorted(oldkeep))
(H/'PRUNE_AUDIT.json').write_text(json.dumps(receipt,indent=2));print(dict(deleted=len(deleted),new_finalists=len(newkeep),blue_finalists=len(oldkeep)),flush=True)
