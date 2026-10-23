import lay3,sys
bl=sys.argv[1]; mh=int(sys.argv[2])
# feasibility: prefer = None-ish -> zero cost
r=lay3.solve([lay3.PRE[0]]*7 if False else lay3.PRE,0,float(sys.argv[3]),int(sys.argv[4]),mh,None,tuple(bl))
print(bl,mh, r if isinstance(r,str) else (r[1],r[2],r[0]),flush=True)
