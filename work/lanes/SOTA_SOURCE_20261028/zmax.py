import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import sys,json,concurrent.futures
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[2]
for d in ('work/tools','work/lanes/PREFIX20261027','work/lanes/T14'):sys.path.insert(0,str(R/d))
from qcirc import parse,save,adjacent
from qtools import price
from qtools.validity import raw_check
from search_phase import singles
P=H/'cand/zech_3_4_2_22';D=json.loads(P.with_suffix('.json').read_text())['data_qubits'];base,dd=parse(P.with_suffix('.qasm').read_text());occupied={(u['t'],q)for u in base for q in u['q']};bit=max(u['b'] for u in base if u['b'] is not None)+1
coords=[1,2,3,7,8,9,14,15,16,10,13];jobs=[]
for target in coords:
 if target==3:continue
 for flag in range(36):
  if flag in coords or not adjacent(flag,target):continue
  options=[]
  for a in range(2,23):
   for b in range(a+3,24):
    if (a,target)in occupied or (b,target)in occupied:continue
    if any((t,flag)in occupied for t in range(a-1,b+2)):continue
    # A target-controlled meter commutes with Z-diagonal source operations and target-as-control CX.
    if any(a<u['t']<b and target in u['q'] and (u['k'] in ('R','RX','M','MX') or u['k']=='CX' and u['q'][1]==target) for u in base):continue
    options.append((target,flag,a,b))
  # Keep maximal intervals, avoiding redundant contained windows.
  jobs += [x for x in options if not any(y[2]<=x[2] and y[3]>=x[3] and (y[2]<x[2] or y[3]>x[3]) for y in options)]
print('jobs',len(jobs),jobs,flush=True)
def run(job):
 target,flag,a,b=job;ops=base+[dict(k='R',q=(flag,),t=a-1,b=None),dict(k='CX',q=(target,flag),t=a,b=None),dict(k='CX',q=(target,flag),t=b,b=None),dict(k='M',q=(flag,),t=b+1,b=bit)];name=f'zmax_{target}_{flag}_{a}_{b}'
 try:
  st=save(H/'cand'/name,ops,dd+[[bit]],D,dict(source='Two temporal source Z checks',target=target,flag=flag,first=a,second=b));raw=raw_check(st.with_suffix('.qasm').read_text(),D)
  if not raw['ok']:return dict(name=name,raw=False)
  c1,harm=singles(st);p=price(st,1);return dict(stem=str(st),target=target,flag=flag,t1=a,t2=b,c1=c1,harmful=harm,loss=p['loss'],acceptance=p['acceptance'])
 except Exception as e:return dict(name=name,error=repr(e))
if __name__=='__main__':
 rows=[]
 with concurrent.futures.ProcessPoolExecutor(max_workers=2) as pool:
  for r in pool.map(run,jobs):rows.append(r);print(json.dumps(r),flush=True);(H/'zmax_results.json').write_text(json.dumps(rows,indent=2)+'\n')
