from pass5 import *
# Independent acceptance-buyer prices feed the next scheduled singles stage.
history=json.loads((R/'wide_history.json').read_text());cur=history[-1]['price'];rnd=history[-1]['round']+1
E.configure(R/('basis_'+sha(C/'base')+'.json'),12)
p=R/f'wide_r{rnd}_menu.json';es=json.loads(p.read_text());ids=[i for i,e in es.items()if e['fam']in ('mi','rm','patch')]
rs=batch(cur['stem'],p,[[i]for i in ids],f'wide_r{rnd}_singles',1,cur['loss'])
from wide5 import buyer
out=[r for r in rs if buyer(r,cur)];dump(R/f'wide_r{rnd}_early_buyers.json',out)
print(json.dumps(dict(event='acceptance_buyers_ready',round=rnd,screened=len(rs),buyers=len(out))),flush=True)
