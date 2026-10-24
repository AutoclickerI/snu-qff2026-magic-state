import os,sys,re,json,argparse
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
ROOT=Path('/home/jihoon/competitions/quantumn');HERE=Path(__file__).parent
sys.path.insert(0,str(ROOT/'work'));sys.path.insert(0,str(ROOT/'work'/'lanes'/'DR'))
from ortools.sat.python import cp_model
import tprep.noise as tn, tprep.qasm as tq
from steane_full import GENS,PRE_DETECTORS
QRE=re.compile(r'q\[(\d+)\]')
P0={0,1,2,3,4,6,7,8,9,10,13,14,15,19,20}
def mapfun(tag):
 m=re.match(r's(\d+)_r(\d+)_c(\d+)',tag);k,tr,tc=map(int,m.groups())
 def tf(rc):
  r,c=rc
  z=[(r,c),(r,5-c),(5-r,c),(5-r,5-c),(c,r),(c,5-r),(5-c,r),(5-c,5-r)][k]
  raw=[(rr,cc) for rr,cc in [(r,c)] for _ in [0]]
  allraw=[]
  for q in P0:
   rr,cc=q//6,q%6;zz=[(rr,cc),(rr,5-cc),(5-rr,cc),(5-rr,5-cc),(cc,rr),(cc,5-rr),(5-cc,rr),(5-cc,5-rr)][k];allraw.append(zz)
  return (z[0]-min(x for x,y in allraw)+tr,z[1]-min(y for x,y in allraw)+tc)
 return lambda q: (lambda rc:rc[0]*6+rc[1])(tf((q//6,q%6)))
def prefix_steps(tag):
 mp=mapfun(tag);raw=(ROOT/'work'/'submissions'/'v11_A1i_alap45.qasm').read_text().splitlines()[:204]
 mapped=[re.sub(r'q\[(\d+)\]',lambda m:f'q[{mp(int(m.group(1)))}]' if int(m.group(1)) in P0 else m.group(0),l) for l in raw]
 head=[l for l in mapped if l.startswith(('OPENQASM','include','qreg'))]
 text='\n'.join(mapped)+'\n';stim,labels,errors=tq.convert(text);assert not errors,errors
 prog,steps,_=tn.schedule(stim);ks={}
 for ins,st in zip(prog,steps):
  lab=labels[ins.line_no-1];m=re.match(r'instruction (\d+) ',lab)
  if m and st:ks[int(m.group(1))]=st[0][1]
 stmts=[];k=0
 for line in mapped:
  s=line.split('//')[0].strip()
  if not s or s.startswith(('OPENQASM','include','qreg','creg')):continue
  k+=1
  if s.startswith('barrier'):continue
  stmts.append([s,ks.get(k)])
 for i,(s,st) in enumerate(stmts):
  if st is not None:continue
  q=QRE.findall(s)[0];nxt=next((t for t in stmts[i+1:] if QRE.findall(t[0])[:1]==[q] and t[1] is not None),None);prv=next((t for t in reversed(stmts[:i]) if QRE.findall(t[0])[:1]==[q] and t[1] is not None),None)
  if s.startswith('h') and prv and prv[0].startswith('reset'):stmts[i][1]=prv[1]
  elif nxt:stmts[i][1]=nxt[1]
  else:stmts[i][1]=prv[1]
 return head,stmts

def jobs(preps,lay,moves):
 out=[]
 def add(st,qs,tag):out.append(dict(stmts=st,qs=tuple(sorted(set(qs))),tag=tag))
 for pi,path in enumerate(moves):
  for hi,(s,d) in enumerate(zip(path,path[1:])):
   add([f'reset q[{d}];'],[d],f'm{pi}.{hi}.r');add([f'cx q[{s}],q[{d}];'],[s,d],f'm{pi}.{hi}.f');add([f'cx q[{d}],q[{s}];'],[s,d],f'm{pi}.{hi}.b')
 for key in ('a','bc'):
  p=preps[key];cells=list(lay[key]) if key=='a' else list(lay['b']+lay['c']);first={}
  for t,L in enumerate(p['ops']):
   for u,v in L:first.setdefault(u,t);first.setdefault(v,t)
  for q in cells:first.setdefault(q,0)
  for q in sorted(first,key=first.get):add([f'reset q[{q}];']+([f'h q[{q}];'] if q in p['pivots'] else []),[q],f'{key}.i.{q}')
  for t,L in enumerate(p['ops']):
   for u,v in L:add([f'cx q[{u}],q[{v}];'],[u,v],f'{key}.x.{t}.{u}.{v}')
 return out

def build(lay,A,BC,tag,seconds=180,workers=8):
 head,stmts=prefix_steps(tag);release={};by={}
 for s,st in stmts:
  by.setdefault(st,[]).append(s)
  for q in map(int,QRE.findall(s)):release[q]=max(release.get(q,0),st+1)
 js=jobs({'a':A,'bc':BC},lay,lay['moves']);m=cp_model.CpModel();N=len(js);starts=[m.NewIntVar(0,100,f's{i}') for i in range(N)];ends=[m.NewIntVar(1,101,f'e{i}') for i in range(N)];ivs=[m.NewIntervalVar(starts[i],1,ends[i],f'i{i}') for i in range(N)];byq={q:[] for q in range(36)}
 for i,j in enumerate(js):
  for q in j['qs']:byq[q].append(i);m.Add(starts[i]>=release.get(q,0))
 for q,ix in byq.items():
  if ix:
   m.AddNoOverlap([ivs[i] for i in ix])
   for a,b in zip(ix,ix[1:]):m.Add(starts[b]>=ends[a])
 d,a,b,c=lay['d'],lay['a'],lay['b'],lay['c'];R=m.NewIntVar(33,100,'R')
 for q in set(d+a+b+c):
  for i in byq[q]:m.Add(ends[i]<=R)
 m.Minimize(R);s=cp_model.CpSolver();s.parameters.max_time_in_seconds=seconds;s.parameters.num_workers=workers;st=s.Solve(m);assert st in (cp_model.OPTIMAL,cp_model.FEASIBLE),s.StatusName(st);r=s.Value(R);m.Add(R==r);m.ClearObjective();m.Maximize(sum(starts));st=s.Solve(m);assert st in (cp_model.OPTIMAL,cp_model.FEASIBLE);when=[s.Value(x) for x in starts]
 for j,t in zip(js,when):by.setdefault(t,[]).extend(j['stmts'])
 n=14;bits={};r0=[];r1=[];r2=[]
 for i in range(7):r0 += [f'cx q[{d[i]}],q[{a[i]}];',f'cx q[{b[i]}],q[{c[i]}];']
 for key,cells in (('a',a),('c',c)):
  for i,q in enumerate(cells):bits[key,i]=n;r1.append(f'measure q[{q}] -> c[{n}];');n+=1
 for i in range(7):r1.append(f'cx q[{b[i]}],q[{d[i]}];')
 for i,q in enumerate(b):bits['b',i]=n;r2 += [f'h q[{q}];',f'measure q[{q}] -> c[{n}];'];n+=1
 by.setdefault(r,[]).extend(r0);by.setdefault(r+1,[]).extend(r1);by.setdefault(r+2,[]).extend(r2)
 used=sorted({int(q) for vals in by.values() for ss in vals for q in QRE.findall(ss)});bar='barrier '+','.join(f'q[{q}]' for q in used)+';';out=head+[f'creg c[{n}];']
 for t in range(min(by),r+3):
  if t==r:out.append('// region round')
  out += by.get(t,[])+[bar]
 out=out[:-1];dets=list(PRE_DETECTORS)
 for key in 'abc':
  for S in GENS:dets.append(' '.join(f'c[{bits[key,i]}]' for i in S))
 dets.append(' '.join(f'c[{bits["c",i]}]' for i in range(7)));out += [f'// DETECTOR {x}' for x in dets]
 return '\n'.join(out)+'\n',d,r,max(release.values())
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('layout');ap.add_argument('a');ap.add_argument('bc');ap.add_argument('out');a=ap.parse_args();lay=json.loads(Path(a.layout).read_text());A=json.loads(Path(a.a).read_text());BC=json.loads(Path(a.bc).read_text());txt,d,R,pre=build(lay,A,BC,lay['pre_transform']);Path(a.out+'.qasm').write_text(txt);Path(a.out+'.json').write_text(json.dumps({'data_qubits':d,'layout':a.layout,'A':a.a,'BC':a.bc,'R':R,'pre_end':pre,'cx':txt.count('cx ')},indent=2)+'\n');print(a.out,'R',R,'pre_end',pre,'CX',txt.count('cx '))
