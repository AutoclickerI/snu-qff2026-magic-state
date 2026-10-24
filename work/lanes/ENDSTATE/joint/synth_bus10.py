import argparse,json
from synth_resource import F,run,H
orig=F.S.nb;F.S.nb=lambda q:list(dict.fromkeys(orig(q)+([8]if q==1 else[1]if q==8 else[])))
Base=F.Model
class Model(Base):
 def __init__(self,*args,**kw):
  super().__init__(*args,**kw);self.add([ss[e]for ss in self.sel for e in ((1,8),(8,1))])
F.Model=Model
a=argparse.Namespace(row=89,out='r89_bus_d10',depth=10,cap=45,seed=21,seconds=120,hint=str(H/'r89_d10_k45.prep.json'),eager=True);run(a)
f=H/(a.out+'.prep.json')
if f.exists():
 d=json.loads(f.read_text());d['remote_helper']=2;d['remote_edges']=[[1,8],[8,1]];f.write_text(json.dumps(d,indent=2))
