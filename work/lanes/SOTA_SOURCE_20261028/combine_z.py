import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import sys,json,itertools,concurrent.futures
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[2]
for d in ('work/tools','work/lanes/PREFIX20261027','work/lanes/T14'):sys.path.insert(0,str(R/d))
from qcirc import parse,save
from qtools import price
from qtools.validity import raw_check
from search_phase import singles
P=H/'cand/zmax_10_11_4_17';D=json.loads(P.with_suffix('.json').read_text())['data_qubits'];base,dd=parse(P.with_suffix('.qasm').read_text());bit=max(u['b'] for u in base if u['b'] is not None)+1
checks=[(1,0,8,22),(14,20,19,22),(16,22,4,9),(16,22,12,17)];jobs=[v for n in range(1,5)for v in itertools.combinations(checks,n)]
def run(subset):
 ops=list(base);dets=list(dd)
 for i,(target,flag,a,b) in enumerate(subset):
  ops += [dict(k='R',q=(flag,),t=a-1,b=None),dict(k='CX',q=(target,flag),t=a,b=None),dict(k='CX',q=(target,flag),t=b,b=None),dict(k='M',q=(flag,),t=b+1,b=bit+i)];dets.append([bit+i])
 name='combo_'+'_'.join(f'{q}_{f}_{a}_{b}'for q,f,a,b in subset)
 try:
  st=save(H/'cand'/name,ops,dets,D,dict(source='Parallel compatible temporal Z echo flags',checks=subset));raw=raw_check(st.with_suffix('.qasm').read_text(),D)
  if not raw['ok']:return dict(name=name,raw=False)
  c1,harm=singles(st);p=price(st,1);return dict(stem=str(st),checks=subset,c1=c1,harmful=harm,loss=p['loss'],acceptance=p['acceptance'])
 except Exception as e:return dict(name=name,error=repr(e))
if __name__=='__main__':
 rows=[]
 with concurrent.futures.ProcessPoolExecutor(max_workers=2) as pool:
  for r in pool.map(run,jobs):rows.append(r);print(json.dumps(r),flush=True);(H/'combine_z_results.json').write_text(json.dumps(rows,indent=2)+'\n')
