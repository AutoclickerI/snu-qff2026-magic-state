"""Actual noisy SpiderCSS B/C + 6-square tail; abstract connectivity only."""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import sys,json,stim
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[2];sys.path.insert(0,str(R/'work/lanes/CAT3_20261027'))
import smallcat as s
from multicat import color
s.HERE=H;(H/'cand').mkdir(exist_ok=True)
rounds=[s.GROUPS[2]]*2
stem,meta=s.build(ncat=2,interleaved=True,round_groups=rounds,coupling_layers=color(rounds,0),name='spider_bc85_source')
ops,_=s.f.parse_current(stem.with_suffix('.qasm').read_text());resource=set(s.A+s.B+s.C)
ops=[o for o in ops if not(o.time>9 and set(o.qs)&resource)]
c=stim.Circuit((H/'spider_bc85.log').read_text());mapping={i:(s.B+s.C+[32,33,34,35])[i] for i in range(18)}
# Reserve source helper wires until their actual final use; others can start at 10.
ready={i:max([10]+[o.time+1 for o in ops if mapping[i] in o.qs]) for i in range(18)}
flagbit=100
for ins in c:
 typ=ins.name;ts=[x.value for x in ins.targets_copy()]
 if typ=='DETECTOR':continue
 if typ in ('R','RX','M','MX'):
  for i in ts:
   t=ready[i];ready[i]=t+1;b=None
   if typ in ('M','MX'):b=flagbit;flagbit+=1
   ops.append(s.f.Op(typ,(mapping[i],),t,b))
 elif typ=='CX':
  for a,b in zip(ts[::2],ts[1::2]):
   t=max(ready[a],ready[b]);ready[a]=ready[b]=t+1
   ops.append(s.f.Op('CX',(mapping[a],mapping[b]),t))
 else:raise ValueError(typ)
r=max(meta['tail_start'],max(ready.values()))
s.prep(ops,s.A,r-4,True)
ops += [s.f.Op('CX',(d,a),r)for d,a in zip(s.D,s.A)]
ops += [s.f.Op('CX',(b,c),r)for b,c in zip(s.B,s.C)]
ops += [s.f.Op('CX',(b,d),r+1)for b,d in zip(s.B,s.D)]
ops += [s.f.Op('CX',(s.C[i],s.A[i]),r+1)for i in [0,2,4,6]]
ops += [s.f.Op('M',(a,),r+2,107+i)for i,a in enumerate(s.A)]
ops += [s.f.Op('MX',(b,),r+2,114+i)for i,b in enumerate(s.B)]
ops += [s.f.Op('MX',(c,),r+2,121+i)for i,c in enumerate(s.C)]
ops.sort(key=lambda o:o.time);used=set()
for o in ops:
 keys={(o.time,q)for q in o.qs};assert not used&keys,(o,used&keys);used|=keys
s.f.DATA=s.D;contract=s.record_contract.complete(s.f.make_model(ops,[]),[])
assert all(not row['reference']for row in contract['missing'])
text=s.emit(ops,[set(row['bits']) for row in contract['missing']]);out=H/'cand/spider_bc85_abstract';out.with_suffix('.qasm').write_text(text)
info={'data_qubits':s.D,'abstract':True,'grid_valid':False,'source':'SpiderCSS generated corrected four-square mask85 joint BC, all noise, abstract edges','raw':s.ideal_contract_check(text,s.D),'cx':sum(o.kind=='CX'for o in ops),'ticks':max(o.time for o in ops)+1,'resource_ready':max(ready.values()),'tail':r}
out.with_suffix('.json').write_text(json.dumps(info,indent=2)+'\n');print('RAW',json.dumps(info),flush=True)
if info['raw']['ok']:
 a=s.record_contract.singles(s.f.make_model(*s.f.parse_current(text)));info['c1']=a['c1'];info['harmful']=len(a['harmful_faults']);print('SINGLES',info['c1'],info['harmful'],flush=True)
 info['exact']=s.exact(out);print('EXACT',info['exact']['loss'],info['exact']['acceptance'],flush=True)
(H/'spider_bc85_abstract_result.json').write_text(json.dumps(info,indent=2)+'\n')
