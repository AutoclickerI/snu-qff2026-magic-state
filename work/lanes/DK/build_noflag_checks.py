import itertools,json
from build import BASE,DATA,build
from build_round import append_round
from schedule_alap import alap
from tprep.exact import verify
from tprep.parse import declarations
for keep in [(),('TA',),('TB',),('PA',),('PB',),('TA','TB'),('TA','PB'),('TB','PA'),('PA','PB')]:
 stem='dk_noflag_' + ('none' if not keep else '_'.join(keep)) + '_alap'
 c=build(barriers=True,keep=keep,steane_flag=False,rm_verifier=True);append_round(c);c=alap(c)
 _,s,j=c.write(stem,dict(protocol='DK two-block plus verified round',variant=stem,kept_checks=list(keep),steane_flag=False,status='grid-free'))
 f,p=declarations(s);ex=verify(s,DATA,frame=f,postselect=p,n_qubits=36);j.update(noiseless=ex,status='verified grid-free' if not ex['errors'] else 'INVALID');(BASE/(stem+'.json')).write_text(json.dumps(j,indent=2)+'\n');print(stem,j['cx'],ex['errors'])
