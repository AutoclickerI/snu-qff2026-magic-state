from common import *
from guards import catalog,apply,pulse_commutes
base=load(H/'control_R38');save(base,'matrix_R38');new=catalog(base);old=json.loads((H/'control_R38.actions.json').read_text());merged={}
def key(a):return json.dumps({k:v for k,v in a.items()if k!='id'},sort_keys=True)
for a in old:
 f=H/('control_R38_'+a['id']+'.price.json')
 if f.exists()and json.loads(f.read_text()).get('ok'):
  if a['type']=='echo':assert all(pulse_commutes(o,a['q'],a['axis'])for o in base['ops']if a['first']<o['t']<a['last'])
  merged[key(a)]=a
for a in new:merged[key(a)]=a
cache={}
for f in H.glob('*.price.json'):
 r=json.loads(f.read_text());name=r.get('stem');q=H/(str(name)+'.qasm');meta=H/(str(name)+'.json');ideal=H/(str(name)+'.ideal.json');full=H/(str(name)+'.allorders.json')
 if r.get('ok')and q.exists()and meta.exists()and ideal.exists()and full.exists():
  m=json.loads(meta.read_text());v=json.loads(ideal.read_text());sha=hashlib.sha256(q.read_bytes()).hexdigest()
  if v.get('passed')and v.get('qasm_sha256')==sha:cache[(sha,tuple(m['data_qubits']))]=(name,r)
out=[];pending=[];hits=0
for i,a in enumerate(merged.values()):
 a=copy.deepcopy(a);a['id']=f'g{i:03d}';stem=save(apply(base,[a]),'matrix_R38_'+a['id']);meta=json.loads(stem.with_suffix('.json').read_text());hit=cache.get((meta['qasm_sha256'],tuple(meta['data_qubits'])))
 if hit:
  source,r=hit;rr=dict(r,stem=stem.name,byte_identical_receipt_source=source,qasm_sha256=meta['qasm_sha256']);stem.with_suffix('.price.json').write_text(json.dumps(rr,indent=2))
  for suffix in('.ideal.json','.allorders.json'):
   d=json.loads((H/(source+suffix)).read_text());d['byte_identical_receipt_source']=source;stem.with_suffix(suffix).write_text(json.dumps(d,indent=2))
  hits+=1
 else:pending.append(stem.name)
 out.append(a)
(H/'matrix_R38.actions.json').write_text(json.dumps(out,indent=2));(H/'corrected_pending.json').write_text(json.dumps(pending));(H/'corrected_scope.json').write_text(json.dumps(dict(old_proposals=len(old),new_generated=len(new),merged_valid_old_plus_new=len(out),verified_same_bytes_cache_hits=hits,new_prices_required=len(pending),control_direction='parsed from CX text, never unordered occupancy qs'),indent=2))
print('corrected catalog',len(out),'cache',hits,'new',len(pending),flush=True)
