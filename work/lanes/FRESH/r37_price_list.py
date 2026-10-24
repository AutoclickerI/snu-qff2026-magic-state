from r37 import *
import subprocess
stems=json.loads(Path(sys.argv[1]).read_text());rows=[]
for raw in stems:
 subprocess.run(['uptime'],check=True)
 s=Path(raw)
 r=dict(stem=str(s));r.update(price(s,int(sys.argv[2])));rows.append(r);print(json.dumps(r),flush=True)
(D/(Path(sys.argv[1]).stem+'_prices.json')).write_text(json.dumps(rows,indent=2))
