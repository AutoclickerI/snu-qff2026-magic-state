"""Fit complete helper lifetimes into native ticks; preserve all original native operations."""
import os,sys,json,re,itertools,hashlib
from pathlib import Path
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
H=Path(__file__).resolve().parent; ROOT=H.parents[2]
os.environ['XTIM_TWIRL_CACHE_DIR']=str(H/'.xtim_cache')
import xtim
xtim.cache_dir=str(H/'.xtim_cache')
sys.path.insert(0,str(ROOT/'work/lanes/EVAL'))
from exact2 import Eval,qasm_lines
BASE=ROOT/'work/lanes/MAIN/v30f'
TEXT=BASE.with_suffix('.qasm').read_text();DATA=json.loads(BASE.with_suffix('.json').read_text())['data_qubits']
EV=Eval(TEXT,DATA);M=EV.m;QL=qasm_lines(TEXT)
HEADER=[];DETS=[];BLOCKS=[[]];BARRIERS=[]; RAWSTEP={}
for ln,l in enumerate(TEXT.splitlines(),1):
 if l.startswith(('OPENQASM','include','qreg','creg')):HEADER.append(l)
 elif l.startswith('//'):DETS.append(l)
 elif l.startswith('barrier'):
  BARRIERS.append(l);BLOCKS.append([])
 elif l.strip():BLOCKS[-1].append(l);RAWSTEP[ln]=len(BLOCKS)-1
OPS=[]
for i,x in enumerate(M.prog):
 if not x.qubits:continue
 k=int(re.search(r'instruction (\d+)',M.labels[i]).group(1));rl=QL[k-1][0];t=M.steps[i][0][1]
 assert RAWSTEP[rl]==t,(rl,t,RAWSTEP[rl])
 OPS.append(dict(name=x.name,qs=list(x.qubits),tick=t,rawline=rl))
QOPS={q:[o for o in OPS if q in o['qs']] for q in range(36)}
BUSY={(o['tick'],q) for o in OPS for q in o['qs']}
FANO=[[0,20,7],[0,10,3],[20,10,22],[7,3,22],[7,10,21],[20,3,21],[0,22,21]]
TRAJECTORIES={0:[(0,16,50)],20:[(20,16,50)],7:[(7,16,50)],
 10:[(4,16,30),(10,33,50)],3:[(3,16,50)],
 22:[(15,16,32),(16,35,41),(22,44,50)],
 21:[(8,16,33),(9,36,36),(15,38,38),(21,40,50)]}
