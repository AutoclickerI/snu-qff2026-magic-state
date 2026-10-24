"""Clean BC transplant with exact native-time preservation outside BC.
Remove old BC-init frame bits, then propagate the replacement frames afresh.
"""
import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
import re,json,collections,random
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
sys.path[:0]=[str(ROOT/'work/lanes/BCPOL'),str(ROOT/'work/lanes/EVAL')]
os.environ['XTIM_TWIRL_CACHE_DIR']=str(H/'.xtim_cache')
import schedule as S
from util import native_times
from synth import B,C,verify
from ortools.sat.python import cp_model
BITS=re.compile(r'c\[(\d+)\]')
def bit(u):return int(BITS.search(next(s for s in u.lines if s.startswith('measure')))[1])
def source(kind='policy',value=9,base='v23h_c2c9'):
 text=Path(base).with_suffix('.qasm').read_text();md=json.loads(Path(base).with_suffix('.json').read_text());head,raw,tail=S.qasm_ops(text);us=S.fold_units(raw);ts=native_times(text,us);R=md['R']
 init={q:max(i for i,u in enumerate(us) if u.qs==(q,) and ts[i]<R and u.name in ('RESET','RX','MEASURE','MX')) for q in B+C}
 rem=set(init.values())|{i for i,u in enumerate(us) if ts[i]<R and u.name=='CX' and set(u.qs)<=set(B+C) and all(i>init[q] for q in u.qs)}
 assert len(rem)==96
 if kind=='endpoint':rem|={i for i,u in enumerate(us) if ts[i]==R and u.name=='CX' and set(u.qs)<=set(B+C)}
 if kind=='c6':
  # Undo readout re-encoding before eliminating the omitted physical C bit.
  readbits={u.qs[0]:bit(u) for i,u in enumerate(us) if ts[i]>R and u.name in ('MEASURE','MX')}
  for i,u in enumerate(us):
   if ts[i]>R and u.name=='CX' and C[value] in u.qs:
    a,b=map(int,re.findall(r'q\[(\d+)\]',u.lines[0]));rem.add(i)
    for j,line in enumerate(tail):
     if line.startswith('// DETECTOR'):
      bs=set(map(int,BITS.findall(line)))
      if readbits[b] in bs:bs^={readbits[a]}
      tail[j]='// DETECTOR '+' '.join(f'c[{z}]' for z in sorted(bs))
  q=C[value];removed_bit=readbits[q]
  # Eliminate the C_i record by row reduction, retaining its orthogonal checks.
  containing=[j for j,line in enumerate(tail) if line.startswith('// DETECTOR') and removed_bit in set(map(int,BITS.findall(line)))]
  if containing:
   pivot=set(map(int,BITS.findall(tail[containing[0]])))
   for j in containing[1:]:tail[j]='// DETECTOR '+' '.join(f'c[{z}]' for z in sorted(set(map(int,BITS.findall(tail[j])))^pivot))
   tail.pop(containing[0])
  rem|={i for i,u in enumerate(us) if ts[i]>=R and q in u.qs}
 # Original random MX outcomes only appear as linear frame corrections.
 mxold={bit(us[i]) for i in init.values() if us[i].name=='MX'}
 zold={bit(us[i]) for i in init.values() if us[i].name=='MEASURE'}
 clean=[]
 for line in tail:
  if line.startswith('// DETECTOR'):
   bs=set(map(int,BITS.findall(line)))
   if bs&zold:
    assert len(bs)==1,('unexpected init detector',line)
    continue
   bs-=mxold
   assert bs,('empty detector',line)
   line='// DETECTOR '+' '.join(f'c[{b}]' for b in sorted(bs))
  else:assert not (set(map(int,BITS.findall(line)))&(mxold|zold))
  clean.append(line)
 return md,head,us,ts,clean,init,rem

