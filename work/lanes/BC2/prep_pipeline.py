import json
from pathlib import Path
import subprocess
import sys

import score

P='/home/jihoon/competitions/quantumn/.venv/bin/python'
for p in sorted(Path('.').glob('window*.qasm')):
    if '_m' in p.stem: continue
    meta=json.loads(p.with_suffix('.json').read_text())
    subprocess.run([P,'../MAIN/minit.py',p.stem,'.','27,29'],check=True)
    stem=p.stem+'_m27_29'
    meta['minit_requested']=[27,29]
    Path(stem+'.json').write_text(json.dumps(meta,indent=2))
    score.score(stem,12)
