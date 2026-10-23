import lay3,sys,time
t=time.time()
for mh in (8,):
    r=lay3.solve([0]*7,0,100,16,mh) if False else lay3.solve(lay3.PRE,0.01,60,32,mh)
    print(mh,r,time.time()-t)
