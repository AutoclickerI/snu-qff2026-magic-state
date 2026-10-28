"""Full noisy ABSTRACT SpiderCSS resource experiment, not a grid-valid candidate."""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import sys,json,hashlib
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[2]
sys.path[:0]=[str(R/'work/lanes/CAT3_20261027')]
import smallcat as s
from multicat import color
s.HERE=H;(H/'cand').mkdir(exist_ok=True)
rounds=[s.GROUPS[2]]*2
stem,meta=s.build(ncat=2,interleaved=True,round_groups=rounds,coupling_layers=color(rounds,0),name='spider_source')
ops,dets=s.f.parse_current(stem.with_suffix('.qasm').read_text())
resource=set(s.A+s.B+s.C)
ops=[o for o in ops if not(o.time>9 and set(o.qs)&resource)]
shift=1; ops=[s.f.Op(o.kind,o.qs,o.time+shift if o.time>9 else o.time,o.bit) for o in ops]
r=meta['tail_start']+shift
perm=(0,1,4,2,5,6,3);mapping={x:s.B[j] for j,x in enumerate(perm)};mapping.update({7:s.C[0],8:s.C[1],9:s.C[2]})
seq=[('RX',(0,)),('RX',(4,)),('RX',(6,))]
for q in (1,2,3,5,7,8,9):seq.append(('R',(q,)))
raw=[('CX',0,7),('CX',7,3),('CX',0,2),('CX',4,8),('CX',6,9),('CX',7,1),('CX',8,2),('CX',4,5),('CX',9,3),('CX',8,1),('CX',9,2),('CX',6,5),('CX',0,7),('M',7),('CX',4,8),('M',8),('CX',6,9),('M',9)]
ready={i:10 for i in range(10)}
for kind,qs in seq:
 q=qs[0];ops.append(s.f.Op(kind,(mapping[q],),10));ready[q]=11
for item in raw:
 kind,*qs=item;t=max(ready[q] for q in qs)
 for q in qs:ready[q]=t+1
 ops.append(s.f.Op(kind,tuple(mapping[q]for q in qs),t,(100+qs[0]-7) if kind=='M' else None))
assert max(ready.values())<=r,(max(ready.values()),r)
s.prep(ops,s.A,r-4,True)
ops += [s.f.Op('CX',(d,a),r)for d,a in zip(s.D,s.A)]
ops += [s.f.Op('CX',(b,d),r+1)for b,d in zip(s.B,s.D)]
ops += [s.f.Op('M',(a,),r+2,107+i)for i,a in enumerate(s.A)]
ops += [s.f.Op('MX',(b,),r+2,114+i)for i,b in enumerate(s.B)]
ops.sort(key=lambda o:o.time);used=set()
for o in ops:
 keys={(o.time,q)for q in o.qs};assert not used&keys,(o,used&keys);used|=keys
s.f.DATA=s.D;contract=s.record_contract.complete(s.f.make_model(ops,[]),[])
assert all(not row['reference']for row in contract['missing'])
text=s.emit(ops,[set(row['bits']) for row in contract['missing']]);out=H/'cand/spider_abstract';out.with_suffix('.qasm').write_text(text)
info={'data_qubits':s.D,'abstract':True,'grid_valid':False,'source':'SpiderCSS generated 7_1_3 depth target, exact real noise, no C verification','raw':s.ideal_contract_check(text,s.D),'cx':sum(o.kind=='CX'for o in ops),'ticks':max(o.time for o in ops)+1,'resource_ready':max(ready.values()),'tail':r}
out.with_suffix('.json').write_text(json.dumps(info,indent=2)+'\n');print('RAW',json.dumps(info),flush=True)
if info['raw']['ok']:
 a=s.record_contract.singles(s.f.make_model(*s.f.parse_current(text)));info['c1']=a['c1'];info['harmful']=len(a['harmful_faults']);print('SINGLES',info['c1'],info['harmful'],flush=True)
 info['exact']=s.exact(out);print('EXACT',json.dumps(info['exact']),flush=True)
(H/'spider_abstract_result.json').write_text(json.dumps(info,indent=2)+'\n')
