from fr import *
ops,dets,md=load(V36F)
data=md['data_qubits'];A=[1,14,8,9,2,16,15]
o2=copy.deepcopy(ops);changes=[]
end=max(o.time for o in o2)
for q in data:
    a=A[data.index(q)];at=max(o.time for o in o2 if o.kind=='CX' and o.qs==(q,a))-1
    conflict=[o for o in o2 if o.time==at and q in o.qs]
    if conflict:
        assert len(conflict)==1 and conflict[0].kind in ('T','TDG'),(q,at,[(c.kind,c.qs) for c in conflict])
        assert not any(o.time==at-1 and q in o.qs for o in o2),(q,at)
        conflict[0].time-=1;changes.append((q,at,at-1))
    assert not any(o.time==end and q in o.qs for o in o2)
    o2.extend([f.Op('SX',(q,),at),f.Op('SXDG',(q,),end)])
check_conflicts(o2)
s=emit('sx_full',o2,copy.deepcopy(dets),md,dict(base='MAIN/v36f',sx='SX before last D->A CX, SXDG at final tick on all 7 data (FRESH r35 recipe)',retimed=changes))
print(changes);print(certify(s));print(json.dumps({k:v for k,v in atoms(s).items() if k not in('offending_gates',)}))
