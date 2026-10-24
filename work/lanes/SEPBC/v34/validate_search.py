from release import *
from mutations import route14
import collections
target={0}
for x in [85,102,120,7]:target|={y^x for y in list(target)}
rows=[]
for rec in json.loads((V/'layer_recipes.json').read_text()):
 c=route14(getbase(0))if rec['mode']>=10 else getbase(0);rr=release(c);mode=rec['mode']%10;piv=set(rec['pivots']);rxqs=(2,9)if rec['mode']>=10 else(2,14)
 ready={q:rr[q]['earliest']+(2-int(mode>=3 and q in rxqs)+int(mode==0 or(mode in(1,3)and q in(1,2,8)))if q in piv else 1+int(q in rxqs))for q in A};span={0}
 for q in piv:span|={x^(1<<A.index(q))for x in list(span)}
 busy=collections.defaultdict(set)
 for t,u,v in rec['ops']:
  assert t>=ready[u]and t>=ready[v]and t<rec['R'];assert not busy[t]&{u,v};busy[t]|={u,v};i,j=A.index(u),A.index(v);span={x^(((x>>i)&1)<<j)for x in span}
 assert span==target,rec
 rows.append(dict(mode=rec['mode'],R=rec['R'],pivots=rec['pivots'],CX=len(rec['ops'])))
for rec in json.loads((V/'measure_calibration.json').read_text()):
 span={0}
 for q in rec['pivots']:span|={x^(1<<A.index(q))for x in list(span)}
 for t,kind,q,other in rec['mbops']:
  i=A.index(q)
  if kind==0:j=A.index(other);span={x^(((x>>i)&1)<<j)for x in span}
  elif kind==1:assert any(x>>i&1 for x in span);span={x for x in span if not(x>>i&1)}
  elif kind==2:assert all(not(x>>i&1)for x in span);span|={x^(1<<i)for x in list(span)}
 assert span==target,rec
out=dict(unitary_witnesses=len(rows),unitary_R43_witnesses=sum(r['R']<=43 for r in rows),measurement_R44_calibration_witnesses=len(json.loads((V/'measure_calibration.json').read_text())),independent_span_replay=True,ready_times_checked=True,disjoint_layers_checked=True,scope='Fixed seven-cell A graph, recorded prefix-release bounds and preparation modes; no global architecture claim.')
(V/'search_validation.json').write_text(json.dumps(out,indent=2));print(out)
