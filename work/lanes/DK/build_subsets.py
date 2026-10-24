import itertools,json
from build import build,BASE,DATA
from tprep.exact import verify
from tprep.parse import declarations
names=['TA','TB','PA','PB']
for n in range(5):
 for keep in itertools.combinations(names,n):
  stem='dk_' + ('none' if not keep else '_'.join(keep))
  c=build(barriers=True,keep=keep)
  _,s,j=c.write(stem,dict(protocol='Daguerre-Kim two-block RM15-to-Steane switch',source='arXiv:2410.07327v3 Figs. 3-7, Tables IV-VII',variant=stem,kept_checks=list(keep),status='grid-free adjacency bypass only'))
  f,p=declarations(s);ex=verify(s,DATA,frame=f,postselect=p,n_qubits=36)
  j.update(noiseless=ex,status='verified grid-free' if not ex['errors'] else 'INVALID')
  (BASE/(stem+'.json')).write_text(json.dumps(j,indent=2)+'\n')
  print(stem,'cx',j['cx'],'meas',j['measurements'],'rank',ex.get('rank'),'errors',ex['errors'])
