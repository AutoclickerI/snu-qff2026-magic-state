import os,sys,re,json,argparse
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from ortools.sat.python import cp_model
ROOT=Path('/home/jihoon/competitions/quantumn'); HERE=Path(__file__).resolve().parent
QRE=re.compile(r'q\[(\d+)\]')
P0={0,1,2,3,4,6,7,8,9,10,13,14,15,19,20}; PRE_D=[0,20,7,4,3,15,8]
GENS=[[0,2,4,6],[1,2,5,6],[3,4,5,6]]

def transform(k,tr,tc):
 def f(q):
  r,c=divmod(q,6);return [(r,c),(r,5-c),(5-r,c),(5-r,5-c),(c,r),(c,5-r),(5-c,r),(5-c,5-r)][k]
 raw=[f(q) for q in P0];mr=min(r for r,c in raw);mc=min(c for r,c in raw)
 def mp(q):r,c=f(q);return (r-mr+tr)*6+c-mc+tc
 return mp

def prefix_v16e(tag, source=None):
 k,tr,tc=map(int,re.match(r's(\d+)_r(\d+)_c(\d+)',tag).groups());mp=transform(k,tr,tc)
 src=Path(source or (ROOT/'work/candidates/v16_bc2m.qasm')).read_text().splitlines(); groups={}; t=0; det=[]; head=[]; inhead=True
 for line in src:
  if line.startswith('barrier'):
   t+=1; continue
  if line.startswith('// DETECTOR'):
   # v16's post-prefix detector lines reference suffix records that this
   # builder replaces; retain only the 14 deterministic pre-stage records.
   bits0=[int(x) for x in re.findall(r'c\[(\d+)\]',line)]
   if bits0 and max(bits0)<14: det.append(line)
   continue
  if inhead and line.startswith(('OPENQASM','include','qreg','creg')): head.append(line); continue
  if t>32: continue
  if not line.strip() or line.startswith('//'): continue
  # map only physical prefix qubits; qreg/creg headers were already copied.
  line=QRE.sub(lambda m:f'q[{mp(int(m.group(1)))}]',line)
  groups.setdefault(t,[]).append(line)
 # Move early released prefix records: original q19 c3 at t32 -> t15; q13 h/c6 -> t19.
 for t0, q0, bit in ([(32,19,3),(32,13,6)] if source is None else []):
  old=f'q[{mp(q0)}]'; take=[]
  for line in groups[t0][:]:
   if old in line and (line.startswith('measure') or (q0==13 and line.startswith('h '))): take.append(line);groups[t0].remove(line)
  if not take: raise RuntimeError((tag,q0,groups[t0]))
  target=15 if q0==19 else 19;groups.setdefault(target,[])[0:0]=take
 # Emit the same native 33 prefix steps, but release those two cells after their measurements.
 out=head
 for st in range(33):
  out += groups.get(st,[])
  used=list(range(36))
  if st>=15: used.remove(mp(19))
  if st>=19: used.remove(mp(13))
  out.append('barrier '+','.join(f'q[{q}]' for q in used)+';')
 return out, det, mp

def jobs(lay,A,BC):
 out=[]
 def add(st,qs,tag):out.append(dict(stmts=st,qs=tuple(sorted(set(qs))),tag=tag))
 # Data paths are ordinary two-CX hops; all paths include initial endpoint.
 for pi,path in enumerate(lay['moves']):
  for hi,(s,d) in enumerate(zip(path,path[1:])):
   add([f'reset q[{d}];'],[d],f'm{pi}.{hi}.r');add([f'cx q[{s}],q[{d}];'],[s,d],f'm{pi}.{hi}.f');add([f'cx q[{d}],q[{s}];'],[s,d],f'm{pi}.{hi}.b')
 for key,p,cells in [('a',A,list(lay['a'])),('bc',BC,list(lay['b']+lay['c']))]:
  first={}
  for ti,L in enumerate(p['ops']):
   for u,v in L:first.setdefault(u,ti);first.setdefault(v,ti)
  for q in cells:first.setdefault(q,0)
  for q in sorted(first,key=first.get):add([f'reset q[{q}];']+([f'h q[{q}];'] if q in p['pivots'] else []),[q],f'{key}.i.{q}')
  for ti,L in enumerate(p['ops']):
   for u,v in L:add([f'cx q[{u}],q[{v}];'],[u,v],f'{key}.x.{ti}.{u}.{v}')
 return out

