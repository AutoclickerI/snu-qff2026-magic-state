from fr import *
ops,dets,md=load(V36F)
def variant(name,moves):
    o2=copy.deepcopy(ops)
    objs=[(find(o2,k,qs,t),t2) for (k,qs,t),t2 in moves]
    for o,t2 in objs:o.time=t2
    check_conflicts(o2)
    s=emit(name,o2,copy.deepcopy(dets),md,dict(base='MAIN/v36f',moves=[f'{k}{qs}@{t}->{t2}' for (k,qs,t),t2 in moves]))
    try:
        r=certify(s); print(name,{k:r[k] for k in ('ideal_acceptance','ideal_loss','stabilizers_ok','n_harmful','ok')},r.get('harmful_singles')[:5])
    except AssertionError as e: print(name,'FAIL',str(e)[:80])
    return s
a,b,c,d=('CX',(3,2),30),('CX',(8,2),31),('CX',(2,8),32),('CX',(2,3),33)
T=(('TDG',(8,),30),29)
for nm,order in [('b1',[b,c,a,d]),('b2',[c,b,a,d]),('b3',[b,c,d,a]),('b4',[c,b,d,a])]:
    variant('blue_'+nm,[T]+[(g,30+i) for i,g in enumerate(order)])
