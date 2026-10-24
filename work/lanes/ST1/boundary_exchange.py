"""Fuse terminal cultivation cat checks with the data's first native hop.

CX(c,d); MX(c); initialize(c,0); CX(d,c); CX(c,d) followed by a
zero-source watch is replaced by CX(d,c); CX(c,d); MX(d). This is the
same conditional input-data instrument for arbitrary joint cat/input states.
The old source is reset if subsequently reused as an A qubit.
"""
from common import *
import argparse
p=argparse.ArgumentParser();p.add_argument('stem');p.add_argument('--out',required=True);a=p.parse_args();base=json.loads(Path(a.stem).with_suffix('.plan.json').read_text())
def fuse(c,d,cat):
 c=copy.deepcopy(c);ops=c['ops'];edge=lambda o,p:unit(o).name=='CX'and S.name_qs(o['lines'][0])[1]==p
 f=max(i for i,o in enumerate(ops)if o['t']<c['meta']['R']and edge(o,(d,cat)));b=next(i for i,o in enumerate(ops)if i>f and edge(o,(cat,d)));ci=max(i for i,o in enumerate(ops[:f])if edge(o,(cat,d)));mi=next(i for i in range(ci+1,f)if unit(ops[i]).name=='MX'and unit(ops[i]).qs==(cat,));ri=next(i for i in range(mi+1,f)if unit(ops[i]).name=='RESET'and unit(ops[i]).qs==(cat,));wi=next(i for i in range(b+1,len(ops))if unit(ops[i]).name=='MEASURE'and unit(ops[i]).qs==(d,));assert ops[wi]['t']<c['meta']['R'];oldbit=int(re.search(r'c\[(\d+)\]',' '.join(ops[wi]['lines']))[1]);related=[l for l in c['tail']if oldbit in list(map(int,re.findall(r'c\[(\d+)\]',l)))];assert related==[f'// DETECTOR c[{oldbit}]'],related
 assert all(d not in unit(o).qs for o in ops[ci+1:f]),[(o['t'],o['lines'])for o in ops[ci+1:f]if d in unit(o).qs]
 t=ops[ci]['t'];ops[ci]['lines']=[f'cx q[{d}],q[{cat}];'];ops[b]['t']=t+1;ops[mi]['lines']=rename(ops[mi]['lines'],{cat:d});ops[mi]['t']=t+2;c['tail'].remove(related[0]);drop={f,ri}
 later=[o for o in ops[wi+1:]if d in unit(o).qs]
 if later:ops[wi]['lines']=[f'reset q[{d}];'];ops[wi]['tag']='exchange_source_reset'
 else:drop.add(wi)
 c['ops']=[o for i,o in enumerate(ops)if i not in drop];c['meta']['boundary_exchanges']=c['meta'].get('boundary_exchanges',[])+[dict(data_source=d,cat_destination=cat,removed_watch=oldbit,source_reused=bool(later))];return c
for label,pairs in [('67',[(6,7)]),('1415',[(14,15)]),('both',[(6,7),(14,15)])]:
 try:
  c=copy.deepcopy(base)
  for d,cat in pairs:c=fuse(c,d,cat)
  c['ops'].sort(key=lambda o:o['t']);name=a.out+'_'+label;st=save(c,name);r=score(st);append_result(name,r,'New full-prefix/round boundary exchange; terminal cat measurement moves to the old data cell. Removed zero-source watch; explicit reset retained where A subsequently reuses that cell.');print(name,json.dumps(r),flush=True)
  d,receipt=schedule(c,mode='alap')
  if d:
   st=save(d,name+'_alap');r=score(st);append_result(name+'_alap',dict(schedule=receipt,**r),'Full native rescheduling after the new cultivation/data exchange. Exact complete-circuit objective, not hop count, determines the result.');print(name+'_alap',json.dumps(r),flush=True)
 except Exception as e:append_result(a.out+'_'+label,dict(error=repr(e)),'Boundary-exchange construction failure; not a physical family closure.');print(label,repr(e),flush=True)
