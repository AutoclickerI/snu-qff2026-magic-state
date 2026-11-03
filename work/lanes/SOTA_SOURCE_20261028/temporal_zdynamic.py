import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import sys,json,concurrent.futures,hashlib
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[2]
for d in ('work/tools','work/lanes/PREFIX20261027','work/lanes/T14'):sys.path.insert(0,str(R/d))
from qcirc import parse,save,adjacent
from qtools import price
from qtools.validity import raw_check
from search_phase import singles
P=R/'work/lanes/PREFIX2_20261027/cand/dynamic11_schedule_e0_d1'; D=json.loads(P.with_suffix('.json').read_text())['data_qubits']; base,dd=parse(P.with_suffix('.qasm').read_text());occupied={(u['t'],q)for u in base for q in u['q']};bit=max(u['b'] for u in base if u['b'] is not None)+1
# Unused-cell flag is exposed only from reset to its X measurement.
coords=[1,2,3,7,8,9,14,15,16,10,13]; jobs=[]; focus={1:7,14:13,3:9,15:19}
for target in coords:
 if target not in focus:continue
 if not any(target in u['q'] and u['t']<16 and u['k'] in ('CX','RX','T','TDG') for u in base):continue
 for flag in range(36):
  if flag in coords or not adjacent(flag,target):continue
  for a in range(2,23):
   for b in range(a+2,25):
    if not a<=focus[target]<b:continue
    if any((t,flag)in occupied for t in range(a-1,b+2)):continue
    if (a,target)in occupied or (b,target)in occupied:continue
    jobs.append((target,flag,a,b))
print('jobs',len(jobs),flush=True)

def run(job):
 target,flag,a,b=job;name=f'zech_{target}_{flag}_{a}_{b}'
 ops=base+[dict(k='R',q=(flag,),t=a-1,b=None),dict(k='CX',q=(target,flag),t=a,b=None),dict(k='CX',q=(target,flag),t=b,b=None),dict(k='M',q=(flag,),t=b+1,b=bit)]
 try:
  st=save(H/'cand'/name,ops,dd+[[bit]],D,dict(source='Time-separated Z-echo flag on dynamic compact source',target=target,flag=flag,first=a,second=b))
  raw=raw_check(st.with_suffix('.qasm').read_text(),D)
  if not raw['ok']:return None
  c1,harm=singles(st);p=price(st,1)
  return dict(stem=str(st),target=target,flag=flag,t1=a,t2=b,c1=c1,harmful=harm,loss=p['loss'],acceptance=p['acceptance'])
 except Exception as e:return dict(name=name,error=repr(e))
if __name__=='__main__':
 rows=json.loads((H/'temporal_zdynamic_results.json').read_text()) if (H/'temporal_zdynamic_results.json').exists() else []
 done={(z.get('target'),z.get('flag'),z.get('t1'),z.get('t2')) for z in rows}
 jobs[:]=[x for x in jobs if x not in done]
 with concurrent.futures.ProcessPoolExecutor(max_workers=2) as pool:
  for j,res in enumerate(pool.map(run,jobs)):
   if res:rows.append(res);print(json.dumps(res),flush=True)
   if j%20==0:(H/'temporal_zdynamic_results.json').write_text(json.dumps(rows,indent=2)+'\n');print('done',j,'of',len(jobs),flush=True)
 (H/'temporal_zdynamic_results.json').write_text(json.dumps(rows,indent=2)+'\n')
