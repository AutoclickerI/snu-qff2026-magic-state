from round35 import *
ops,dets,md=load(D/'sx_full')
for subset in (md['data_qubits'],[10,21],[0,20,7,3,22]):
 oo=copy.deepcopy(ops);desc=[]
 for q in subset:
  op=next(o for o in oo if o.kind=='SX' and o.qs==(q,));at=op.time
  for other in oo:
   if other is not op and q in other.qs and at-2<=other.time<at:
    assert other.kind in ('T','TDG')
    assert not any(v is not other and q in v.qs and v.time==at-3 for v in oo)
    desc.append((q,other.kind,other.time,at-3));other.time=at-3
  oo.remove(op);oo.extend([f.Op('H',(q,),at-2),f.Op('S',(q,),at-1),f.Op('H',(q,),at)])
 stem=emit('sx_hsh_'+str(len(subset)),oo,copy.deepcopy(dets),md,dict(hsh_qubits=subset,retimings=desc))
 try:print(stem.name,certify(stem),speed(stem,5000),flush=True)
 except Exception as e:print('ERROR',stem.name,repr(e),flush=True)
