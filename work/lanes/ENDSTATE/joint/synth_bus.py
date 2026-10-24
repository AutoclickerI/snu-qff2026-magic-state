"""Fixed-region search with one logical shortcut expanded as a measured-helper CX."""
import sys,json,argparse
from pathlib import Path
from synth_resource import F,run,H
orig=F.S.nb
F.S.nb=lambda q:list(dict.fromkeys(orig(q)+([8]if q==1 else[1]if q==8 else[])))
a=argparse.Namespace(row=89,out='r89_bus_d9',depth=9,cap=48,seed=17,seconds=240,hint=None,eager=True)
run(a)
f=H/(a.out+'.prep.json')
if f.exists():
 d=json.loads(f.read_text());d['remote_helper']=2;d['remote_edges']=[[1,8],[8,1]];f.write_text(json.dumps(d,indent=2))
