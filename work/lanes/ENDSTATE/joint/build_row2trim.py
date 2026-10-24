from pathlib import Path
import json
from build import build
from reuse_A import reuse
from retime import run
H=Path(__file__).resolve().parent
s=build(H/'r2_d11_k56.prep.json','region2_k56');run(s,s.name+'_alap');reuse(s,s.name+'_same',[14,20,15,9])
(H/'row2_trim_stems.json').write_text(json.dumps(['region2_k56_alap','region2_k56_same']))
