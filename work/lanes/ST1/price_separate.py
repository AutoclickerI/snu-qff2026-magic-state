from common import *
import separate_bc as sb,argparse
p=argparse.ArgumentParser();p.add_argument('plans',nargs='+');a=p.parse_args()
for path in map(Path,a.plans):
 x=json.loads(path.read_text());name=path.name.removesuffix('.solver.json')
 try:
  stem=sb.emit(x,name);r=score(stem);print(name,r,flush=True);append_result(name,r,'Fully emitted separate BC plan; 11-CX encoders and interleaved teleports. Raw first-witness timing.')
  for mode in ['alap','near']:
   c=read(stem);d,rec=schedule(c,mode=mode)
   if d:
    ss=save(d,name+'_'+mode);r=score(ss);append_result(ss.name,r,'Separate blocks; native per-wire retiming '+mode+'; '+json.dumps(rec));print(ss,r,flush=True)
 except Exception as e:
  append_result(name,dict(error=repr(e)),'Separate-plan build/pricing failure; not a measured physical negative.');print(name,repr(e),flush=True)
