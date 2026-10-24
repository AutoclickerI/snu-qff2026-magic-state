import os,sys,json,time
sys.dont_write_bytecode=True
from pathlib import Path
ROOT=Path('/home/jihoon/competitions/quantumn');HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'work/lanes/DR'))
from synth import synth,check
from steane_full import GENS
assert os.getloadavg()[0]<os.cpu_count()-2
l=json.loads((ROOT/'work/lanes/LAYOUT3/hopt_s4_r0_c2.json').read_text());B=l['b'];F=[33,34,25,31]
for depth in [12,16]:
 t=time.time();res=synth(B,GENS,B+F,depth,seconds=120,workers=1)
 print(depth,round(time.time()-t,1),res,flush=True)
 if res:
  p=dict(ops=res[0],pivots=res[1],status=res[2]);assert check(B,GENS,B+F,p['ops'],p['pivots']);(HERE/f'grid_B_d{depth}.json').write_text(json.dumps(p,indent=2)+'\n')
