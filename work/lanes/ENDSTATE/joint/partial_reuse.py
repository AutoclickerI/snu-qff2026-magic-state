import json
from pathlib import Path
from reuse_A import reuse
H=Path(__file__).resolve().parent;out=[]
for label,qs in [('M',[19,20,15,27]),('MX',[21,26,18]),('q18',[18]),('q19',[19]),('q20',[20]),('q27',[27]),('M18',[19,20,15,27,18])]:
 name='region89_k45_A0_reuse'+label;reuse(H/'region89_k45_A0',name,qs);out.append(name)
(H/'partial_reuse_stems.json').write_text(json.dumps(out))
