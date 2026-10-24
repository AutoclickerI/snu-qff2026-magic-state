"""Measured-helper BC instrument, preserving the v23 exterior and native gates."""
from common import *
from interleave import exterior,GENS
import ft_mb,collections
def solve_support(rows,rhs):
 basis={}
 for i,v in enumerate(rows):
  mask=1<<i
  while v:
   p=v.bit_length()-1
   if p not in basis:basis[p]=(v,mask);break
   w,z=basis[p];v^=w;mask^=z
 out=0
 while rhs:
  p=rhs.bit_length()-1
  if p not in basis:raise ValueError('measurement removed independent amplitude')
  w,z=basis[p];rhs^=w;out^=z
 return out
def build(prep,name,init_policy='original',timing='project'):
 old,tail=exterior(45);ops=copy.deepcopy(old);n=100;new=[];meas=[]
 active=set(B+C)|{q for L in prep['ops']for e in L for q in e}|{q for L in prep.get('measures',[])for q in L}
 piv=prep['pivots'];vals={q:(1<<piv.index(q)if q in piv else 0)for q in active}
 def add(lines,t,tag,**kw):
  o=dict(lines=lines,t=t,tag=tag,**kw);new.append(o);return o
 original=json.loads((H/'inputs/ladder_f00.json').read_text())['units']
 oldmx={unit(o).qs[0]for o in original if o['tag']=='BC'and unit(o).name=='MX'}
 oldmz={unit(o).qs[0]for o in original if o['tag']=='BC'and unit(o).name=='MEASURE'}
 for q in sorted(active):
  if init_policy=='original'and q in piv and q in oldmx and q!=19:
   add([f'h q[{q}];',f'measure q[{q}] -> c[{n}];',f'h q[{q}];'],0,'bc_init');meas.append((n,vals[q]));n+=1
  elif init_policy=='original'and q not in piv and q in oldmz:
   add([f'measure q[{q}] -> c[{n}];'],0,'bc_init');tail.append(f'// DETECTOR c[{n}]');n+=1
  else:add([f'reset q[{q}];']+([f'h q[{q}];']if q in piv else[]),0,'bc_init')
 for t,layer in enumerate(prep['ops'],1):
  for a,b in layer:add([f'cx q[{a}],q[{b}];'],t,'bc_encoder');vals[b]^=vals[a]
  for q in prep.get('measures',[[]for _ in prep['ops']])[t-1]:
   add([f'h q[{q}];',f'measure q[{q}] -> c[{n}];'],t,'bc_midmeasure');meas.append((n,vals[q]));vals[q]=0;n+=1
   add([f'reset q[{q}];'],t+1,'bc_midreset')
 for q in sorted(active-set(B+C)):
  uses=sorted([o for o in new if q in unit(o).qs],key=lambda o:o['t'])
  if unit(uses[-1]).name in('RESET','RX'):
   # This helper was already measured and discarded; its final reset has
   # no downstream consumer. Keep the MX, delete the redundant reset.
   if len(uses)>1 and unit(uses[-2]).name=='MX':new.remove(uses[-1]);continue
   if len(uses)==1:new.remove(uses[-1]);continue
  t=max(o['t']for o in new if q in unit(o).qs)+1
  if prep.get('helper_x')and vals[q]!=0:
   add([f'h q[{q}];',f'measure q[{q}] -> c[{n}];'],t,'bc_helpermeasure');meas.append((n,vals[q]));vals[q]=0
  else:
   assert vals[q]==0
   add([f'measure q[{q}] -> c[{n}];'],t,'bc_helpermeasure');tail.append(f'// DETECTOR c[{n}]')
  n+=1
 new.sort(key=lambda o:o['t'])
 # At a shared tick MX must precede its next-tick reset. No unphysical
 # same-wire ordering can be introduced by the schedule optimization.
 rows=[vals[q]for q in B+C];zcor={i:set()for i in range(7)}
 for bit,row in meas:
  zz=solve_support(rows,row);bmask=(zz&127)^(zz>>7)
  for i in range(7):
   if bmask>>i&1:zcor[i].add(bit)
 bbits=[];cbits=[]
 for i,(b,c,d)in enumerate(zip(B,C,D)):
  ops.extend([dict(lines=[f'cx q[{b}],q[{c}];'],t=45,tag='bc_check'),dict(lines=[f'cx q[{b}],q[{d}];'],t=46,tag='bc_data')])
  cbits.append(n);ops.append(dict(lines=[f'measure q[{c}] -> c[{n}];'],t=46,tag='bc_read'));n+=1
  bbits.append(n);ops.append(dict(lines=[f'h q[{b}];',f'measure q[{b}] -> c[{n}];'],t=47,tag='bc_read'));n+=1
 for k,bs in [('b',bbits),('c',cbits)]:
  for gen in GENS+([list(range(7))]if k=='c'else[]):
   bits={bs[i]for i in gen}
   if k=='b':
    for i in gen:bits^=zcor[i]
   tail.append('// DETECTOR '+' '.join(f'c[{b}]'for b in sorted(bits)))
 # Native-time model with fixed exterior prefix, only the round can shift.
 m=cp_model.CpModel();allops=ops+new;tv=[m.NewIntVar(0,90,f't{i}')for i in range(len(allops))];R=m.NewIntVar(45,85,'R')
 for i,o in enumerate(ops):m.Add(tv[i]==o['t']+(R-45 if o['t']>=45 else 0))
 for q in range(36):
  pre=[i for i,o in enumerate(ops)if o['t']<45 and q in unit(o).qs]
  post=[i for i,o in enumerate(ops)if o['t']>=45 and q in unit(o).qs]
  middle=[len(ops)+i for i,o in enumerate(new)if q in unit(o).qs]
  seq=sorted(pre,key=lambda i:ops[i]['t'])+middle+sorted(post,key=lambda i:ops[i]['t'])
  for a,b in zip(seq,seq[1:]):m.Add(tv[b]>tv[a])
 for i,o in enumerate(new,len(ops)):
  m.Add(tv[i]<R+(1 if o['tag']=='bc_helpermeasure'else 0))
 s=cp_model.CpSolver();s.parameters.num_workers=1;s.parameters.max_time_in_seconds=20;m.Minimize(R)
 st=s.Solve(m);assert st in(cp_model.FEASIBLE,cp_model.OPTIMAL),s.StatusName(st)
 m.Add(R==s.Value(R));dev=[]
 if timing=='project':
  refs=collections.defaultdict(list)
  for o in original:
   if o['tag']=='BC':refs[tuple(o['lines'])].append(o['t'])
  used=collections.Counter()
  for i,o in enumerate(allops):
   if i<len(ops):continue
   key=tuple(o['lines']);j=used[key];used[key]+=1
   if j<len(refs[key]):
    z=m.NewIntVar(0,90,'dev');m.AddAbsEquality(z,tv[i]-refs[key][j]);dev.append(z)
 m.Maximize(-1000*sum(dev)+sum(((-1 if 'measure'in o['tag']else 1)*tv[i])for i,o in enumerate(allops)if i>=len(ops)))
 st=s.Solve(m);assert st in(cp_model.FEASIBLE,cp_model.OPTIMAL)
 for i,o in enumerate(allops):o['t']=s.Value(tv[i]);o['id']=i
 c=dict(h=['OPENQASM 2.0;','include "qelib1.inc";','qreg q[36];',f'creg c[{n}];'],ops=allops,tail=tail,meta=dict(data_qubits=D,R=s.Value(R),prep=prep,measurement_frames=[dict(bit=b,row=r,support=solve_support(rows,r))for b,r in meas],method='BC measured-helper instrument',init_policy=init_policy,timing=timing,source='MAIN/v23h_c2c9'))
 return save(c,name)
if __name__=='__main__':
 prep=json.loads(Path(sys.argv[1]).read_text());stem=build(prep,sys.argv[2],*(sys.argv[3:]));r=score(stem);append_result(stem.name,r,'Complete measured-helper instrument, independent six-amplitude frame derivation; c1 and cubic screen.');print(json.dumps(r),flush=True)
