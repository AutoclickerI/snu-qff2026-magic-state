from fr import *
ops,dets,md=load(V36F)
s=emit('v36f_rt',ops,dets,md,dict(kind='roundtrip'))
t=time.time();print(certify(s,singles=True),time.time()-t)
print(atoms(s)['prediction'])
