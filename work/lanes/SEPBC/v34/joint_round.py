"""Interleave D->A with unfinished A encoding using code-preserving syndrome maps.

For each input column e_i, propagate it through the A CXs after its coupling.
Require H M = N H with N in GL(3,2). Thus data codewords cannot leak into the
ancilla readout and every nonzero single-X syndrome remains distinguished.
The full unchanged ideal/noisy evaluator is still authoritative.
"""
from assemble_layers import *
from mutations import route14
import itertools,collections
def gls():
 for a,b,c in itertools.product(range(1,8),repeat=3):
  v=[(a if i&1 else 0)^(b if i&2 else 0)^(c if i&4 else 0)for i in range(1,8)]
  if len(set(v))==7 and 0 not in v:yield v
def data_ready(c):
 last={}
 for o in prefix(c):
  u=unit(o);t=max(last.get(q,-1)+1 for q in u.qs)
  for q in u.qs:last[q]=t
 return {q:last.get(q,-1)+1 for q in D}
recs=json.loads((V/'layer_recipes.json').read_text());rows=[];built=0;seen=set()
for j,rec in enumerate(recs):
 if rec['mode']%10>=3:continue # no measured-X-state reuse in this search
 base=route14(getbase(0))if rec['mode']>=10 else getbase(0);c=assemble(base,rec);dr=data_ready(base);first={q:0 for q in A}
 for o in c['ops']:
  if o.get('tag')=='encoder_a'and unit(o).name!='CX':
   for q in unit(o).qs:first[q]=max(first[q],o['t']+1)
 rr=release(base)
 for q in A:first[q]=max(first[q],rr[q]['earliest']+1)
 opts=[]
 for i,q in enumerate(A):
  choices=collections.defaultdict(list)
  for t in range(max(first[q],dr[D[i]]),44):
   if any(u==q or v==q for tt,u,v in rec['ops']if tt==t):continue
   x=1<<i
   for tt,u,v in rec['ops']:
    if tt>t and x>>A.index(u)&1:x^=1<<A.index(v)
   sig=0
   for k in range(7):
    if x>>k&1:sig^=k+1
   if sig:choices[sig].append(t)
  opts.append(choices)
 matches=[]
 for ns in gls():
  if all(ns[i]in opts[i]for i in range(7)):
   ts=[max(opts[i][ns[i]])for i in range(7)];matches.append((sum(ts),ns,ts))
 for _,ns,ts in sorted(matches,reverse=True)[:2]:
  key=(tuple(map(tuple,rec['ops'])),tuple(ts),tuple(rec['pivots']),rec['mode'])
  if key in seen:continue
  seen.add(key);d=copy.deepcopy(c);d['meta'].update(R=43,A_encoder_ready=44,syndrome_map=ns,D_A_times=ts)
  for o in d['ops']:
   if o.get('tag')=='encoder_a':o['offset']=o['t']-43
   elif o.get('tag')in('round','decoder'):
    old=o['t'];u=unit(o);t=old
    if u.name=='CX':
     pair=tuple(map(int,S.QRE.findall(o['lines'][0])))
     if pair in list(zip(D,A)):t=ts[list(zip(D,A)).index(pair)]
     elif pair in list(zip(B,C)):t=43
     elif pair in list(zip(B,D)):t=44
    # Existing decoder at44/45 and terminal outputs through46 are retained.
    o['offset']=t-43;o['t']=t
  name=f'joint_{j}_{built}_R43';f,r=fit(d,6,cut=0,phases=True);row=dict(stem=name,recipe=rec,D_A_times=ts,syndrome_map=ns,schedule=r)
  if f:
   try:st,z=write(f,name,'Joint A-encoder / D->A schedule with HM=NH, N invertible. All data couplings and BC checks at or before43; A decoder starts44. Full ideal/noisy checks retain all source detectors.');row['screen']=z
   except Exception as e:row['error']=repr(e);print(name,repr(e),flush=True)
  else:print(name,r,flush=True)
  rows.append(row);built+=1;(V/'joint_builds.json').write_text(json.dumps(rows,indent=2))
print('joint schedules found',built,'from',len(recs),'recipes',flush=True)
(V/'joint_builds.json').write_text(json.dumps(rows,indent=2))
(V/'joint_summary.json').write_text(json.dumps(dict(input_witnesses=len(recs),found=built,GL3_maps=len(list(gls())),fresh_reset_modes_only=True),indent=2))
