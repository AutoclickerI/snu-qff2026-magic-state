"""Complete-circuit screen of the 20 best exact A encoders on the fixed region."""
import json,os,sys,subprocess,time
from pathlib import Path
from build import build
from reuse_A import reuse
H=Path(__file__).resolve().parent;ROOT=H.parents[3];rows=json.loads((H/'A89_exact_raw.json').read_text())['top'];out=[]
for i,ap in enumerate(rows):
 if i==0:continue
 ap['cx']=sum(map(len,ap['ops']));f=H/f'A89_top{i}.json';f.write_text(json.dumps(ap));name=f'region89_k45_A{i}';stem=build(H/'r89_d10_k45.prep.json',name,a_prep=f);name+='_safe';reuse(stem,name,[18,19,21,26]);out.append(name)
(H/'encoder_sweep_stems.json').write_text(json.dumps(out))
