"""Move fresh hop-destination initializations immediately before their first CX.
The route's minimum R is unchanged; avoids charging an arbitrary ASAP-init wait.
"""
import build as b
import json,copy
for folder in [b.OUT,b.OUT/'order210']:
 m=json.loads((folder/'r_hops_hop.json').read_text());ops=copy.deepcopy(m['units']);changes=[]
 for x in ops:
  if x['tag']=='hop' and (set(b.bits(x))&{43,45,46} or b.name(x)=='RESET'):
   q=b.qs(x)[0];nxt=min(y['t'] for y in ops if y['t']>x['t'] and q in b.qs(y))
   changes.append(dict(q=q,old=x['t'],new=nxt-1));x['t']=nxt-1
 tail=b.S.qasm_ops((folder/'r_hops_hop.qasm').read_text())[2]
 b.OUT=folder;b.emit('r_hops_hop_alap',ops,tail,m['data_qubits'],m['R'],'Original hop paths at earliest feasible R, fresh destination preparation just before first use',dict(init_changes=changes))
