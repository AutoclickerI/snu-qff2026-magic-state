from reset_keep import *
import tprep
rows=[json.loads(l)for l in (OUT/'reset_keep.jsonl').read_text().splitlines()]
for fam in ['h','w']:
 r=min([r for r in rows if r['desc']['base']==fam],key=lambda r:r['total'])
 for c,d in cs:
  if all(r['desc'].get(k)==v for k,v in d.items()):
   c=normalize(c);txt=textof(c);assert hashlib.sha256(txt.encode()).hexdigest()==r['sha256'];ref=score(txt);assert abs(ref['total']-r['total'])<1e-14
   r['pruned_exact2_check']=ref;r['stem']='reset_'+fam;save(r['stem'],txt,c['meta'],r)
   start=time.monotonic();ck=tprep.check(txt,D,shots=10000,seed=0);r['runtime_probe']=dict(shots=10000,seconds=time.monotonic()-start,passed=ck.passed,acceptance=ck.acceptance)
   (OUT/(r['stem']+'.runtime.json')).write_text(json.dumps(r['runtime_probe'],indent=2));print(r['stem'],r['total'],r['runtime_probe'],flush=True)
