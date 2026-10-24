from pathlib import Path
import json,sys,subprocess
V=Path(__file__).resolve().parent
todo=[]
for p in V.glob('*.screen.json'):
 name=p.name.removesuffix('.screen.json');r=json.loads(p.read_text())
 if not(V/(name+'.allorders.json')).exists()and not r.get('invalid_cubic'):todo.append((r['total'],name))
names=[n for _,n in sorted(todo)];(V/'remaining_rank_manifest.json').write_text(json.dumps(names,indent=2));print('Remaining all-orders prices',len(names),flush=True)
if names:subprocess.run([sys.executable,str(V/'rank.py'),*names,'--procs','6'],check=True)
