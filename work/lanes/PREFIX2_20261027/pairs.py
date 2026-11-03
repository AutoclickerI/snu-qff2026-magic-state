"""Exact order-two fault-pair ledger for zero-first-order circuits.

Canonicalizes the complete detector row space, buckets by the deterministic
identity-projector syndrome, and evaluates only pairs able to pass that syndrome.
Mutually exclusive alternatives in the same physical channel are subtracted.
The contribution fields include p=0.001 probabilities; divide by p**2 for c2.
"""
import os,sys,json,time,math
from pathlib import Path
from collections import defaultdict
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from qtools.evaluator import frontend as fa
from qtools.evaluator import sparse_walsh as sw

def audit(stem,out=None):
 st=Path(stem);fa.DATA=json.loads(st.with_suffix('.json').read_text())['data_qubits'];ops,ds=fa.parse_current(st.with_suffix('.qasm').read_text());m=fa.make_model(ops,ds);eng=fa.Engine(m)
 sw.canonicalize_detector_rows(m,eng);eng=fa.Engine(m)
 active=sum(1<<i for i,p in enumerate(eng.projs) if p[:2]!=(0,0))
 full=(1<<len(ds))-1;inactive=full^active
 groups=defaultdict(list)
 for i,f in enumerate(m.faults):groups[(f['s'],f['d'],f['e'])].append(i)
 G=[];buckets=defaultdict(list)
 for key,ids in groups.items():
  bychan=defaultdict(float)
  for i in ids:bychan[m.faults[i]['chan']]+=m.faults[i]['p']
  g=dict(key=key,ids=ids,weight=sum(m.faults[i]['p'] for i in ids),channels=dict(bychan))
  buckets[key[1]&inactive].append(len(G));G.append(g)
 tables={};total=0;positive=0;tested=0;pairrows=[];faultweight=defaultdict(float);regionweight=defaultdict(float)
 def table(s,d):
  key=(s,d)
  if key not in tables:tables[key]=eng.ntable(s,d)
  return tables[key]
 def brief(i):
  f=m.faults[i];op=ops[f['ins']]
  return dict(id=i,channel=f['chan'],t=op.time,kind=op.kind,gate_qs=list(op.qs),fault_qs=f['qs'],pauli=f['pauli'],p=f['p'],record_flips=f['record_flips'],s=f['s'],d=f['d'],e=f['e'])
 for bi,(det,ids) in enumerate(buckets.items()):
  for a,ia in enumerate(ids):
   g=G[ia]
   for ib in ids[a+1:]:
    h=G[ib];s=g['key'][0]^h['key'][0];d=g['key'][1]^h['key'][1];e=g['key'][2]^h['key'][2]
    tested+=1;A,n=table(s,d)
    loss=0 if n is None else float(n[e])
    if loss<=1e-12:continue
    same=sum(p*h['channels'].get(c,0) for c,p in g['channels'].items())
    prob=g['weight']*h['weight']-same
    if prob<=1e-20:continue
    value=prob*loss;total+=value;positive+=1
    pairrows.append(dict(value=value,loss_numerator=loss,acceptance=A,gids=[ia,ib],weight=prob,
       a=[brief(i) for i in sorted(g['ids'],key=lambda i:-m.faults[i]['p'])[:12]],
       b=[brief(i) for i in sorted(h['ids'],key=lambda i:-m.faults[i]['p'])[:12]]))
    for gg,hh in [(g,h),(h,g)]:
     for i in gg['ids']:
      f=m.faults[i];faultweight[i]+=f['p']*(hh['weight']-hh['channels'].get(f['chan'],0))*loss
    # Region/Pauli decomposition accumulates all mutually exclusive-aware pairs.
    for i in g['ids']:
     f=m.faults[i];oi=ops[f['ins']]
     for j in h['ids']:
      z=m.faults[j]
      if f['chan']==z['chan']:continue
      oj=ops[z['ins']]
      label=tuple(sorted((f'{oi.time:02d}:{oi.kind}',f'{oj.time:02d}:{oj.kind}')))
      regionweight[label]+=f['p']*z['p']*loss
  if bi%40==0:print('progress',bi,len(buckets),'pairs',tested,'tables',len(tables),'N2',total,flush=True)
 pairrows.sort(key=lambda r:-r['value'])
 faults=[dict(value=v,**brief(i)) for i,v in sorted(faultweight.items(),key=lambda z:-z[1])]
 res=dict(stem=str(st),second_order_contribution_at_p001=total,c2=total/1e-6,groups=len(G),faults=len(m.faults),channels=len(m.chans),tested_group_pairs=tested,harmful_group_pairs=positive,kernel_tables=len(tables),top_pairs=pairrows[:100],fault_attribution=faults,region_pairs=[dict(a=k[0],b=k[1],value=v) for k,v in sorted(regionweight.items(),key=lambda z:-z[1])])
 p=Path(out) if out else st.with_suffix('.pairs.json');p.write_text(json.dumps(res,indent=2)+'\n');print('DONE',json.dumps({k:v for k,v in res.items() if k not in ['top_pairs','fault_attribution','region_pairs']}),flush=True)
 return res
if __name__=='__main__':audit(sys.argv[1],sys.argv[2] if len(sys.argv)>2 else None)
