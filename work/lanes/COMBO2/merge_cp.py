import json, re, sys
from pathlib import Path
from ortools.sat.python import cp_model
sys.path.insert(0,str(Path(__file__).parents[1]/'LAYOUT2'))
import merge
from steane_full import GENS, PRE_DETECTORS
QRE=merge.QRE

def jobs(preps,layout,moves,anc,tree):
 out=[]
 def add(stmts,qs,tag): out.append({'stmts':stmts,'qs':tuple(sorted(set(qs))),'tag':tag})
 for pi,path in enumerate(moves):
  for hi,(s,d) in enumerate(zip(path,path[1:])):
   add([f'reset q[{d}];'],[d],f'move{pi}.{hi}.reset')
   add([f'cx q[{s}],q[{d}];'],[s,d],f'move{pi}.{hi}.fwd')
   add([f'cx q[{d}],q[{s}];'],[s,d],f'move{pi}.{hi}.back')
 for k in ('a','bc'):
  p=preps[k]; ops,piv=p['ops'],p['pivots']
  cells=(list(layout['a']) if k=='a' else sorted(set(layout['b']+layout['c'])|{q for L in ops for e in L for q in e}))
  first={}
  for t,L in enumerate(ops):
   for u,v in L: first.setdefault(u,t); first.setdefault(v,t)
  for q in cells:first.setdefault(q,0)
  for q in sorted(first,key=first.get): add([f'reset q[{q}];']+([f'h q[{q}];'] if q in piv else []),[q],f'{k}.init.{q}')
  for t,L in enumerate(ops):
   for u,v in L:add([f'cx q[{u}],q[{v}];'],[u,v],f'{k}.cx.{t}.{u}.{v}')
 for q in anc:add([f'reset q[{q}];']+([f'h q[{q}];'] if q==anc[0] else []),[q],f'cat.init.{q}')
 for u,v in tree:add([f'cx q[{u}],q[{v}];'],[u,v],f'cat.cx.{u}.{v}')
 return out

def solve(js,release,round_q,anc,seconds=120,workers=8):
 m=cp_model.CpModel(); N=len(js); starts=[m.NewIntVar(0,130,f's{i}') for i in range(N)]; ends=[m.NewIntVar(1,131,f'e{i}') for i in range(N)]; iv=[m.NewIntervalVar(starts[i],1,ends[i],f'j{i}') for i in range(N)]; byq={q:[] for q in range(36)}
 for i,j in enumerate(js):
  for q in j['qs']:
   byq[q].append(i);m.Add(starts[i]>=release.get(q,0))
 for q,ix in byq.items():
  if ix:
   m.AddNoOverlap([iv[i] for i in ix])
   for a,b in zip(ix,ix[1:]):m.Add(starts[b]>=ends[a])
 R=m.NewIntVar(33,120,'R')
 for q in round_q:
  for i in byq[q]:m.Add(ends[i]<=R)
 for q in anc:
  for i in byq[q]:m.Add(ends[i]<=R+1)
 m.Minimize(R); s=cp_model.CpSolver();s.parameters.max_time_in_seconds=seconds;s.parameters.num_workers=workers;s.parameters.random_seed=0
 st=s.Solve(m)
 if st not in (cp_model.OPTIMAL,cp_model.FEASIBLE):raise RuntimeError(s.StatusName(st))
 r=s.Value(R);m.Add(R==r);m.ClearObjective();m.Maximize(sum(starts));st=s.Solve(m)
 if st not in (cp_model.OPTIMAL,cp_model.FEASIBLE):raise RuntimeError(s.StatusName(st))
 return [s.Value(x) for x in starts],r,s.StatusName(st),s.WallTime()

def build(preps,layout,moves,seconds=120,workers=8):
 head,stmts=merge.prefix_steps();release={};by={}
 for text,step in stmts:
  by.setdefault(step,[]).append(text)
  for q in map(int,QRE.findall(text)):release[q]=max(release.get(q,0),step+1)
 anc=layout['cat'];seen={anc[0]};tree=[]
 while len(seen)<len(anc):
  e=next((u,v) for u in seen for v in anc if v not in seen and abs(u//6-v//6)+abs(u%6-v%6)==1);tree.append(e);seen.add(e[1])
 js=jobs(preps,layout,moves,anc,tree); round_q=set(layout['a']+layout['b']+layout['c']+layout['d']);when,R,status,wall=solve(js,release,round_q,anc,seconds,workers)
 for j,t in zip(js,when):by.setdefault(t,[]).extend(j['stmts'])
 n=14;bits={};r0=[];r1=[];r2=[];d,a,b,c=layout['d'],layout['a'],layout['b'],layout['c']
 for i in range(7):r0 += [f'cx q[{d[i]}],q[{a[i]}];',f'cx q[{b[i]}],q[{c[i]}];']
 for k,cells in (('a',a),('c',c)):
  for i,q in enumerate(cells):bits[(k,i)]=n;r1.append(f'measure q[{q}] -> c[{n}];');n+=1
 for i in range(7):r1.append(f'cx q[{b[i]}],q[{d[i]}];')
 for i,q in enumerate(b):bits[('b',i)]=n;r2 += [f'h q[{q}];',f'measure q[{q}] -> c[{n}];'];n+=1
 for u,v in zip(anc,layout['M']):by.setdefault(R+1,[]).append(f'cx q[{u}],q[{a[v]}];')
 gb=[]
 for q in anc:by.setdefault(R+2,[]).extend([f'h q[{q}];',f'measure q[{q}] -> c[{n}];']);gb.append(n);n+=1
 by.setdefault(R,[]).extend(r0);by.setdefault(R+1,[]).extend(r1);by.setdefault(R+2,[]).extend(r2)
 used=sorted({int(x) for vals in by.values() for s in vals for x in QRE.findall(s)});bar='barrier '+','.join(f'q[{q}]' for q in used)+';';out=head+[f'creg c[{n}];']
 for t in range(min(by),R+3):
  if t==R:out.append('// region round')
  out += by.get(t,[])+[bar]
 out=out[:-1];dets=list(PRE_DETECTORS)
 for k in 'abc':
  for S in GENS:dets.append(' '.join(f'c[{bits[(k,i)]}]' for i in S))
 dets.append(' '.join(f'c[{bits[("c",i)]}]' for i in range(7)));dets.append(' '.join(f'c[{x}]' for x in gb));out += [f'// DETECTOR {x}' for x in dets]
 return '\n'.join(out)+'\n',list(d),R,max(release.values()),status,wall

def main():
 l,a,bc,o=sys.argv[1:5];sec=float(sys.argv[5]) if len(sys.argv)>5 else 120;workers=int(sys.argv[6]) if len(sys.argv)>6 else 8;lay=json.loads(Path(l).read_text());A=json.loads(Path(a).read_text());BC=json.loads(Path(bc).read_text());A=A[0] if isinstance(A,list) else A;txt,data,R,pre,status,wall=build({'a':A,'bc':BC},lay,lay['moves'],sec,workers);Path(o+'.qasm').write_text(txt);Path(o+'.json').write_text(json.dumps({'data_qubits':data,'layout':l,'A':a,'BC':bc,'R':R,'pre_end':pre,'solver':status,'solver_wall':wall,'M':lay['M'],'cat':lay['cat'],'cx':txt.count('cx ')},indent=2)+'\n');print(o,'R',R,'pre',pre,'status',status,'wall',wall,'cx',txt.count('cx '),flush=True)
if __name__=='__main__':main()