def build(lay,A,BC,tag,source=None):
 head,pre_det,mp=prefix_v16e(tag,source);release={};by={}
 # first 33 groups can be reconstructed from barriers in head/pre output.
 t=0
 for line in head:
  if line.startswith('barrier'): t+=1; continue
 # prefix_v16e returns lines with barriers, so collect operations and release time.
 t=0
 for line in head:
  if line.startswith('barrier'):t+=1;continue
  if line.startswith(('OPENQASM','include','qreg','creg')):continue
  by.setdefault(t,[]).append(line)
  for q in map(int,QRE.findall(line)):release[q]=max(release.get(q,0),t+1)
 js=jobs(lay,A,BC);m=cp_model.CpModel();starts=[m.NewIntVar(0,100,f's{i}') for i in range(len(js))];ends=[m.NewIntVar(1,101,f'e{i}') for i in range(len(js))];ivs=[m.NewIntervalVar(starts[i],1,ends[i],f'i{i}') for i in range(len(js))];byq={q:[] for q in range(36)}
 for i,j in enumerate(js):
  for q in j['qs']:byq[q].append(i);m.Add(starts[i]>=release.get(q,0))
 for q,ix in byq.items():
  if ix:
   m.AddNoOverlap([ivs[i] for i in ix])
   for i,j in zip(ix,ix[1:]): m.Add(starts[j]>=ends[i])
 # all prep/move jobs must finish before round; maximize their starts after minimizing R.
 R=m.NewIntVar(33,100,'R')
 for q,ix in byq.items():
  for i in ix:m.Add(ends[i]<=R)
 m.Minimize(R);s=cp_model.CpSolver();s.parameters.max_time_in_seconds=120;s.parameters.num_workers=8;s.parameters.random_seed=0;st=s.Solve(m);assert st in (cp_model.OPTIMAL,cp_model.FEASIBLE),s.StatusName(st);r=s.Value(R)
 m.Add(R==r);m.ClearObjective();m.Maximize(sum(starts));st=s.Solve(m);assert st in (cp_model.OPTIMAL,cp_model.FEASIBLE);when=[s.Value(x) for x in starts]
 for j,t0 in zip(js,when):by.setdefault(t0,[]).extend(j['stmts'])
 d=lay['d'];a=lay['a'];b=lay['b'];c=lay['c'];n=47;bits={};
 # Star round: A read in Z and C check in Z at R+1; B check is immediately followed by B->data.
 by.setdefault(r,[]).extend([f'cx q[{d[i]}],q[{a[i]}];' for i in range(7)]+[f'cx q[{b[i]}],q[{c[i]}];' for i in range(7)])
 for key,cells in [('a',a),('c',c)]:
  for i,q in enumerate(cells):bits[key,i]=n;by.setdefault(r+1,[]).append(f'measure q[{q}] -> c[{n}];');n+=1
 by.setdefault(r+1,[]).extend([f'cx q[{b[i]}],q[{d[i]}];' for i in range(7)])
 for i,q in enumerate(b):bits['b',i]=n;by.setdefault(r+2,[]).extend([f'h q[{q}];',f'measure q[{q}] -> c[{n}];']);n+=1
 used=sorted({int(q) for ls in by.values() for line in ls for q in QRE.findall(line)});bar='barrier '+','.join(f'q[{q}]' for q in used)+';';out=[x for x in head if x.startswith(('OPENQASM','include','qreg'))]+[f'creg c[{n}];']
 for st0 in range(r+3):
  out+=by.get(st0,[])+[bar]
 out=out[:-1]
 # Preserve every source prefix detector, then append final block detectors and C logical parity.
 out += pre_det
 for key in 'abc':
  for S in GENS:out.append('// DETECTOR '+' '.join(f'c[{bits[key,i]}]' for i in S))
 out.append('// DETECTOR '+' '.join(f'c[{bits["c",i]}]' for i in range(7)))
 return '\n'.join(out)+'\n',dict(data_qubits=d,layout=lay.get('source',tag),R=r,pre_end=32,last_round_cx=r+2,A=a,B=b,C=c,moves=lay.get('moves'),cx=sum(line.startswith('cx ') for line in out),encoders={'A':A,'BC':BC},prefix=tag)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('layout');ap.add_argument('a');ap.add_argument('bc');ap.add_argument('out');ap.add_argument('--source');args=ap.parse_args();lay=json.loads(Path(args.layout).read_text());A=json.loads(Path(args.a).read_text());BC=json.loads(Path(args.bc).read_text());txt,meta=build(lay,A,BC,lay['pre_transform'],args.source);Path(args.out+'.qasm').write_text(txt);Path(args.out+'.json').write_text(json.dumps(meta,indent=2)+'\n');print(meta)
if __name__=='__main__':main()
