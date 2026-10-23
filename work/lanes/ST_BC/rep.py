import json,sys
d=json.load(open(sys.argv[1]))
for q in(4,6,13,19):
    print(q,[i+1 for i,L in enumerate(d["ops"]) if any(q in e for e in L)])
print(len(d["ops"]),sum(map(len,d["ops"])),d["pivots"])
