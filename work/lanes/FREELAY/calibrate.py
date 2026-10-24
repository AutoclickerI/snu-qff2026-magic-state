"""Price native exposure features against completed full-circuit exact screens.

Calibration is an in-sample fit, not a rank oracle. The report retains residuals.
"""
from co_design import *
import numpy as np
from scipy.optimize import nnls
def features(name):
 path=HERE/name;meta=json.loads(path.with_suffix('.json').read_text());txt=path.with_suffix('.qasm').read_text()
 h,r,d=S.qasm_ops(txt);us=S.fold_units(r);ts=native_times(txt,us);R=meta['R'];pre=set(meta['prefix_unit_indices'])
 lastpre={q:max(t for j,(u,t) in enumerate(zip(us,ts)) if j in pre and q in u.qs) for q in D0}
 firstpre={q:min(t for j,(u,t) in enumerate(zip(us,ts)) if j in pre and q in u.qs) for q in D0}
 life={}
 for k,cells in [('a',AC),('bc',BCELLS+CCELLS)]:
  init={q:max(t for j,(u,t) in enumerate(zip(us,ts)) if j not in pre and t<R and u.qs==(q,) and u.name in ['RESET','RX','MEASURE']) for q in cells}
  life[k]=sum(R-t for t in init.values())
 return dict(R=R,pre_end=max(ts[j] for j in pre),pre_exposure=sum(R-ts[j] for j in pre),data_exposure=sum(R-firstpre[q] for q in D0),data_wait=sum(R-lastpre[q]-1 for q in D0),a_exposure=life['a'],bc_exposure=life['bc'],cx=meta['cx'],data_hops=6,block_teleports=0)

def main():
 rows=[]
 for p in sorted(HERE.glob('joint*.score.json')):
  name=p.name.removesuffix('.score.json');s=json.loads(p.read_text())
  if 'total' in s and abs(s['c1'])<1e-12:rows.append(dict(name=name,features=features(name),exact=s['total']))
 # A small nonnegative linear calibration to native exposures; include the round floor
 # as a constant feature, and report every predicted-versus-measured difference.
 keys=['pre_exposure','data_wait','data_exposure','a_exposure','bc_exposure','cx']
 X=np.array([[r['features'][k] for k in keys] for r in rows],float);scale=X.mean(axis=0)
 coef,residual=nnls(X/scale,np.array([r['exact']-2.865e-5 for r in rows]));weights=coef/scale
 for r,xx in zip(rows,X):r.update(predicted=2.865e-5+float(xx@weights),residual=(2.865e-5+float(xx@weights))-r['exact'])
 out=dict(note='In-sample nonnegative fit; too few circuits for out-of-family validation. Applied to search proxies only, never final ranking.',floor=2.865e-5,weights=dict(zip(keys,map(float,weights))),rows=rows)
 (HERE/'calibration.json').write_text(json.dumps(out,indent=1));print(json.dumps(out,indent=1))
if __name__=='__main__':main()
