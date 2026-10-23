"""Extract the exact submitted v12 pre-stage, including its native times."""
import os,sys,re,json,collections
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path[:0]=[str(ROOT/'work'),str(ROOT/'work/lanes/me_layout'),str(ROOT/'work/lanes/DR')]
from tprep.qasm import convert
from tprep.noise import schedule
SRC=(ROOT/'work/submissions/v12_L5lns12_r86.qasm').read_text()
BASE=json.loads((ROOT/'work/lanes/L5_precycle/combined_lns_0012.json').read_text())
OPS=[(k,tuple(qs),b) for k,qs,b in BASE['schedule']['ops']];TIMES=BASE['schedule']['times'];NPRE=137
DATA0=[0,20,7,4,3,15,8]
def native(k):return {'cx':'CX','MX_KEEP':'MX','g:t':'T','g:tdg':'T_DAG'}.get(k,k)
# Reconstruct native scheduling and lazy initialization from the saved source.
free={};nt={}
for t in sorted(set(TIMES)):
 for i,(k,qs,b) in enumerate(OPS):
  if TIMES[i]!=t:continue
  nt[i]=max(free.get(q,0) for q in qs)
  for q in qs:free[q]=nt[i]+1
 sync=max(free.values());free={q:sync for q in free}
for i,(k,qs,b) in enumerate(OPS):
 if k in ('R','RX'):
  following=[j for j,(_,qq,_) in enumerate(OPS) if TIMES[j]>TIMES[i] and qs[0] in qq]
  if following:nt[i]=min(nt[j] for j in following)-1
expected={(native(k),qs,nt[i]):i for i,(k,qs,b) in enumerate(OPS)}
assert len(expected)==len(OPS)
stimtext,labels,err=convert(SRC);assert not err,err
prog,steps,gaps=schedule(stimtext)
raw=[line for line in SRC.splitlines() if line.strip() and not line.startswith(('OPENQASM','include','qreg','creg','//'))]
owner={};source_native={};node_to_prog={}
for ii,ins in enumerate(prog):
 if not steps[ii]:continue
 key=(ins.name,tuple(ins.qubits),steps[ii][0][1]);i=expected.pop(key)
 ri=int(re.match(r'instruction (\d+)',labels[ins.line_no-1]).group(1))-1
 owner[ri]=i;source_native[ri]=ins.name;node_to_prog[i]=ii
assert not expected,expected
# Native folding drops only H statements. Attach them to their R/M owner.
for ri,line in enumerate(raw):
 if line.startswith('barrier') or ri in owner:continue
 assert line.startswith('h '),line
 q=int(re.search(r'q\[(\d+)\]',line).group(1))
 same=[j for j,s in enumerate(raw) if j in owner and re.search(rf'q\[{q}\]',s)]
 prev=max((j for j in same if j<ri),default=None);nxt=min((j for j in same if j>ri),default=None)
 if nxt is not None and source_native[nxt]=='MX':owner[ri]=owner[nxt]
 elif prev is not None and source_native[prev] in ('RX','MX'):owner[ri]=owner[prev]
 else:raise ValueError((ri,line,prev,nxt,raw[prev] if prev is not None else None,raw[nxt] if nxt is not None else None,source_native.get(prev),source_native.get(nxt)))
PRE=[(nt[owner[j]],j,line,owner[j]) for j,line in enumerate(raw) if j in owner and owner[j]<NPRE]
PRE_LAST={q:max(nt[i] for i,(k,qs,b) in enumerate(OPS[:NPRE]) if q in qs) for q in {q for k,qs,b in OPS[:NPRE] for q in qs}}
RETAINED={qs[0]:(b,nt[i]) for i,(k,qs,b) in enumerate(OPS[:NPRE]) if k=='MX_KEEP'}
PRE_DETS=[line for line in SRC.splitlines() if line.startswith('// DETECTOR') and all(int(b)<14 for b in re.findall(r'c\[(\d+)\]',line))]

def op_lines(k,qs,b=None):
 if k=='CX':return [f'cx q[{qs[0]}],q[{qs[1]}];']
 if k=='RX':return [f'reset q[{qs[0]}];',f'h q[{qs[0]}];']
 if k=='R':return [f'reset q[{qs[0]}];']
 if k in ('M','MX'):return ([f'h q[{qs[0]}];'] if k=='MX' else [])+[f'measure q[{qs[0]}] -> c[{b}];']
 raise ValueError(k)

def emit(nodes,times,detectors,nbits):
 by=collections.defaultdict(list)
 for t,j,line,i in PRE:by[t].append((j,line))
 for i,((k,qs,b),t) in enumerate(zip(nodes,times)):
  for j,line in enumerate(op_lines(k,qs,b)):by[t].append((10000+3*i+j,line))
 used=sorted(set(PRE_LAST)|{q for k,qs,b in nodes for q in qs})
 bar='barrier '+','.join(f'q[{q}]' for q in used)+';'
 out=['OPENQASM 2.0;','include "qelib1.inc";','qreg q[36];',f'creg c[{nbits}];']
 for t in range(max(by)+1):
  out.extend(line for j,line in sorted(by[t]))
  if t<max(by):out.append(bar)
 out+=PRE_DETS+['// DETECTOR '+' '.join(f'c[{b}]' for b in d) for d in detectors]
 return '\n'.join(out)+'\n'

def audit(text):
 st,labs,err=convert(text);assert not err,err
 pp,ss,gg=schedule(st)
 actual=collections.Counter((ins.name,tuple(ins.qubits),ss[i][0][1]) for i,ins in enumerate(pp) if ss[i])
 for i,(k,qs,b) in enumerate(OPS[:NPRE]):assert actual[(native(k),qs,nt[i])]>0,(i,k,qs,nt[i])
 # Raw pre-stage instructions appear literally, in the submitted relative order.
 return dict(pre_nodes=NPRE,pre_raw_lines=len(PRE),pre_last=PRE_LAST,retained=RETAINED,pre_native_times_verified=True)

if __name__=='__main__':
 nodes=[(native(k),qs,b) for k,qs,b in OPS[NPRE:]];ts=[nt[i] for i in range(NPRE,len(OPS))]
 dets=[[int(b) for b in re.findall(r'c\[(\d+)\]',l)] for l in SRC.splitlines() if l.startswith('// DETECTOR') and any(int(b)>=14 for b in re.findall(r'c\[(\d+)\]',l))]
 text=emit(nodes,ts,dets,22);print(audit(text),flush=True)
 a,_,_=convert(text);p,s,g=schedule(a)
 assert collections.Counter((x.name,tuple(x.qubits),s[i][0][1]) for i,x in enumerate(p) if s[i])==collections.Counter((x.name,tuple(x.qubits),steps[i][0][1]) for i,x in enumerate(prog) if steps[i])
 (HERE/'prefix_audit.json').write_text(json.dumps(audit(text),indent=2));print('FULL NATIVE MATCH',flush=True)
