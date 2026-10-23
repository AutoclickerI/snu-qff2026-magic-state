import lay3,sys,json
bl=sys.argv[1]
r=lay3.solve(lay3.PRE,1,100,10,8,None,tuple(bl))
print(bl, r if isinstance(r,str) else (r[1],r[2],r[0]))
