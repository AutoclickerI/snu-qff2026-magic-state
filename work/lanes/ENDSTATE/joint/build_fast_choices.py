from pathlib import Path
import json
from reuse_A import reuse
from zero_checks import add
H=Path(__file__).resolve().parent
reuse(H/'region89_k45_A0','region89_k45_A0_safe',[21,26,18,19])
reuse(H/'region89_k45','region89_k45_q18',[18])
reuse(H/'region89_k45_A0','region89_k45_A0_q15',[15])
add(H/'region89_k45_A0_safe','region89_k45_A0_safe_z')
(H/'fast_choices.json').write_text(json.dumps(['region89_k45_alap','region89_k45_q18','region89_k45_A0_alap','region89_k45_A0_safe','region89_k45_A0_safe_z']))
