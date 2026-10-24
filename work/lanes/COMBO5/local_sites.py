import json,subprocess
from pathlib import Path
from evaluate import score
HERE=Path(__file__).resolve().parent
base='clean_d14_late3_s0';meta=json.loads((HERE/(base+'.json')).read_text());dest=HERE/(base+'_init')
for q in (29,28,27,25,23,22):
    stem=dest/(base+f'_m{q}')
    stem.with_suffix('.json').write_text(json.dumps(dict(meta,first_use_measured=[q]),indent=2))
    score(stem,22,True)
    subprocess.run(['rsync','-az','-e','ssh -q -o ControlMaster=no -o ControlPath=none','--exclude','.submit_credentials',str(stem.with_suffix('.score.json')),str(stem.with_suffix('.json')),f'sunfish:{dest}/'],check=True)
