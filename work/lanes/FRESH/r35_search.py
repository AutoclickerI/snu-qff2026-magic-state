from round35 import *

def sx_signs():
 ops,dets,md=load(D/'sx_full');data=md['data_qubits'];results=[]
 for early in (True,False):
  for mask in range(128):
   # Signed transversal sqrt-X differs by a code-preserving X word.
   if any((mask & sum(1<<i for i in row)).bit_count()%2 for row in f.SUPPORTS):continue
   oo=copy.deepcopy(ops)
   for o in oo:
    if o.kind not in ('SX','SXDG'):continue
    if mask>>data.index(o.qs[0])&1:o.kind={'SX':'SXDG','SXDG':'SX'}[o.kind]
    if early and o.time==46 and o.qs[0] in (10,21):o.time=44
   stem=emit(f'sx_sign_{mask:03}_{int(early)}',oo,copy.deepcopy(dets),md,dict(sign_mask=mask,early_output=early))
   r=dict(stem=stem.name)
   try:
    r['ideal']=certify(stem,singles=False);r['speed']=speed(stem,5000)
   except Exception as e:r['error']=repr(e)
   results.append(r);(D/'sx_sign_results.json').write_text(json.dumps(results,indent=2))
   print(json.dumps({k:v for k,v in r.items() if k!='ideal'}),flush=True)


def timing(procs=7,passes=1):
 ops,dets,md=load(BASE)
 base=emit('timing_base',ops,dets,md,dict(kind='control'))
 certify(base);r=price(base,procs);best=r['loss'];acc=r['acceptance'];moves=[];results=[]
 # Move each operation within its full per-wire slack, preserving logical wire order.
 for pas in range(passes):
  improvements=0
  # Late schedule first: closest connection to conditional loss, then full prefix.
  indices=sorted(range(len(ops)),key=lambda i:(-ops[i].time,-len(ops[i].qs),i))
  for i in indices:
   o=ops[i];prior=[p.time for p in ops[:i] if set(o.qs)&set(p.qs)];later=[p.time for p in ops[i+1:] if set(o.qs)&set(p.qs)]
   lo=max(prior,default=-1)+1;hi=min(later,default=47)-1
   ts=sorted(set(range(lo,hi+1))-{o.time},key=lambda t:(abs(t-o.time),t))
   oldtime=o.time;best_time=oldtime;best_r=None;best_stem=None
   for at in ts:
    oo=copy.deepcopy(ops);oo[i].time=at
    name=f'timing_p{pas}_i{i:03}_t{at:02}';stem=emit(name,oo,copy.deepcopy(dets),md,dict(moves=moves+[dict(index=i,kind=o.kind,qubits=o.qs,old=oldtime,new=at)]))
    rr=dict(stem=name,index=i,kind=o.kind,qubits=o.qs,old=oldtime,new=at)
    try:
     certify(stem,singles=False);rr.update(price(stem,procs))
     if rr['acceptance']>=.5005 and rr['loss']<best-1e-12:
      best=rr['loss'];best_time=at;best_r=rr;best_stem=stem
    except Exception as ex:rr.update(error=repr(ex),trace=traceback.format_exc())
    with (D/'timing_results.jsonl').open('a') as log:log.write(json.dumps(rr)+'\n')
    print(json.dumps(rr),flush=True)
   if best_time!=oldtime:
    moves.append(dict(index=i,kind=o.kind,qubits=o.qs,old=oldtime,new=best_time));o.time=best_time;improvements+=1
    target=emit('timing_best',ops,dets,md,dict(moves=moves));acc=best_r['acceptance']
    Path(str(target)+'.allorders.json').write_text(Path(str(best_stem)+'.allorders.json').read_text())
    (D/'timing_incumbent.json').write_text(json.dumps(dict(loss=best,acceptance=acc,moves=moves,source=str(best_stem)),indent=2))
    print('IMPROVED',best,acc,moves[-1],flush=True)
  if not improvements:break
 print('DONE',best,acc,moves,flush=True)

if __name__=='__main__':
 if sys.argv[1]=='signs':sx_signs()
 elif sys.argv[1]=='timing':timing(int(sys.argv[2]) if len(sys.argv)>2 else 7)
