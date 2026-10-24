#!/usr/bin/env python
import os,sys,json
HERE=os.path.dirname(os.path.abspath(__file__))
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT,'work','lanes','EARLY'))
sys.path.insert(0, os.path.join(ROOT,'work','lanes','DR'))
import early_merge
from steane_full import GENS, PRE_DETECTORS
PRE_DATA=[0,20,7,4,3,15,8]
FREE=[5,11,12,16,17,18,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35]
PIV=[0,1,3]
LAYERS0=[[(0,2),(1,6),(3,5)],[(0,4),(1,2),(3,6)],[(0,6),(1,5),(3,4)]]
def enc(cells,plus,t0):
 out=[]
 for i,q in enumerate(cells):
  out.append((t0-1,f'reset q[{q}];'))
  if (i in PIV)!=plus: out.append((t0-1,f'h q[{q}];'))
 for k,layer in enumerate(LAYERS0):
  for c,t in layer:
   a,b=(cells[t],cells[c]) if plus else (cells[c],cells[t])
   out.append((t0+k,f'cx q[{a}],q[{b}];'))
 return out
# edge-color the three GENS checks, flag ancilla on target
edges=[(k,i) for k,S in enumerate(GENS) for i in S]
# simple backtracking colors 0..3, no same B or flag in layer
colors={}
def bt(j):
 if j==len(edges): return True
 k,i=edges[j]
 for c in range(4):
  if any(v==c and (kk==k or ii==i) for (kk,ii),v in colors.items()): continue
  colors[(k,i)]=c
  if bt(j+1): return True
  del colors[(k,i)]
 return False
assert bt(0),colors

def build(R=39):
 head,stmts=early_merge.prefix_steps(); by={}
 for s,t in stmts: by.setdefault(t,[]).append(s)
 A,B,F=FREE[:7],FREE[7:14],FREE[14:17]
 # Encoders finish at R-7=32 for R=39; flag checks t33..36.
 for t,s in enc(A,True,R-9)+enc(B,False,R-9): by.setdefault(t,[]).append(s)
 n=14; fbits=[]
 for q in F: by.setdefault(R-7,[]).append(f'reset q[{q}];')
 for (k,i),c in sorted(colors.items(),key=lambda x:x[1]):
  by.setdefault(R-6+c,[]).append(f'cx q[{B[i]}],q[{F[k]}];')
 for k,q in enumerate(F):
  fbits.append(n); by.setdefault(R-2,[]).append(f'measure q[{q}] -> c[{n}];'); n+=1
 # final Steane-like round: data->A, B->data, then read A Z/B X
 bitsA=[]; bitsB=[]
 for i in range(7): by.setdefault(R,[]).append(f'cx q[{PRE_DATA[i]}],q[{A[i]}];')
 for i in range(7): by.setdefault(R+1,[]).append(f'cx q[{B[i]}],q[{PRE_DATA[i]}];')
 for i,q in enumerate(A): bitsA.append(n); by.setdefault(R+2,[]).append(f'measure q[{q}] -> c[{n}];');n+=1
 for i,q in enumerate(B): bitsB.append(n); by.setdefault(R+2,[]).append(f'h q[{q}];'); by.setdefault(R+2,[]).append(f'measure q[{q}] -> c[{n}];');n+=1
 bar='barrier '+','.join(f'q[{q}]' for q in range(36))+';'
 out=head+[f'creg c[{n}];']
 for t in range(min(by),R+3): out += by.get(t,[]) or ['id q[35];']; out.append(bar)
 out=out[:-1]
 dets=list(PRE_DETECTORS)
 # B flag records are expected +1 parity (all-zero syndrome)
 for b in fbits: dets.append(f'c[{b}]')
 for S in GENS: dets.append(' '.join(f'c[{bitsA[i]}]' for i in S))
 for S in GENS: dets.append(' '.join(f'c[{bitsB[i]}]' for i in S))
 out += [f'// DETECTOR {d}' for d in dets]
 return '\n'.join(out)+'\n', {'data_qubits':PRE_DATA,'grid_free':True,'variant':'merged3_flagged_B','R':R,'cx':sum(1 for x in out if x.startswith('cx ')),'flag_colors':{f'{k},{i}':c for (k,i),c in colors.items()}}
if __name__=='__main__':
 out,meta=build(int(sys.argv[1]) if len(sys.argv)>1 else 39); stem=sys.argv[2] if len(sys.argv)>2 else 'work/lanes/GAP/merged3'; open(stem+'.qasm','w').write(out); json.dump(meta,open(stem+'.json','w'),indent=2)
