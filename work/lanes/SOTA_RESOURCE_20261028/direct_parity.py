"""Complete native direct six-stabilizer readout using dirty bridge CNOTs.
A bounded architectural pilot: physical noise is retained everywhere.
"""
import os,sys,json,collections
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
R=Path.cwd();H=R/'work/lanes/SOTA_RESOURCE_20261028';sys.path[:0]=[str(R/'work/tools'),str(R/'work/lanes/END2_20261027'),str(R/'work/lanes/REBUILD20261027')]
from qtools.evaluator import frontend as f
from qtools.validity import raw_check
from qtools import write_stem,price
from joint import emit
from record_contract import complete,singles
base=R/'work/lanes/NATIVE2_20261027/boundary/source_prefix_d828869d5031c029_d6_20_19_10_2_22_16';data=json.loads(base.with_suffix('.json').read_text())['data_qubits'];ops,dets=f.parse_current(base.with_suffix('.qasm').read_text());f.DATA=data

def path(a,b):
 prev={a:None};q=collections.deque([a])
 while q:
  u=q.popleft()
  if u==b:break
  for v in range(36):
   if v not in prev and abs(u//6-v//6)+abs(u%6-v%6)==1:prev[v]=u;q.append(v)
 p=[]
 while b is not None:p.append(b);b=prev[b]
 return p[::-1]
def remote(p):
 if len(p)==2:return [p]
 es=[list(e) for e in zip(p,p[1:])];half=es+es[-2:0:-1];return half+half
# Each check uses the minimum remote-CX-cost ancilla, fully serialized at
# the instrument level; dirty intermediates are restored by each bridge.
usedtime=max(o.time for o in ops)+1;bit=max(o.bit for o in ops if o.bit is not None)+1;checks=[]
for basis in ('Z','X'):
 for support in f.SUPPORTS:
  targets=[data[i] for i in sorted(support)]
  def cost(q):
   return sum((1 if len(path(q,d))==2 else 4*(len(path(q,d))-1)-4) for d in targets)
  anc=min((q for q in range(36) if q not in data),key=cost)
  ops.append(f.Op('R' if basis=='Z' else 'RX',(anc,),usedtime));usedtime+=1
  for d in targets:
   for a,b in remote(path(d,anc) if basis=='Z' else path(anc,d)):
    ops.append(f.Op('CX',(a,b),usedtime));usedtime+=1
  ops.append(f.Op('M' if basis=='Z' else 'MX',(anc,),usedtime,bit));checks.append({'basis':basis,'ancilla':anc,'record':bit,'time':usedtime,'targets':targets});bit+=1;usedtime+=1
ops.sort(key=lambda o:o.time)
model=f.make_model(ops,dets);rec=complete(model,dets);extra=[set(r['bits']) for r in rec['missing'] if not r['reference']];dets+=extra
text=emit(ops,dets);raw=raw_check(text,data);stem=write_stem(text,data,H/'cand','direct_parity',source={'parent':str(base),'checks':checks,'native':True,'scope':'Direct physical stabilizer-readout pilot; all gates and waits noisy.'})
r={'stem':str(stem),'checks':checks,'raw':raw,'cx':sum(o.kind=='CX' for o in ops),'ticks':max(o.time for o in ops)+1,'extra_detectors':len(extra)}
print('RAW',json.dumps(r),flush=True)
if raw['ok']:
 ss=singles(f.make_model(*f.parse_current(text)));r['singles']=ss;print('SINGLES',ss['c1'],len(ss['harmful_faults']),flush=True)
 r['exact']=price(stem,1,use_cache=False);print('EXACT',r['exact']['loss'],r['exact']['acceptance'],flush=True)
(H/'direct_parity.receipt.json').write_text(json.dumps(r,indent=2)+'\n')
