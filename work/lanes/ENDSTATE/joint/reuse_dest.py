from pathlib import Path
import json
from reuse_A import reuse
H=Path(__file__).resolve().parent;out=[]
for name in ('region2_k56_A2_safe','region2_k56_A6_safe','region2_k56_same'):
 target=name+'_dest';reuse(H/name,target,regions=('data_hops',),same_only=True);out.append(target)
(H/'destination_stems.json').write_text(json.dumps(out))
