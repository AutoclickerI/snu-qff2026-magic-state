from pass5 import *
E.configure(R/('basis_'+sha(C/'base')+'.json'),12)
p=R/'wide_r1_menu.json';es=json.loads(p.read_text());old=json.loads((H/'res37f/wide_r4_funding.json').read_text())['buyers'];buyers=[i for i in old if i in es]
core=['herald:RX7@0:v0','herald:RX8@37:v0'];tasks=[core+list(x)for n in range(3)for x in itertools.combinations(buyers,n)]
rs=batch(C/'base',p,tasks,'pilot_r1_fund',10)
print(json.dumps(dict(event='pilot_funded',best=choose(rs,record(C/'base','control')),count=len(rs))),flush=True)
