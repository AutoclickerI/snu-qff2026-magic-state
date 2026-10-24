import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'upstream/snu-qff2026-problem'));sys.path.insert(0,str(HERE/'inputs/EVAL'))
from exact2 import Eval
for name in ['grid_cp20','grid_routed']:
 p=HERE/(name+'.qasm');j=json.loads(p.with_suffix('.json').read_text());ev=Eval(p.read_text(),j['data_qubits']);bad=[]
 for i,v in enumerate(ev.fp*ev.n_single):
  if v>1e-15:bad.append(dict(contribution=float(v),label=ev.fault_label(i)))
 out=dict(c1_p=float((ev.fp*ev.n_single).sum()),A1=float((ev.fp*(1-ev.a_single)).sum()),bad_singles=bad)
 p.with_suffix('.singles.json').write_text(json.dumps(out,indent=2)+'\n');print(name,out,flush=True)
