import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
from generate import build,direct,PRE_DATA
HERE=Path(__file__).resolve().parent
rows=[[0,1,2],[0,3,4],[1,3,5],[0,2,4,6]];ll=direct(rows,4)
(HERE/'weak_schedule.json').write_text(json.dumps(dict(parities=rows,layers=ll),indent=2)+'\n')
for R in [33,39]:
 txt=build('anc4',R,layers=ll);p=HERE/'gf'/f'weak4_{R}';p.with_suffix('.qasm').write_text(txt);p.with_suffix('.json').write_text(json.dumps(dict(data_qubits=PRE_DATA,grid_free=True,R=R,variant='weak4',cx=txt.count('\ncx '))))
