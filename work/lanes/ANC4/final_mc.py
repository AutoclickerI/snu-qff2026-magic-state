import sys,os,re,json,subprocess
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
rank=[]
for p in HERE.glob('grid_*.exact.log'):
 name=p.name.removesuffix('.exact.log');c=HERE/(name+'.check.json')
 if not c.exists():continue
 j=json.loads(c.read_text())
 if j['format_errors'] or j['class_error'] or j['correctness_errors'] or j['acceptance']<0.5:continue
 m=re.search(r'1-F \(to 3rd order\) = (\S+)',p.read_text())
 if m:rank.append((float(m[1]),name))
rank.sort();selected=rank[:2];(HERE/'mc_selection.json').write_text(json.dumps(dict(screening=rank,selected=selected),indent=2)+'\n');print('MC candidates selected by exact screen:',selected,flush=True)
for score,name in selected:
 print('capacity:',os.cpu_count(),os.getloadavg(),flush=True)
 procs=max(1,min(8,int(os.cpu_count()-os.getloadavg()[0]-1)))
 with (HERE/(name+'.mc.log')).open('w') as f:
  subprocess.run([str(ROOT/'.venv/bin/python'),str(HERE/'mc3.py'),str(HERE/(name+'.qasm')),str(procs)],stdout=f,stderr=subprocess.STDOUT,check=True)
 print(name,json.loads((HERE/(name+'.mc.json')).read_text())['mean'],flush=True)
