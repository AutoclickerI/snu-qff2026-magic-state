import sys,runpy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));import pop35_support as v
# Shared finalist machinery imports v35 campaign; set the final gate baseline
# back to v35b after import while retaining existing native helper definitions.
import v35_finalize as f
v.a.BASE_LOSS=4.376021340833061e-5;v.a.BASE_ACC=.5016883498058476
for st in sys.argv[1:-1]:
 p=Path(st).resolve();g=f.gate(p)
 if g['gated']:f.mc(p,int(sys.argv[-1]))
