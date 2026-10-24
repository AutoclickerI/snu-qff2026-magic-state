from common import *
from guards import apply
import concurrent.futures

def one(item):
 i,action=item
 try:
  s=save(apply(BASE,[action]),f'portcheck_{i:03d}');verify(s);r=dict(index=i,action=action,ok=True)
 except Exception as e:r=dict(index=i,action=action,ok=False,error=repr(e))
 print(json.dumps(r),flush=True);return r
if __name__=='__main__':
 BASE=load(H/'control_R37selective');unique={}
 for f in sorted(H.glob('R37selective_pack*.json')):
  if f.name.count('.')!=1:continue
  m=json.loads(f.read_text())
  for a in m['protection_actions']:unique[json.dumps(a,sort_keys=True)]=a
 with concurrent.futures.ProcessPoolExecutor(8)as pool:out=list(pool.map(one,enumerate(unique.values())))
 (H/'port_action_validity.json').write_text(json.dumps(out,indent=2));good={json.dumps(r['action'],sort_keys=True)for r in out if r['ok']};names=[]
 for f in sorted(H.glob('R37selective_pack*.json')):
  if f.name.count('.')!=1:continue
  m=json.loads(f.read_text());aa=[a for a in m['protection_actions']if json.dumps(a,sort_keys=True)in good];p=apply(BASE,aa);p['meta']['port_repair']=dict(source=f.stem,rejected_actions=[a for a in m['protection_actions']if a not in aa],method='Restore original operation for individually invalid intervention; all original detectors remain.');s=save(p,f.stem+'_valid');names.append(s.name)
 (H/'port_repaired_queue.json').write_text(json.dumps(names))
