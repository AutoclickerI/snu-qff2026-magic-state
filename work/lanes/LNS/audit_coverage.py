"""Associate old failure receipts with hashes and audit finite coverage."""
from moves import *
import hops

def key(d):return json.dumps({k:v for k,v in d.items()if k not in ('source','parent_total','local_track','iteration')},sort_keys=True)

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('pattern');a=ap.parse_args();rows=[]
 for f in OUT.glob('*.jsonl'):
  for line in f.read_text().splitlines():
   try:r=json.loads(line)
   except ValueError:continue
   if isinstance(r,dict)and 'desc'in r:rows.append(r)
 good={r['sha256']:r for r in rows if r.get('sha256')};repairs=[]
 for cf in OUT.glob(a.pattern):
  cert=json.loads(cf.read_text());src=cert['source'];base=read(src);bad={key(r['desc']):r for r in rows if r.get('error')and not r.get('sha256')and r['desc'].get('source')==src};families={r['desc']['family']for r in bad.values()}
  generators=[]
  if 'init'in families:generators += [init_moves,extra_init_moves]
  if 'readout'in families:generators += [readout_moves,detector_moves]
  if 'hop'in families:generators += [hops.moves]
  if 'commute'in families:generators += [commute_moves]
  if 'phase'in families:generators += [phase_moves]
  if 'timing'in families:generators += [lambda b:timing_moves(b,True)]
  for gen in generators:
   for c,d in gen(base):
    if key(d)not in bad or c is None:continue
    try:c=normalize(c)
    except (ValueError,AssertionError):continue
    sha=hashlib.sha256(textof(c).encode()).hexdigest();r=bad[key(d)];good[sha]=dict(r,sha256=sha);repairs.append(dict(source=src,desc=d,sha256=sha,error=r['error']))
  result={}
  for family,cv in cert['coverage'].items():
   hs=set(cv['hashes']);rr=[good[h]for h in hs if h in good];valid=[r for r in rr if 'total'in r and r['exp_minus_A1']>=.505]
   result[family]=dict(generated=cv['generated'],build_failures=len(cv['build_failures']),unique=len(hs),receipts=len(rr),invalid=sum('error'in r for r in rr),below_acceptance=sum(r.get('exp_minus_A1',1)<.505 for r in rr),missing=sorted(hs-good.keys()),best=min((r['total']for r in valid),default=None),strict_improvements=sum(r['total']<cert['parent_total']-1e-12 for r in valid))
  out=dict(source=src,parent_total=cert['parent_total'],improved=cert['improved'],families=result,scope=cert['scope'],all_normalized_candidates_have_receipts=all(not r['missing']for r in result.values()),build_failures_are_not_optimality_proofs=True)
  target=cf.with_suffix('.audit.json');target.write_text(json.dumps(out,indent=2));print(target.name,json.dumps(out),flush=True)
 (OUT/'failure_hash_reconstruction.json').write_text(json.dumps(repairs,indent=2))
