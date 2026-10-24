"""Iterate the explicitly enumerated neighborhood; preserve per-family coverage."""
from moves import *
import hops
from round_lns import proposals
from compound import apply
import itertools

def records():
 out={}
 for f in OUT.glob('*.jsonl'):
  for line in f.read_text().splitlines():
   try:r=json.loads(line)
   except ValueError:continue
   if isinstance(r,dict) and r.get('sha256') and 'desc' in r:out[r['sha256']]=r
 return out

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('stem');ap.add_argument('--label',default='closure');ap.add_argument('--workers',type=int,default=10);a=ap.parse_args()
 base=read(a.stem);stage=0
 while True:
  stage+=1;parent=base['meta']['lns_result']['total'];label=f'{a.label}{stage}';candidates=[];coverage={};built={};timings={}
  families=[('timing',lambda b:timing_moves(b,True)),('commute',commute_moves),('init',init_moves),('extra_init',extra_init_moves),('phase',phase_moves),('readout',readout_moves),('detector',detector_moves),('hop',hops.moves),('round',proposals)]
  for family,gen in families:
   cv=coverage[family]=dict(generated=0,build_failures=[],hashes=[])
   for c,d in gen(base):
    cv['generated']+=1
    if c is None:cv['build_failures'].append(dict(desc=d,error='infeasible retiming'));continue
    native_order_times=S.compress(c['t'])
    try:c=normalize(c)
    except Exception as e:cv['build_failures'].append(dict(desc=d,error=str(e)));continue
    sha=hashlib.sha256(textof(c).encode()).hexdigest();cv['hashes'].append(sha);d.update(parent_total=parent,local_track=True,source=base['source'])
    candidates.append((c,d));built[sha]=(c,d)
    if d.get('move')=='single' and family=='timing':timings[sha]=native_order_times
  # Fixed-order timing is exactly the same channel-signature polynomial with
  # different gap probabilities. Compile it once instead of rebuilding per move.
  if timings:
   from temporal import Cubic
   q=Cubic(base);initial=q.score(base['t']);ref=base['meta']['lns_result'];error=max(abs(initial[k]-ref[k])for k in ('second','third','total'));assert error<1e-14,error
   (OUT/(label+'.compiled_validation.json')).write_text(json.dumps(dict(source=base['source'],compiled=initial,reference=ref,error=error),indent=2));seen=records();best=parent
   with (OUT/(label+'.timing.jsonl')).open('a')as f:
    for sha,ts in timings.items():
     if sha in seen:continue
     c,d=built[sha];r=dict(desc=dict(d,source=base['source']),sha256=sha,evaluator='validated fixed-order cubic contraction',**q.score(ts))
     assert abs(r['c1'])<1e-12
     if r['exp_minus_A1']>=.505 and r['total']<best-1e-12:
      independent=score(textof(c));assert max(abs(r[k]-independent[k])for k in ('second','third','total'))<1e-14
      r.update(pruned_exact2_check=independent,stem=label+'_'+sha[:10]);save(r['stem'],textof(c),c['meta'],r);best=r['total'];report()
     f.write(json.dumps(r)+'\n');f.flush();print(json.dumps(r),flush=True)
  batch(candidates,label,a.workers);rs=records()
  # Price interactions among individually beneficial edits before choosing the
  # next center. This avoids serial passes for independent compatible moves.
  options=[];identities=set()
  eligible=[dict(rs[h],desc=built[h][1])for h in built if h in rs and rs[h].get('total',1)<parent-1e-10 and rs[h].get('exp_minus_A1',0)>=.505]
  for r in sorted(eligible,key=lambda r:r['total']):
   d=r['desc']
   if d.get('move')not in ('single','swap','reset_to_measure','check_rx','watch_before_reset','add_edge'):continue
   k=(d['move'],d.get('unit'),str(d.get('units')),str(d.get('edge')))
   if k in identities:continue
   identities.add(k);options.append(d)
   if len(options)>=12:break
  cv=coverage['compound']=dict(generated=0,build_failures=[],hashes=[]);cc=[]
  for inds in [tuple(range(n))for n in range(2,len(options)+1)]+list(itertools.combinations(range(min(10,len(options))),2)):
   d=dict(family='triple',move='combine_verified',moves=[options[i]for i in inds],parent_total=parent,local_track=True);cv['generated']+=1;c=clone(base)
   try:
    for i in inds:c=apply(c,base,options[i])
    c=normalize(c)
   except (ValueError,AssertionError,StopIteration)as e:cv['build_failures'].append(dict(desc=d,error=str(e)));continue
   sha=hashlib.sha256(textof(c).encode()).hexdigest();cv['hashes'].append(sha);cc.append((c,d));built[sha]=(c,d)
  if cc:batch(cc,label+'_compound',a.workers);rs=records()
  valid=[]
  for family,cv in coverage.items():
   hashes=set(cv['hashes']);rr=[rs[h]for h in hashes if h in rs];ok=[r for r in rr if r.get('total')is not None and r.get('exp_minus_A1',0)>=.505]
   cv.update(unique=len(hashes),measured=len(rr),missing=sorted(hashes-rs.keys()),invalid=sum('error'in r for r in rr),below_acceptance=sum(r.get('exp_minus_A1',1)<.505 for r in rr),best=min((r['total']for r in ok),default=None));valid+=ok
  winner=min(valid,key=lambda r:r['total']);improved=winner['total']<parent-1e-12
  receipt=dict(source=base['source'],source_sha256=hashlib.sha256(textof(base).encode()).hexdigest(),parent_total=parent,best_total=winner['total'],improved=improved,coverage=coverage,scope='Generated moves in moves.py, hops.py, round_lns.py; all feasible single-unit integer placements, legal commuting swaps, enumerated initialization/check/phase/readout/frame/hop variants and R-3..R+1 CP proposals. Solver timeouts and build failures remain unresolved. Pure T shifts in unchanged isotropic-idle intervals are analytically equivalent. This does not cover arbitrary circuits, routes or CP solutions.')
  (OUT/(label+'.certificate.json')).write_text(json.dumps(receipt,indent=2));print('COVERAGE',label,json.dumps({f:{k:v for k,v in c.items()if k not in ('hashes','build_failures','missing')}for f,c in coverage.items()}),flush=True)
  if not improved:print('CLOSED',label,flush=True);break
  stem=winner.get('stem')
  if not stem or not (OUT/(stem+'.qasm')).exists():
   c,d=built[winner['sha256']];winner=dict(winner,stem=label+'_'+winner['sha256'][:10]);save(winner['stem'],textof(c),c['meta'],winner);stem=winner['stem'];print(json.dumps(winner),flush=True)
  base=read(OUT/stem)
 report()
