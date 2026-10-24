"""Close the early data waits: one CX identity and maximal disjoint identities."""
from v35_build import *
jobs=[];windows=[];seen=set()
def put(name,c,desc):
 r=emit(name,c,desc);r['procs']=4;jobs.append(r)
def fill(c,q,h,first,last,n):
 for t in range(first,first+2*n):add(c,'CX',[q,h],t)
 return c
paths=list((d,q,a,z)for d,pp in PATHS.items()for q,a,z in pp)+[(None,10,20,27)]
for logical,q,a,z in paths:
 for h in adjacent(q):
  if h in DATA:continue
  available=[t for t in range(max(18,a),min(43,z)+1)if not any(o['t']==t and(q in o['qs']or h in o['qs'])for o in BASE['ops'])and not any(cell==h and x<=t<=y for pp in PATHS.values()for cell,x,y in pp)]
  chunks=[]
  for t in available:
   if chunks and chunks[-1][-1]==t-1:chunks[-1].append(t)
   else:chunks.append([t])
  for cc in chunks:
   if len(cc)<2 or cc[0]>=30 or not any(h in o['qs']and o['t']<cc[0]for o in BASE['ops']):continue
   lo,hi=cc[0],cc[-1];key=(q,h,lo,hi)
   if key in seen:continue
   seen.add(key);record=dict(logical=logical,q=q,h=h,window=[lo,hi],cases=[])
   for n in sorted({1,len(cc)//2}):
    # All placements of the same count within this uninterrupted joint idle
    # window are identical Pauli channels. Reuse an existing one-pair price.
    existing=[]
    if n==1:
     for t in range(lo,hi):
      p=V/f'live_X_q{q}_h{h}_{t}_{t+1}.score.json'
      if p.exists():existing.append(p)
    if existing:
     record['cases'].append(dict(pairs=n,reused=existing[0].name,reason='Same joint idle interval; isotropic CX-pair channel commutes with the remaining Pauli idle channels.'));continue
    name=f'early_q{q}_h{h}_{lo}_{hi}_n{n}'
    put(name,fill(clone(),q,h,lo,hi,n),dict(family='early_wait_identity_pairs',q=q,h=h,logical=logical,window=[lo,hi],pairs=n))
    record['cases'].append(dict(pairs=n,stem=name))
   windows.append(record)
c=clone();allpairs=[]
for g in GUARDS:
 lo,hi=g['first']+1,g['last']-1;n=(hi-lo+1)//2
 if n:
  fill(c,g['q'],g['h'],lo,hi,n);allpairs.append(dict(q=g['q'],h=g['h'],first=lo,pairs=n))
put('early_fill_existing_guards',c,dict(family='combination',ingredients=allpairs))
(V/'early_jobs.json').write_text(json.dumps(jobs,indent=2));(V/'early_windows.json').write_text(json.dumps(windows,indent=2));print('EARLY',len(jobs),'WINDOWS',len(windows))
