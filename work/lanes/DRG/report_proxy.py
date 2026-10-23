import sys,json
sys.path.insert(0,'/home/jihoon/competitions/quantumn/work/lanes/DR'); import poc
s={int(k):[(t,typ,frozenset(S)) for t,typ,S in v] for k,v in json.load(open('/home/jihoon/competitions/quantumn/work/lanes/DR/sched_zfirst.json')).items()}
for label,fn in [('hybrid_pair',lambda s:poc.build_hybrid(s,z_mode='pair')),('hybrid_cat1',lambda s:poc.build_hybrid(s,z_mode='cat1')),('clean',lambda s:poc.build_clean(s,clean_z=True))]:
 r,c=poc.proxy(s,builder=fn); print(label,r,c.n,c.n_2q())
