"""Native destructive A decoders on a complete new geometry, exact priced.

Conjugate every existing detector row, expose all deterministic X flags on
columns absent from the transformed Z checks, and preserve the data tail.
"""
from common import *
import itertools,argparse,gzip
p=argparse.ArgumentParser();p.add_argument('stem');p.add_argument('--out',required=True);p.add_argument('--gates',type=int,default=2);p.add_argument('--tail-delay',type=int,default=0);p.add_argument('--commute',action='store_true');p.add_argument('--seconds',type=float,default=8);a=p.parse_args()
src=Path(a.stem);base=json.loads(src.with_suffix('.plan.json').read_text());A=base['meta']['A'];oldR=base['meta']['R'];R=oldR+a.tail_delay;edges=[(u,v)for u in A for v in A if abs(u//6-v//6)+abs(u%6-v%6)==1];reads={}
for i,o in enumerate(base['ops']):
 u=unit(o)
 if u.name=='MEASURE'and u.qs[0]in A and o['t']>=oldR:reads[u.qs[0]]=i
assert len(reads)==7
bits={q:int(re.search(r'c\[(\d+)\]',base['ops'][i]['lines'][0])[1])for q,i in reads.items()};rows=[set(map(int,re.findall(r'c\[(\d+)\]',l)))for l in base['tail']if l.startswith('// DETECTOR')];seen=set();results=[]
def build(gates,index):
 transformed=copy.deepcopy(rows)
 for u,v in gates:
  for row in transformed:
   if bits[v]in row:row.symmetric_difference_update({bits[u]})
 flags=[q for q in A if all(bits[q]not in row for row in transformed)]
 if not flags:return
 # The pulled-back X flag must be in the |+L> X stabilizer group.
 cert=[]
 for q in flags:
  support={q}
  for u,v in reversed(gates):
   if u in support:support.symmetric_difference_update({v})
  assert all(sum(A[i]in support for i in row)%2==0 for row in[[0,2,4,6],[1,2,5,6],[3,4,5,6]])
  cert.append(dict(measured=q,pullback=sorted(support)))
 key=(tuple(tuple(sorted(x))for x in transformed),tuple(flags),tuple(gates))
 if key in seen:return
 seen.add(key);c=copy.deepcopy(base);ops=c['ops'];original_count=len(ops);m=cp_model.CpModel();ts=[m.NewIntVar(max(0,o['t']-5),min(R+2,o['t']+3+a.tail_delay),'t'+str(i))for i,o in enumerate(ops)]
 for i,o in enumerate(ops):
  u=unit(o)
  pair=S.name_qs(o['lines'][0])[1]
  if o['t']>=oldR and i not in reads.values() and not(u.name=='CX'and pair[1]in A):m.Add(ts[i]==o['t']+a.tail_delay)
  if u.name=='CX'and pair in list(zip(c['meta']['data_qubits'],A))and o['t']==oldR:m.Add(ts[i]<=R)
  m.AddHint(ts[i],o['t'])
 per={q:[]for q in range(36)}
 for i,o in enumerate(ops):
  if i not in reads.values():
   for q in unit(o).qs:per[q].append(i)
 for j,(u,v)in enumerate(gates):
  i=len(ops);ops.append(dict(lines=[f'cx q[{u}],q[{v}];'],t=R+j,tag='A_decoder'));ts.append(m.NewIntVar(max(0,R-3),R+1,'decode'+str(j)))
  if j:m.Add(ts[i]>ts[i-1])
  for q in(u,v):per[q].append(i)
 for q,i in reads.items():per[q].append(i)
 for q,seq in per.items():
  if a.commute:
   m.AddNoOverlap([m.NewFixedSizeIntervalVar(ts[i],1,f'occupy{q}_{i}')for i in seq])
   for ii,i in enumerate(seq):
    for j in seq[ii+1:]:
     ui,uj=unit(ops[i]),unit(ops[j]);pi=S.name_qs(ops[i]['lines'][0])[1];pj=S.name_qs(ops[j]['lines'][0])[1]
     commutes=ui.name==uj.name=='CX'and pi[0]!=pj[1]and pi[1]!=pj[0]
     if not commutes:m.Add(ts[j]>ts[i])
  else:
   for i,j in zip(seq,seq[1:]):m.Add(ts[j]>ts[i])
 # Tie existing unit ordering only; every new CX is after its own A data contact.
 for q,i in reads.items():
  if q in flags:ops[i]['lines']=[f'h q[{q}];',f'measure q[{q}] -> c[{bits[q]}];',f'h q[{q}];']
 c['tail']=[l for l in c['tail']if not l.startswith('// DETECTOR')]+['// DETECTOR '+' '.join(f'c[{b}]'for b in sorted(row))for row in transformed]+[f'// DETECTOR c[{bits[q]}]'for q in flags]
 changes=[]
 for i,o in enumerate(ops[:original_count]):d=m.NewIntVar(0,8,'change'+str(i));m.AddAbsEquality(d,ts[i]-o['t']);changes.append(d)
 m.Minimize(sum(changes))
 s=cp_model.CpSolver();s.parameters.num_workers=1;s.parameters.max_time_in_seconds=a.seconds;st=s.Solve(m);row=dict(index=index,gates=gates,flags=cert,status=s.StatusName(st))
 if st in(cp_model.OPTIMAL,cp_model.FEASIBLE):
  for i,o in enumerate(ops):o['t']=s.Value(ts[i]);o['id']=i
  compact={t:i for i,t in enumerate(sorted({o['t']for o in ops}))};c['meta']['R']=compact[R];c['meta']['source']='ENDSTATE region2 full circuit with native A decoder';c['meta']['A_decoder']=cert;c['meta']['decoder_gates']=gates;c['meta']['source_sha256']=hashlib.sha256(src.with_suffix('.qasm').read_bytes()).hexdigest();name=a.out+f'_{index}'
  try:stem=save(c,name);row['stem']=str(stem);row.update(score(stem))
  except Exception as e:row['error']=repr(e)
  with gzip.open(H/(a.out+'.witnesses.jsonl.gz'),'at')as z:z.write(json.dumps(dict(result=row,plan=c))+'\n')
  append_result(name,row,'Native A decoder on complete ENDSTATE region2 redesign. All prior detector rows exactly conjugated; X flags certified by |+L> stabilizers. Original final data tail kept; moved earlier A contacts and preparation are included in exact score.')
 row['tail_delay']=a.tail_delay;results.append(row);print(json.dumps(row),flush=True)
for index,gates in enumerate(itertools.product(edges,repeat=a.gates)):
 if any(gates[i]==gates[i+1]for i in range(len(gates)-1)):continue
 build(gates,index)
(H/(a.out+'.receipt.json')).write_text(json.dumps(results,indent=2));print('DONE',len(results),flush=True)
