"""Transport terminal transversal Tdg with the data through an exact coherent hop."""
import json
from pathlib import Path
from build import build
from reuse_A import reuse
from retime import run
H=Path(__file__).resolve().parent;P=H.parent
p=json.loads((P/'v30f.prefix.json').read_text());data=p['data_qubits'];drop=[]
for q in data:
 seq=[i for i,o in enumerate(p['ops'])if q in o['qs']];i=seq[-1];assert p['ops'][i]['name']=='TDG',p['ops'][i];drop.append(i)
p['ops']=[o for i,o in enumerate(p['ops'])if i not in drop];p['note']='Terminal Tdg is transported exactly with each data wire and reinserted at its final cell before the round.';(P/'v30f_hopT.prefix.json').write_text(json.dumps(p,indent=1))
for ai in(0,1):
 ap=H/('A89_0.json'if ai==0 else'A89_top1.json');s=build(H/'r89_d10_k45.prep.json',f'region89_hopT_A{ai}',a_prep=ap,hop_t=True);reuse(s,s.name+'_safe',[18,19,21,26])
(H/'hopT_stems.json').write_text(json.dumps([f'region89_hopT_A{i}_safe'for i in(0,1)]))
