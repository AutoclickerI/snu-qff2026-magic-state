"""Full-circuit flags from native encoder libraries and exact CX commutation.

Enumerates physical instruments, jointly schedules prefix release/A/contacts,
and prices every feasible instrument by the unmodified all-orders evaluator.
"""
from context76 import *
import argparse,itertools,gzip
p=argparse.ArgumentParser();p.add_argument('stem');p.add_argument('--out',required=True);p.add_argument('--library',default='A2');p.add_argument('--round',type=int,default=39);p.add_argument('--workers',type=int,default=2);p.add_argument('--templates',type=int,default=20);p.add_argument('--support',type=int,default=-1);p.add_argument('--window',type=int,default=1);p.add_argument('--commute-prefix',action='store_true');a=p.parse_args()
b=json.loads(Path(a.stem).with_suffix('.plan.json').read_text());A=b['meta']['A'];D=b['meta']['data_qubits'];oldR=b['meta']['R'];R=a.round
reads={};cons={};kept=[]
for o in b['ops']:
 u=unit(o);pair=S.name_qs(o['lines'][0])[1]
 if o.get('tag')=='A':continue
 if u.name=='CX' and pair in list(zip(D,A)) and o['t']==oldR:cons[pair[1]]=o;continue
 if u.name=='MEASURE' and u.qs[0]in A and o['t']>=oldR:reads[u.qs[0]]=o;continue
 kept.append(o)
