from pathlib import Path
from build import build
from reuse_A import reuse
H=Path(__file__).resolve().parent
s=build(H/'r2_correctable_d10_k42.prep.json','region2_correctable',a_prep=H/'A2_top2.json',require_clean=False);reuse(s,s.name+'_safe',[14,27,15,20]);reuse(H/(s.name+'_safe'),s.name+'_safe_dest',regions=('data_hops',),same_only=True)