def build(d,options=None):
 opt=options or {};v=verify(d);assert v['stim_target_pass'] and v['policy_pass'],v
 kind=d.get('kind','policy');value=d.get('value',9)
 md,head,old,ots,tail,oinit,rem=source(kind,value,opt.get('base','v23h_c2c9'));sourceR=md['R'];roundshift=int(opt.get('round_shift',0));R=sourceR+roundshift;piv=set(d['pivots']);cells=d['cells'];assert set(cells)==set(B+C)
 mx=set(opt.get('mx',piv));mz=set(opt.get('mz',[q for q in B+C if old[oinit[q]].name=='MEASURE']))-piv
 keep=[i for i in range(len(old)) if i not in rem];us=[old[i] for i in keep];oldts=[ots[i]+(roundshift if ots[i]>=sourceR else 0) for i in keep];cand=[];frames_init={};newdets=[]
 # A following Z measurement prevents the judge from folding a prior H+M
 # into native MX. Model those two real steps explicitly, never hide the
 # extra H noise or let barrier compression silently shift the whole circuit.
 unfold=set()
 for q in mz:
  prev=[i for i in keep if q in old[i].qs and i<oinit[q]]
  if prev and old[prev[-1]].name=='MX' and old[prev[-1]].last_is_measure:unfold.add(prev[-1])
 if unfold:
  kk=[];uu=[];tt=[]
  for i,u,t in zip(keep,us,oldts):
   if i in unfold:
    assert len(u.lines)==2
    kk.extend([i,i]);uu.extend([S.Unit([u.lines[0]],[]),S.Unit([u.lines[1]],[])]);tt.extend([t,t+1])
   else:kk.append(i);uu.append(u);tt.append(t)
  keep,us,oldts=kk,uu,tt
 retained=[]
 for q in mx&piv:
  prev=[i for i in keep if q in old[i].qs and i<oinit[q]]
  if prev and old[prev[-1]].name=='MX' and old[prev[-1]].last_is_measure:
   old[prev[-1]].lines.append(f'h q[{q}];');retained.append(q)
 nb=int(re.search(r'creg c\[(\d+)\]','\n'.join(head))[1]);init={}
 for q in cells:
  init[q]=len(us)
  if q in piv:
   if q in mx:
    lines=[f'h q[{q}];',f'measure q[{q}] -> c[{nb}];',f'h q[{q}];'];frames_init[len(us)]=(q,nb);nb+=1
   else:lines=[f'reset q[{q}];',f'h q[{q}];']
  elif q in mz:
   lines=[f'measure q[{q}] -> c[{nb}];'];newdets.append(f'// DETECTOR c[{nb}]');nb+=1
  else:lines=[f'reset q[{q}];']
  cand.append(len(us));us.append(S.Unit(lines,[]))
 for layer in d['ops']:
  for a,b in layer:cand.append(len(us));us.append(S.Unit([f'cx q[{a}],q[{b}];'],[]))
 helper_id=None;helper_z=[]
 if kind=='c6':
  helper_id=len(us);cand.append(helper_id);lines=[f'measure q[{C[value]}] -> c[{nb}];']
  if d.get('helper_x'):
   lines.insert(0,f'h q[{C[value]}];')
   vals={q:0 for q in cells}
   for j,q in enumerate(d['pivots']):vals[q]=1<<j
   for layer in d['ops']:
    for a,b in layer:vals[b]^=vals[a]
   output=[q for q in cells if q!=C[value]];equations=[]
   for j in range(len(d['pivots'])):
    row=sum(((vals[q]>>j)&1)<<k for k,q in enumerate(output));rhs=(vals[C[value]]>>j)&1
    for rr,yy,pc in equations:
     if row>>pc&1:row^=rr;rhs^=yy
    if not row:assert not rhs;continue
    pc=(row&-row).bit_length()-1;equations=[(rr^row,yy^rhs,pp) if rr>>pc&1 else (rr,yy,pp) for rr,yy,pp in equations]+[(row,rhs,pc)]
   helper_z=[output[pc] for rr,yy,pc in equations if yy]
  else:newdets.append(f'// DETECTOR c[{nb}]')
  us.append(S.Unit(lines,[]));nb+=1
 per={q:[j for j,i in enumerate(keep) if q in old[i].qs] for q in range(36)}
 for q in cells:
  orig=per[q];cp=[j for j in cand if q in us[j].qs];cut=next((k for k,j in enumerate(orig) if keep[j]>oinit[q]),len(orig));per[q]=orig[:cut]+cp+orig[cut:]
 # Optional explicit check-order experiments; no other round operations change.
 delta=int(opt.get('check_delta',0));read_early=bool(opt.get('read_early',False))
 changed={}
 if delta:
  for j,i in enumerate(keep):
   if ots[i]==sourceR and old[i].name=='CX' and tuple(map(int,re.findall(r'q\[(\d+)\]',old[i].lines[0]))) in list(zip(B,C)):
    oldts[j]+=delta;changed[i]=oldts[j]
   elif ots[i]>sourceR and (set(old[i].qs)<=set(C) or 17 in old[i].qs and 16 in old[i].qs):
    if delta>0 or read_early:oldts[j]+=delta;changed[i]=oldts[j]
   elif delta>0 and ots[i]==sourceR+2 and old[i].name=='MX' and old[i].qs[0] in B:
    oldts[j]+=delta;changed[i]=oldts[j]
  if delta>0:
   # Preserve A's c19 read after its C-controlled correction.
   for j,i in enumerate(keep):
    if old[i].name=='MEASURE' and bit(old[i])==19:oldts[j]+=delta;changed[i]=oldts[j]
 m=cp_model.CpModel();tv=[m.NewIntVar(0,70,f't{i}') for i in range(len(us))];keepdev=[]
 window=int(opt.get('retime_window',0))
 for j,t in enumerate(oldts):
  if window and ots[keep[j]]<sourceR:
   m.Add(tv[j]>=max(0,t-window));m.Add(tv[j]<=min(R-1,t+window));z=m.NewIntVar(0,70,'keepdev');m.AddAbsEquality(z,tv[j]-t);keepdev.append(z)
  else:m.Add(tv[j]==t)
 # Check can be after B->data only in the explicit check-order experiment.
 if delta>0:
  for q in B:
   seq=per[q];nkeep=[j for j in seq if j<len(keep)];nprep=[j for j in seq if j>=len(keep)]
   pre=[j for j in nkeep if ots[keep[j]]<sourceR];post=sorted([j for j in nkeep if ots[keep[j]]>=sourceR],key=lambda j:(oldts[j],j));per[q]=pre+nprep+post
 for seq in per.values():
  for a,b in zip(seq,seq[1:]):m.Add(tv[b]>tv[a])
 for j in cand:m.Add(tv[j]<R+min(delta,0)+(1 if kind=='endpoint' or j==helper_id else 0))
 if kind=='c6' and d.get('helper_x'):m.Add(tv[helper_id]==R)
 for q,t in opt.get('fixed_init',{}).items():m.Add(tv[init[int(q)]]==int(t))
 policy=opt.get('timing','alap');rng=random.Random(opt.get('timing_seed',0));dev=[]
 if policy=='project':
  refs=collections.defaultdict(list)
  for i in sorted(rem):refs[tuple(old[i].lines)].append(ots[i])
  used=collections.Counter()
  for j in cand:
   key=tuple(us[j].lines);k=used[key];used[key]+=1
   if k<len(refs[key]):
    z=m.NewIntVar(0,70,'dev');m.AddAbsEquality(z,tv[j]-refs[key][k]);dev.append(z)
  m.Minimize(1000000*sum(keepdev)+10000*sum(dev)-sum(tv[j] for j in cand))
 elif policy=='asap':m.Minimize(1000000*sum(keepdev)+sum(tv[j] for j in cand))
 elif policy=='random':m.Minimize(1000000*sum(keepdev)+sum(rng.choice([-7,-3,-1,1,3,7])*tv[j] for j in cand))
 elif policy=='deadline':
  deadline=int(opt.get('deadline',44))
  for j in cand:m.Add(tv[j]<=deadline)
  m.Maximize(sum(tv[j] for j in cand)-1000000*sum(keepdev))
 else:m.Maximize(sum(tv[j] for j in cand)-1000000*sum(keepdev))
 solver=cp_model.CpSolver();solver.parameters.num_search_workers=1;solver.parameters.max_time_in_seconds=10;solver.parameters.random_seed=opt.get('timing_seed',0)
 st=solver.Solve(m)
 if st not in (cp_model.OPTIMAL,cp_model.FEASIBLE):raise ValueError('SCHEDULE_'+solver.StatusName(st))
 ts=[solver.Value(z) for z in tv]
 for j,i in enumerate(keep):
  if ts[j]!=ots[i]:changed[i]=ts[j]
 frames={q:[set(),set()] for q in range(36)};corr={}
 for i in sorted(range(len(us)),key=lambda j:(ts[j],j)):
  u=us[i]
  if i in frames_init:
   q,b=frames_init[i];frames[q]=[set(),{b}];continue
  if u.name in ('RESET','RX'):frames[u.qs[0]]=[set(),set()]
  elif u.name=='CX':
   a,b=map(int,re.findall(r'q\[(\d+)\]',u.lines[0]));frames[b][0]^=frames[a][0];frames[a][1]^=frames[b][1]
  elif u.name in ('MX','MEASURE'):
   corr[bit(u)]=frames[u.qs[0]][u.name=='MX'].copy()
   if i==helper_id and d.get('helper_x'):
    correction={bit(u)}^corr[bit(u)]
    zs=set(helper_z)
    for j in sorted(range(len(us)),key=lambda j:(ts[j],j)):
     if (ts[j],j)>=(ts[i],i):break
     if ts[j]>=R and us[j].name=='CX':
      a,b=map(int,re.findall(r'q\[(\d+)\]',us[j].lines[0]))
      if b in zs:zs.symmetric_difference_update([a])
    for q in zs:frames[q][1]^=correction
  elif u.name=='H':frames[u.qs[0]].reverse()
  elif any(any(frames[q]) for q in u.qs):raise AssertionError(('nonClifford frame',u.lines))
 assert all(not any(frames[q]) for q in md['data_qubits'])
 ntail=[]
 for line in tail+newdets:
  if line.startswith('// DETECTOR'):
   bs=set(map(int,BITS.findall(line)));ex=set()
   for b in bs:ex^=corr.get(b,set())
   line='// DETECTOR '+' '.join(f'c[{b}]' for b in sorted(bs^ex))
  ntail.append(line)
 head=[re.sub(r'creg c\[\d+\]',f'creg c[{nb}]',s) for s in head]
 text=S.emit(head,us,ts,ntail);_,rr,_=S.qasm_ops(text);nu=S.fold_units(rr);nt=native_times(text,nu);order=sorted(range(len(us)),key=lambda i:(ts[i],i))
 assert [us[i].lines for i in order]==[u.lines for u in nu],'native fold changed'
 assert [ts[i] for i in order]==nt,('native timing mismatch',[(ts[i],t) for i,t in zip(order,nt) if ts[i]!=t])
 md['init_times']={q:ts[i] for q,i in init.items()}
 md.update(source=opt.get('base','v23h_c2c9'),method='BCPOL contract transplant',R=R,prep=d,verification=v,options=opt,CX=sum(u.name=='CX' for u in nu),native_depth=max(nt)+1,non_BC_time_changes=changed,retained_previous_X_states=retained,unfolded_previous_MX=sorted(unfold))
 return text,md

if __name__=='__main__':
 d=json.loads((H/'inputs/fb_s401_0035.prep.json').read_text());text,md=build(d,dict(timing='project'));out=H/'inputs/replay';out.with_suffix('.qasm').write_text(text);out.with_suffix('.json').write_text(json.dumps(md,indent=2));print('built',md['CX'],md['native_depth'])
