from part1 import *
ROWS[:]=json.loads((HERE/'part1_rows.json').read_text());ERRORS=[]
def record(name,fn):
 try:row(name,fn)
 except ValueError as e:
  if 'verification overlaps the encoder' not in str(e) and 'non-deterministic' not in str(e):raise
  ERRORS.append(dict(name=name,error=str(e)));print('INFEASIBLE',name,str(e).splitlines()[0],flush=True)
  (HERE/'part1_infeasible.json').write_text(json.dumps(ERRORS,indent=2))
for i,S in enumerate(steane.W3):record(f'DR Steane single W3[{i}]',lambda S=S:steane.score(ver=(S,)))
for i,j in itertools.combinations(range(len(steane.W3)),2):record(f'DR Steane pair W3[{i},{j}]',lambda i=i,j=j:steane.score(ver=(steane.W3[i],steane.W3[j])))
sched={int(q):[(t,typ,set(s)) for t,typ,s in v] for q,v in json.loads((ROOT/'work/lanes/DR/sched_xlast.json').read_text()).items()}
for ver in (False,True):record(f'DR poc xlast verified={ver}',lambda v=ver:poc.proxy(sched,verify=v))
for clean_z in (False,True):record(f'DR clean xlast clean_z={clean_z}',lambda z=clean_z:poc.proxy(sched,builder=lambda sc:poc.build_clean(sc,clean_z=z)))
for ver in (False,True):record(f'DR poc default verified={ver}',lambda v=ver:poc.proxy(verify=v))
for sa in stav.SPECS:
 for sd in ('std','exact'):
  for gap in (2,6):record(f'ST_AV A={sa} D={sd} pin=0 gap={gap}',lambda a=sa,d=sd,g=gap:stav.score(a,d,0,gap=g))
ROWS[:]=list({r['name']:r for r in ROWS}.values());(HERE/'part1_rows.json').write_text(json.dumps(ROWS,indent=2))
