from common import *
import argparse
p=argparse.ArgumentParser();p.add_argument('stems',nargs='+');p.add_argument('--mode',default='alap');a=p.parse_args()
for stem in a.stems:
 try:
  c=read(stem);d,rec=schedule(c,mode=a.mode)
  if d:
   out=save(d,Path(stem).stem+'_'+a.mode);r=score(out)
   append_result(out.name,r,'Rank-three resource; complete native per-wire retiming '+json.dumps(rec));print(out.name,r,flush=True)
 except Exception as e:
  append_result(Path(stem).stem,{'error':repr(e)},'Retiming build error, not a physical exclusion');print(stem,repr(e),flush=True)
