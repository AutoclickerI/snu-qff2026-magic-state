"""Replace only B+C prep units; preserve v20 timing outside the replacement."""
import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import argparse,collections,json,re
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path[:0]=[str(HERE),str(ROOT/'work/lanes/EVAL')]
import schedule as S
from util import native_times
from ortools.sat.python import cp_model
sys.path.insert(0,str(HERE))
from synth import B,C,verify

def source():
 text=(HERE/'inputs/v20.qasm').read_text();meta=json.loads((HERE/'inputs/v20.json').read_text());head,raw,tail=S.qasm_ops(text);old=S.fold_units(raw);ots=native_times(text,old)
 init={q:max(i for i,u in enumerate(old) if u.qs==(q,) and ots[i]<45 and u.name in ('RESET','RX','MEASURE')) for q in B+C}
 rem=set(init.values())
 for i,u in enumerate(old):
  if ots[i]<45 and u.name=='CX' and set(u.qs)<=set(B+C) and all(i>init[q] for q in u.qs):rem.add(i)
 assert len(rem)==96,(len(rem),init)
 return meta,head,old,ots,tail,init,rem

def build(prep,out,mode='project',mx=(),reuse=()):
 v=verify(prep);assert v['stim_target_pass'] and v['clean_pass'],v
 meta,head,old,ots,tail,oinit,rem=source();cells=prep.get('cells',B+C);piv=set(prep['pivots']);helpers=[q for q in cells if q not in B+C]
 keep=[i for i in range(len(old)) if i not in rem];us=[old[i] for i in keep];timesold=[ots[i] for i in keep]
 for q in set(mx)|set(reuse):
  prev=[i for i in keep if q in old[i].qs and i<oinit[q]]
  if prev and old[prev[-1]].name=='MX' and old[prev[-1]].lines[-1].startswith('measure'):
   old[prev[-1]].lines.append(f'h q[{q}];')
 nbits=int(re.search(r'creg c\[(\d+)\]', '\n'.join(head)).group(1));newdets=[];init={};cand=[];mxids={}
 removed_bits={int(re.search(r'c\[(\d+)\]',old[i].lines[0]).group(1)) for i in oinit.values() if old[i].name=='MEASURE'}
 tail=[s for s in tail if not(s.startswith('// DETECTOR') and set(map(int,re.findall(r'c\[(\d+)\]',s))) & removed_bits)]
 for q in cells:
  i=len(us);init[q]=i
  if q in reuse:
   prev=[i for i in keep if q in old[i].qs and i<oinit[q]]
   assert prev and old[prev[-1]].name==('MX' if q in piv else 'MEASURE'),('reuse basis',q,piv)
   bit=int(re.search(r'c\[(\d+)\]',next(l for l in old[prev[-1]].lines if l.startswith('measure'))).group(1))
   assert f'// DETECTOR c[{bit}]' in tail,('reuse needs existing zero postselection',q,bit)
   continue
  if q in mx and q in piv:
   lines=[f'h q[{q}];',f'measure q[{q}] -> c[{nbits}];',f'h q[{q}];'];mxids[i]=nbits;nbits+=1
  elif q in piv:lines=[f'reset q[{q}];',f'h q[{q}];']
  elif q in oinit and old[oinit[q]].name=='MEASURE':
   lines=old[oinit[q]].lines;bit=int(re.search(r'c\[(\d+)\]',lines[0]).group(1));newdets.append(f'// DETECTOR c[{bit}]')
  elif q not in {x for i in keep for x in old[i].qs}:
   lines=[f'measure q[{q}] -> c[{nbits}];'];newdets.append(f'// DETECTOR c[{nbits}]');nbits+=1
  else:lines=[f'reset q[{q}];']
  us.append(S.Unit(lines,[]));cand.append(i)
 for lay in prep['ops']:
  for u,vv in lay: cand.append(len(us));us.append(S.Unit([f'cx q[{u}],q[{vv}];'],[]))
 helperids={}
 if prep.get('helper_x'):
  for q in helpers:
   helperids[q]=(len(us),nbits);cand.append(len(us));us.append(S.Unit([f'h q[{q}];',f'measure q[{q}] -> c[{nbits}];'],[]));nbits+=1
 # Reset-style helpers must also be read, avoiding exposed helper tails.
 else:
  for q in helpers:
   cand.append(len(us));us.append(S.Unit([f'measure q[{q}] -> c[{nbits}];'],[]));newdets.append(f'// DETECTOR c[{nbits}]');nbits+=1
 per={q:[j for j,i in enumerate(keep) if q in old[i].qs] for q in range(36)}
 for q in cells:
  orig=per[q];cp=[j for j in cand if q in us[j].qs]
  if q in oinit:
   cut=next((k for k,j in enumerate(orig) if keep[j]>oinit[q]),len(orig));per[q]=orig[:cut]+cp+orig[cut:]
  else:
   assert not orig,('helper with conflicting lifetime',q,orig)
   per[q]=cp
 m=cp_model.CpModel();tv=[m.new_int_var(0,100,f't{i}') for i in range(len(us))];shift=m.new_int_var(0,40,'shift')
 early=[]
 for j,i in enumerate(keep):
  if mode=='release_alap' and old[i].last_is_measure and len(old[i].qs)==1 and old[i].qs[0] in oinit and i<oinit[old[i].qs[0]]:
   m.add(tv[j]<=ots[i]);early.append(j)
  else:m.add(tv[j]==ots[i]+(shift if ots[i]>=45 else 0))
 for q,seq in per.items():
  for x,y in zip(seq,seq[1:]):m.add(tv[y]>tv[x])
 for q in helpers:
  for j in cand:
   if q in us[j].qs:m.add(tv[j]<45+shift)
 m.minimize(shift);s=cp_model.CpSolver();s.parameters.num_search_workers=1;s.parameters.max_time_in_seconds=20
 status=s.solve(m);assert status in (cp_model.FEASIBLE,cp_model.OPTIMAL),s.status_name(status)
 sh=s.value(shift);m.add(shift==sh)
 # Match operations by per-edge occurrence to retain TREP2's measured timing.
 refs=collections.defaultdict(list)
 for i in sorted(rem):refs[tuple(old[i].lines)].append(ots[i])
 used=collections.Counter();dev=[]
 for j in cand:
  key=tuple(us[j].lines);k=used[key];used[key]+=1
  if mode=='project' and k<len(refs[key]):
   z=m.new_int_var(0,100,'deviation');m.add_abs_equality(z,tv[j]-refs[key][k]);dev.append(z)
 m.minimize(10000*sum(dev)-sum(tv[j] for j in cand)+100*sum(tv[j] for j in early));status=s.solve(m);assert status in (cp_model.FEASIBLE,cp_model.OPTIMAL)
 times=[s.value(z) for z in tv]
 # Native MX initialization leaves a random sign tracked through Clifford gates.
 frames={q:[set(),set()] for q in range(36)};corr={}
 for i in sorted(range(len(us)),key=lambda j:(times[j],j)):
  u=us[i]
  if i in mxids:frames[u.qs[0]]=[set(),{mxids[i]}];continue
  if u.name in ('RESET','RX'):frames[u.qs[0]]=[set(),set()]
  elif u.name=='CX':
   a,b=map(int,re.findall(r'q\[(\d+)\]',u.lines[0]));frames[b][0]^=frames[a][0];frames[a][1]^=frames[b][1]
  elif u.name in ('MX','MEASURE'):
   bit=int(re.search(r'c\[(\d+)\]',next(l for l in u.lines if l.startswith('measure'))).group(1));corr[bit]=frames[u.qs[0]][u.name=='MX'].copy()
  elif u.name=='H':frames[u.qs[0]].reverse()
  elif any(any(frames[q]) for q in u.qs):raise AssertionError(('non-Clifford frame',u.lines))
 assert all(not any(frames[q]) for q in meta['data_qubits'])
 if mxids:
  newtail=[]
  for line in tail:
   if line.startswith('// DETECTOR'):
    bits=set(map(int,re.findall(r'c\[(\d+)\]',line)));ex=set()
    for b in bits:ex^=corr.get(b,set())
    line='// DETECTOR '+' '.join(f'c[{b}]' for b in sorted(bits^ex))
   newtail.append(line)
  tail=newtail
 # Projecting helper X outcomes induces a known Z Pauli on B/C. Derive it
 # from the six propagated columns and fold into subsequent B X readouts.
 if helperids:
  val={q:0 for q in cells}
  for j,q in enumerate(prep['pivots']):val[q]=1<<j
  for lay in prep['ops']:
   for u,vv in lay:val[vv]^=val[u]
  for h,(_,bit) in helperids.items():
   # Solve six linear equations for a Z support on B+C.
   eq=[(sum(((val[q]>>j)&1)<<k for k,q in enumerate(B+C)),(val[h]>>j)&1) for j in range(6)];pivs=[]
   for r,y in eq:
    for pr,py,pc in pivs:
     if r>>pc&1:r^=pr;y^=py
    if not r:assert not y;continue
    pc=(r&-r).bit_length()-1
    pivs=[(pr^r,py^y,pcc) if pr>>pc&1 else (pr,py,pcc) for pr,py,pcc in pivs]+[(r,y,pc)]
   z=sum(1<<pc for r,y,pc in pivs if y);zb=(z&127)^(z>>7)
   for i,line in enumerate(tail):
    bits=set(map(int,re.findall(r'c\[(\d+)\]',line)))
    if line.startswith('// DETECTOR') and sum((28+j in bits) for j in range(7) if zb>>j&1)%2:tail[i]+=' c['+str(bit)+']'
 for i,line in enumerate(head):
  if line.startswith('creg'):head[i]=f'creg c[{nbits}];'
 text=S.emit(head,us,times,tail+newdets)
 hh,rr,tt=S.qasm_ops(text);nu=S.fold_units(rr);nt=native_times(text,nu)
 nativeR=next(t for u,t in zip(nu,nt) if u.lines==['cx q[0],q[1];'] and t>=40)
 order=sorted(range(len(us)),key=lambda i:(times[i],i));assert [us[i].lines for i in order]==[u.lines for u in nu], 'native fold changed'
 out=Path(out);out.with_suffix('.qasm').write_text(text);out.with_suffix('.json').write_text(json.dumps(dict(data_qubits=meta['data_qubits'],R=nativeR,CX=sum(u.name=='CX' for u in nu),mode=mode,mx=list(mx),reuse=list(reuse),prep=prep,verification=v),indent=2))
 return dict(R=nativeR,CX=sum(u.name=='CX' for u in nu),units=len(nu),shift=sh)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('prep');p.add_argument('out');p.add_argument('--mode',choices=['project','alap','release_alap'],default='project');p.add_argument('--mx',default='');p.add_argument('--reuse',default='');a=p.parse_args();d=json.loads(Path(a.prep).read_text());print(build(d,a.out,a.mode,[int(q) for q in a.mx.split(',') if q],[int(q) for q in a.reuse.split(',') if q]))
