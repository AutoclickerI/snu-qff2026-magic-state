import json
from pathlib import Path
from reuse_A import reuse
H=Path(__file__).resolve().parent;names=[]
for label,qs in [('same',[14,20,15,9]),('q13',[14,20,15,9,13]),('q21',[14,20,15,9,21]),('q27',[14,20,15,9,27])]:
 name='region2_reuse_'+label;reuse(H/'region2_d11',name,qs);names.append(name)
(H/'row2_variants_stems.json').write_text(json.dumps(names))
