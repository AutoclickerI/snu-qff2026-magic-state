from fr import *
ops,dets,md=load(V36F)
show(ops,20,24)
pairs=[('CX',(14,13),21),('CX',(14,13),22),('CX',(9,10),21),('CX',(9,10),22),('CX',(6,7),21),('CX',(6,7),22),
       ('CX',(3,4),22),('CX',(3,4),23),('CX',(20,21),22),('CX',(20,21),23)]
# Emptying tick 22: q8's RX goes (reuse of the MX8 c7 state), and the five gadget pairs that straddle it.
o2=collapse(ops,22,[('RX',(8,),22)]+[p for p in pairs if p[2]==22]+[p for p in pairs if p[2]!=22 and False]) if False else None
o2=copy.deepcopy(ops)
for k,qs,t in [('RX',(8,),22)]+pairs: o2.remove(find(o2,k,qs,t))
# pairs at (22,23): after removing both halves tick 22 is empty
for o in o2:
    if o.time>22:o.time-=1
check_conflicts(o2)
s=emit('q8reuse',o2,copy.deepcopy(dets),md,dict(base='MAIN/v36f',removed=['RX8@22']+[f'{k}{qs}@{t}' for k,qs,t in pairs],shift='t>22 -1'))
print(certify(s)); print(json.dumps({k:v for k,v in atoms(s).items() if k!='offending_gates'}))
# control: same pair drops without the reuse (no compression), to separate the pair price from the reuse gain
o3=copy.deepcopy(ops)
for k,qs,t in pairs: o3.remove(find(o3,k,qs,t))
s3=emit('v36f_nopairs22',o3,copy.deepcopy(dets),md,dict(base='MAIN/v36f',removed=[f'{k}{qs}@{t}' for k,qs,t in pairs]))
print(certify(s3)); print(atoms(s3)['prediction'])
