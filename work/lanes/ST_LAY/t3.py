import lay3,sys,json
lay3.SEED=int(sys.argv[1]); mh=int(sys.argv[2])
r=lay3.solve(lay3.PRE,0.01,float(sys.argv[3]),int(sys.argv[4]),mh)
print(sys.argv[1:], r if isinstance(r,str) else (r[1],r[2],r[0]))
json.dump(r,open(f"t3_{sys.argv[1]}_{mh}.json","w"))
