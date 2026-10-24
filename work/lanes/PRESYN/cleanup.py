"""Run only after all lane jobs exit: discard regenerable circuit/cache bulk."""
from pathlib import Path
import json,shutil
OUT=Path(__file__).resolve().parent
mc=json.loads((OUT/'mc_results.json').read_text())
keep={'best','base',*[n for n,s in mc.items()if len(s)==3]}
removed=[]
for f in OUT.glob('*.qasm'):
 if f.stem not in keep:
  removed.append(f.name);f.unlink();j=f.with_suffix('.json')
  if j.exists():j.unlink()
for d in ['.xtim_cache','__pycache__','inputs/__pycache__']:
 p=OUT/d
 if p.exists():shutil.rmtree(p)
(OUT/'cleanup.json').write_text(json.dumps(dict(kept_circuits=sorted(keep),removed_circuits=removed),indent=2)+'\n')
print('kept',len(keep),'removed',len(removed))