def adjacent(q):return [h for h in range(36) if abs(h//6-q//6)+abs(h%6-q%6)==1]
def templates():
 out=[];gaps=[];free=[]
 for q in DATA+[4,15,16]:
  for a,b in zip(QOPS[q],QOPS[q][1:]):
   lo,hi=a['tick']+1,b['tick']-1
   if hi<lo:continue
   gaps.append(dict(q=q,lo=lo,hi=hi,adjacent=adjacent(q)))
   if hi<18:continue
   for h in adjacent(q):
    seq=[dict(name='UNUSED',tick=-1)]+QOPS[h]+[dict(name='END',tick=51)]
    for prev,nxt in zip(seq,seq[1:]):
     # A free helper has not been used or has been measured. Idle entangled cells are not free.
     if prev['name'] not in ('UNUSED','M','MX'):continue
     flo,fhi=prev['tick']+1,nxt['tick']-1
     if max(flo,lo)>min(fhi,hi):continue
     free.append(dict(q=q,lo=lo,hi=hi,h=h,free=[flo,fhi],previous=prev['name'],next=nxt['name']))
     for axis in ('Z','X'):
      restore=(axis=='Z' and nxt['name']=='M') or (axis=='X' and nxt['name']=='MX' and prev['name']=='MX')
      # Reset one tick before first CX; measure one tick after last CX. Restore a reused
      # measured basis when required. All operations remain inside helper's free lifetime.
      start=max(lo,flo+1);end=min(hi,fhi-1-int(restore))
      if end<=start:continue
      logical=next((dq for dq,path in TRAJECTORIES.items() for cell,ta,tb in path if cell==q and ta<=start<=end<=tb),None)
      out.append(dict(q=q,h=h,axis=axis,start=start,end=end,reset=start-1,measure=end+1,logical=logical,
                      restore=(end+2 if restore else None),gap=[lo,hi],free=[flo,fhi],kind='whole' if start==lo and end==hi else 'part'))
 # No duplicate physical schedules.
 return list({(x['q'],x['h'],x['axis'],x['start'],x['end']):x for x in out}.values()),gaps,free

def extra_ops(g,rec):
 q,h=g['q'],g['h'];z=g['axis']=='Z'
 cx=f'cx q[{h}],q[{q}];' if z else f'cx q[{q}],q[{h}];'
 out=[(g['reset'],[h],[f'reset q[{h}];']+([f'h q[{h}];'] if z else [])),
      (g['start'],[h,q] if z else [q,h],[cx]),(g['end'],[h,q] if z else [q,h],[cx]),
      (g['measure'],[h],([f'h q[{h}];'] if z else [])+[f'measure q[{h}] -> c[{rec}];']+([f'h q[{h}];'] if z else []))]
 if g['restore'] is not None:out.append((g['restore'],[h],[f'reset q[{h}];']+([f'h q[{h}];'] if not z else [])))
 return out

def compatible(gs):
 # Helpers must remain dedicated throughout their lifetime, including idle time.
 for a,b in itertools.combinations(gs,2):
  if set((a['q'],a['h']))&set((b['q'],b['h'])):
   al=a['restore'] if a['restore'] is not None else a['measure'];bl=b['restore'] if b['restore'] is not None else b['measure']
   if not(al<b['reset'] or bl<a['reset']):return False
 busy=set(BUSY)
 for k,g in enumerate(gs):
  for t,qs,ls in extra_ops(g,264+k):
   for q in qs:
    if (t,q) in busy:return False
    busy.add((t,q))
 return True

def emit(name,gs):
 assert compatible(gs),gs
 bl=[list(b) for b in BLOCKS]; origins={};extra=[]
 for k,g in enumerate(gs):
  for t,qs,ls in extra_ops(g,264+k):bl[t].extend(ls)
  extra.append(f'// DETECTOR c[{264+k}]')
 hdr=[re.sub(r'creg c\[\d+\]',f'creg c[{264+len(gs)}]',l) for l in HEADER]
 text=list(hdr)
 for t,b in enumerate(bl):
  text.extend(b)
  if t<len(BARRIERS):text.append(BARRIERS[t])
 text.extend(DETS+extra); text='\n'.join(text)+'\n'
 stem=H/name;stem.with_suffix('.qasm').write_text(text)
 md=dict(data_qubits=DATA,base_sha256=hashlib.sha256(TEXT.encode()).hexdigest(),protected=gs,R=48,native_depth=51,cx=189+2*len(gs),source='WAITPROT native-tick storage')
 stem.with_suffix('.json').write_text(json.dumps(md,indent=2)+'\n')
 return stem

def check(stem):
 md=json.loads(stem.with_suffix('.json').read_text());ev=Eval(stem.with_suffix('.qasm').read_text(),DATA)
 expected=[]
 for t in range(51):
  expected.extend((o['name'],tuple(o['qs']),t) for o in OPS if o['tick']==t)
  for k,g in enumerate(md['protected']):
   for tt,qs,ls in extra_ops(g,264+k):
    if tt==t:
     n=('RX' if g['axis']=='Z' else 'R') if t==g['reset'] else ('CX' if t in (g['start'],g['end']) else ('MX' if g['axis']=='Z' else 'M'))
     if t==g['restore']:n='RX' if g['axis']=='X' else 'R'
     expected.append((n,tuple(qs),t))
 actual=[(x.name,tuple(x.qubits),ev.m.steps[i][0][1]) for i,x in enumerate(ev.m.prog) if x.qubits]
 assert actual==expected, next(((a,b) for a,b in zip(actual,expected) if a!=b),('length',len(actual),len(expected)))
 return dict(correct=True,c1=float(ev.fp@ev.n_single),exp_minus_A1=float(__import__('numpy').exp(-ev.fp@(1-ev.a_single))),channels=len(ev.m.chans),classes=len(ev.gkeys))

if __name__=='__main__':
 ts,gaps,free=templates();(H/'tick_mapping.json').write_text(json.dumps(dict(data_order=DATA,gaps=gaps,free=free,templates=ts,fano=FANO),indent=2))
 rows=[]
 for i,g in enumerate(ts):
  name=f't{i:02d}_{g["axis"].lower()}q{g["q"]}h{g["h"]}_{g["start"]}_{g["end"]}'
  p=emit(name,[g]);r=dict(stem=name,gadgets=[g])
  try:r.update(check(p))
  except Exception as e:r.update(correct=False,error=repr(e))
  rows.append(r);print(json.dumps(r),flush=True)
 (H/'tick_singles.json').write_text(json.dumps(rows,indent=2))