assert len(cons)==len(reads)==7
bits={q:int(re.search(r'c\[(\d+)\]',o['lines'][0])[1])for q,o in reads.items()};rows=[set(map(int,re.findall(r'c\[(\d+)\]',l)))for l in b['tail']if l.startswith('// DETECTOR')]
edges=[(u,v)for u in A for v in A if abs(u//6-v//6)+abs(u%6-v%6)==1]
instruments=[];seen=set()
for ng in [1,2]:
 for gs in itertools.product(edges,repeat=ng):
  if any(gs[i]==gs[i+1]for i in range(ng-1)):continue
  dr=copy.deepcopy(rows)
  for u,v in gs:
   for row in dr:
    if bits[v]in row:row.symmetric_difference_update({bits[u]})
  flags=[q for q in A if all(bits[q]not in row for row in dr)]
  if len(flags)!=1:continue
  pull={flags[0]}
  for u,v in reversed(gs):
   if u in pull:pull.symmetric_difference_update({v})
  if len(pull)!=3:continue
  sig=(tuple(tuple(sorted(r))for r in dr),tuple(sorted(pull)))
  # Equivalent transformations can have different physical schedules: retain
  # each CX order, only discard literal duplicates.
  key=(sig,gs)
  if key in seen:continue
  seen.add(key);instruments.append((gs,dr,flags,sorted(A.index(q)for q in pull)))
if a.support>=0:instruments=[x for x in instruments if x[3]==[[0,1,2],[1,3,5]][a.support]]
previous={q:max((i for i,o in enumerate(kept)if q in unit(o).qs and o['t']<oldR),key=lambda i:kept[i]['t'],default=None)for q in A}
results=[]
for ei in range(a.templates):
 e=json.loads((OUT/f'library_{a.library}.json').read_text())[ei];enc=[tuple(z)for layer in e['ops']for z in layer];piv=set(e['pivots']);assert set(sum((list(z)for z in enc),[]))==set(A)
 for fi,(gs,dr,flags,pull)in enumerate(instruments):
  ops=copy.deepcopy(kept);m=cp_model.CpModel();ts=[];last={};movement=[]
  for i,o in enumerate(ops):
   t=m.NewIntVar(0,R if unit(o).name=='TDG'else R-1,'k'+str(i))if o['t']<oldR else m.NewConstant(R+o['t']-oldR);ts.append(t)
   for q in unit(o).qs:
    if q in last and not a.commute_prefix:m.Add(t>ts[last[q]])
    last[q]=i
   d=m.NewIntVar(0,100,'move'+str(i));m.AddAbsEquality(d,t-o['t']);movement.append(d)
   if o['t']<oldR:m.AddHint(t,min(R-1,o['t']))
  if a.commute_prefix:commuting_precedence(m,kept,ts)
  def add(lines,lo,hi,tag):
   i=len(ops);ops.append(dict(lines=lines,tag=tag));ts.append(m.NewIntVar(lo,hi,'x'+str(i)));return i
  own={q:[]for q in A};init={};contact={};measure={}
  for q in A:
   prior=previous[q];old=kept[prior]if prior is not None else None
   # Reuse only the same measured basis. Full noiseless verification still
   # checks that any source-record dependency has not been lost.
   reuse=old is not None and unit(old).name==('MX'if q in piv else'MEASURE')
   if reuse:init[q]=prior
   else:init[q]=add([f'reset q[{q}];']+([f'h q[{q}];']if q in piv else[]),0,R-1,'A')
   if prior is not None and not reuse:m.Add(ts[init[q]]>ts[prior])
  for u,v in enc:idx=add([f'cx q[{u}],q[{v}];'],max(0,R-14),R-1,'A');own[u].append(idx);own[v].append(idx)
  for i,q in enumerate(A):
   idx=add(cons[q]['lines'][:],R-a.window,R,'round');contact[q]=idx;own[q].append(idx)
   prior=max((j for j,o in enumerate(kept)if D[i]in unit(o).qs and o['t']<oldR and unit(o).name!='TDG'),key=lambda j:kept[j]['t']);m.Add(ts[idx]>ts[prior])
   for j,o in enumerate(kept):
    if D[i]in unit(o).qs and unit(o).name=='TDG':m.Add(ts[idx]!=ts[j])
  for u,v in gs:idx=add([f'cx q[{u}],q[{v}];'],R-a.window,R+1,'A_decoder');own[u].append(idx);own[v].append(idx)
  for q in A:
   lines=[f'h q[{q}];',f'measure q[{q}] -> c[{bits[q]}];',f'h q[{q}];']if q in flags else reads[q]['lines'][:]
   measure[q]=add(lines,R-a.window+1,R+2,'round')
   for idx in own[q]:m.Add(ts[idx]>ts[init[q]]);m.Add(ts[measure[q]]>ts[idx])
   m.AddNoOverlap([m.NewFixedSizeIntervalVar(ts[idx],1,f'oc{q}_{idx}')for idx in own[q]])
   for jj,idx in enumerate(own[q]):
    u,v=S.name_qs(ops[idx]['lines'][0])[1]
    for jdx in own[q][jj+1:]:
     c,d=S.name_qs(ops[jdx]['lines'][0])[1]
     if u==d or v==c:m.Add(ts[jdx]>ts[idx])
  m.Minimize(sum(movement)+100*sum(R-ts[i]for i in contact.values())+sum(ts[i]for i in measure.values()))
  assert not m.Validate(),m.Validate()
  s=cp_model.CpSolver();s.parameters.num_workers=a.workers;s.parameters.max_time_in_seconds=2;st=s.Solve(m);rec=dict(template=ei,instrument=fi,gates=gs,support=pull,status=s.StatusName(st))
  if st in(cp_model.FEASIBLE,cp_model.OPTIMAL):
   for i,o in enumerate(ops):o['t']=s.Value(ts[i])
   c=copy.deepcopy(b);c['ops']=ops;c['tail']=[l for l in b['tail']if not l.startswith('// DETECTOR')]+['// DETECTOR '+' '.join(f'c[{v}]'for v in sorted(row))for row in dr]+[f'// DETECTOR c[{bits[q]}]'for q in flags]
   comp={t:i for i,t in enumerate(sorted({o['t']for o in ops}))};c['meta']['R']=comp[R];c['meta']['A_decoder']=dict(gates=gs,flag=flags,support=pull);c['meta']['A_encoder']=dict(ops=enc,pivots=sorted(piv));name=f'{a.out}_e{ei}_f{fi}'
   try:
    stem=save(c,'p76/'+name);rec.update(rank(stem,a.workers));rec['stem']=str(stem)
    selected=[(o['t'],*S.name_qs(o['lines'][0])[1])for o in c['ops']if o.get('tag')=='A'and unit(o).name=='CX'];rec['profile']=phase_profile(selected,piv,A,pull)[0]
   except Exception as e:rec['error']=repr(e)
   append_result(name,rec,'Native library encoder/pivot and length1–3 logical-X decoder instrument, prefix/cell-release timing and commuting CX order solved together; complete all-orders rank. Fixed selected region and routes, no universal closure.')
   print(json.dumps(rec),flush=True)
  results.append(rec)
  with gzip.open(OUT/(a.out+'.records.jsonl.gz'),'at')as f:f.write(json.dumps(rec)+'\n')
 (OUT/(a.out+'.receipt.json')).write_text(json.dumps(dict(results=results,args=vars(a)),indent=1))
print('DONE',len(results),flush=True)
