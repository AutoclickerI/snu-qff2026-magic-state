from pathlib import Path
from build import build
from retime import run
from reuse_A import reuse
from zero_checks import add
H=Path(__file__).resolve().parent
base=build(H/'r89_d10_k45.prep.json','region89_k45');run(base,base.name+'_alap');reuse(base,base.name+'_reuseA')
a=build(H/'r89_d10_k45.prep.json','region89_k45_A0',a_prep=H/'A89_0.json');run(a,a.name+'_alap');reuse(a,a.name+'_reuse');add(H/(a.name+'_reuse'),a.name+'_reuse_z')
