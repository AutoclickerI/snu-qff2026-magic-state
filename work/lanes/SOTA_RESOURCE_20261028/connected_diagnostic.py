"""Full-noise native-resource diagnostic with ideal synthetic D and A inputs.
Explicit counterfactual, not a complete physical native circuit.
"""
import os,sys,json
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
R=Path.cwd();H=R/'work/lanes/SOTA_RESOURCE_20261028';sys.path[:0]=[str(R/'work/tools'),str(R/'work/lanes/END2_20261027'),str(R/'work/lanes/REBUILD20261027')]
from qtools.evaluator import frontend as f,sparse_walsh as sw
from partial_contract import make_partial_contract
from partial_square import ENC,PIV,prep,ideal_contract_check
from joint import emit
m=json.loads((H/f'{sys.argv[1]}_module.json').read_text());c=make_partial_contract(m['roles'],85,True);D,A=c.D,c.A
ops=[]
for i,q in enumerate(D):ops.append(f.Op('RX' if i in PIV|{2} else 'R',(q,),0))
ops += [f.Op('T',(D[2],),1),f.Op('CX',(D[2],D[4]),2),f.Op('CX',(D[2],D[5]),3)]
for t,l in enumerate(ENC):ops += [f.Op('CX',(D[a],D[b]),4+t) for a,b in l]
prep(ops,A,0,True)
nextbit=21;dets=[set(r) for r in c.DETECTORS]
for x in m['operations']:
 bit=nextbit if x['kind']=='M' else None
 if bit is not None:dets.append({bit});nextbit+=1
 ops.append(f.Op(x['kind'],tuple(x['qs']),x['time'],bit))
round_=max(8,max(x.time for x in ops)+1)
for kind,qs,t,bit in c.terminal():ops.append(f.Op(kind,qs,round_+t,bit))
ops.sort(key=lambda x:x.time);text=emit(ops,dets);raw=ideal_contract_check(text,D)
name=H/f'{sys.argv[1]}_diagnostic';name.with_suffix('.qasm').write_text(text);name.with_suffix('.json').write_text(json.dumps({'data_qubits':D,'raw':raw,'R':round_,'scope':'Abstract ideal D/A input preparations; resource and terminal channels fully noisy.'},indent=2))
assert raw['ok'],raw
model,eng,groups,nd,ks,psi,where,_=sw.prepare(name,True)
for cid,ch in enumerate(model.chans):
 op=model.labels[ch['ins']]
 if op.time<round_ and (set(op.qs)<=set(D) or set(op.qs)<=set(A)):
  ch['p']=0
  for ff in groups[cid]:ff['p']=0
compiled,elim=sw.compile_best(model,eng,groups,nd,ks,save=False);sw._CTX.update(eng=eng,ks=ks,psi=psi,where=where,compiled=compiled,elim=elim)
try:
 vals=[sw._row(k) for k in [None]+eng.keys];acc=vals[0]['value'];obs=sum(w*b*v['value'] for w,b,v in zip(eng.W,eng.beta,vals[1:]));loss=(acc-obs)/(2*acc)
finally:sw._CTX.clear();sw.COLUMNS.clear()
out={'raw':raw,'loss':loss,'acceptance':acc,'round':round_,'resource_cx':m['cx'],'resource_depth':m['depth'],'scope':'Ideal synthetic D/A preparations; all resource and terminal noise retained. Not a complete native circuit.'}
(H/f'{sys.argv[1]}_diagnostic_result.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out),flush=True)
