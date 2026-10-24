"""Restore acceptance only along exact-score ties, then close coordinate timing."""
from temporal import *
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('stem');ap.add_argument('--label',default='clean_timing');a=ap.parse_args();base=read(a.stem);q=Cubic(base);ts=base['t'][:];initial=q.score(ts);cur=initial;pred,succ=S.build_dag(base['u']);trace=[];seen=set();rounds=0
 while True:
  changed=False;tested=0
  for i,u in enumerate(base['u']):
   if u.name in ('T','TDG')and pred[i]and succ[i]and ts.count(ts[i])>1:continue
   lo=max((ts[j]+1 for j in pred[i]),default=0);hi=min((ts[j]-1 for j in succ[i]),default=max(ts));winner=None;best=cur
   for t in range(lo,hi+1):
    if t==ts[i]:continue
    nt=ts[:];nt[i]=t;nt=S.compress(nt);key=tuple(nt)
    if key in seen:continue
    seen.add(key);tested+=1;v=q.score(nt)
    if v['exp_minus_A1']<.505:continue
    strict=v['total']<best['total']-1e-12
    equal=abs(v['total']-best['total'])<=1e-14 and v['exp_minus_A1']>best['exp_minus_A1']+1e-8
    if strict or equal:best=v;winner=nt
   if winner is not None:
    trace.append(dict(unit=i,old=ts[i],new=winner[i],score=best));ts=winner;cur=best;changed=True
  rounds+=1;print('round',rounds,'tested',tested,'score',cur,flush=True)
  if not changed:break
 c=clone(base);c['t']=ts;c=normalize(c);ref=score(textof(c));err=max(abs(cur[k]-ref[k])for k in ['second','third','total']);assert err<1e-14,(cur,ref)
 row=dict(desc=dict(family='timing',move='coordinate_exact_and_ties',source=a.stem,parent_total=initial['total'],rounds=rounds,unique=len(seen)),**ref,stem=a.label+'_best');save(row['stem'],textof(c),c['meta'],row)
 (OUT/(a.label+'.jsonl')).write_text(json.dumps(row)+'\n');(OUT/(a.label+'.certificate.json')).write_text(json.dumps(dict(base=a.stem,initial=initial,final=ref,rounds=rounds,tested=len(seen),moves=trace,error=err,scope='Every feasible integer single-unit timing with fixed per-wire order, same maximum step, acceptance estimate >=0.505; strict improvements >1e-12. Pure T idle relocation is analytically equivalent and skipped. Acceptance is used only on score ties within1e-14.'),indent=2));report();print('DONE',row,flush=True)
