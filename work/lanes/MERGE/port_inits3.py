from pass3 import *
from measured_init import convert_init
def build(stem,tag):
 b=M.read(stem);tasks=[];success=[];invalid=[]
 sites=[(3,21),(10,26),(11,25),(13,21),(16,1),(16,2),(19,21),(19,17),(19,16),(25,13),(41,31)]
 for t,q in sites:
  try:
   i=next(i for i,o in enumerate(b['ops'])if o['t']==t and M.unit(o).qs==(q,)and M.unit(o).name in ['RESET','RX'])
   result=convert_init(b,i)
   if result is None:raise ValueError('non-stabilizer logical byproduct')
   c,detail=result;st=save(c,f'{tag}_q{q}t{t}',dict(kind='GLOBAL measured source transport',details=detail))
   success.append((t,q));tasks.append(dict(stem=str(st),why=dict(kind='GLOBAL source',base=str(stem),details=detail)))
  except Exception as ex:invalid.append(dict(t=t,q=q,error=repr(ex)))
 c=copy.deepcopy(b);steps=[]
 for t,q in success:
  i=next(i for i,o in enumerate(c['ops'])if o['t']==t and M.unit(o).qs==(q,)and M.unit(o).name in ['RESET','RX'])
  result=convert_init(c,i)
  if result is None:invalid.append(dict(t=t,q=q,error='joint byproduct changed'));continue
  c,detail=result;steps.append(detail)
 st=save(c,f'{tag}_all',dict(kind='GLOBAL all eligible measured source transports',steps=steps));tasks.append(dict(stem=str(st),why=dict(kind='GLOBAL joint sources',base=str(stem),steps=steps)))
 dump(R/f'{tag}_tasks.json',tasks);dump(R/f'{tag}_invalid.json',invalid)
 print(json.dumps(dict(tag=tag,tasks=len(tasks),invalid=invalid)),flush=True)
if __name__=='__main__':build(Path(sys.argv[1]),sys.argv[2])
