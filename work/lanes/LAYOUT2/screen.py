import sys,os,json
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
import exenc
here=Path(__file__).resolve().parent
seen=set();summary=[]
layouts=[]
for f in here.glob('*.json'):
 try:l=json.loads(f.read_text())
 except (ValueError,OSError):continue
 if isinstance(l,dict) and all(k in l for k in ('a','b','c','d','M','cat','moves')):layouts.append((f,l))
layouts.sort(key=lambda fl:fl[1]['objective'])
for f,l in layouts:
 key=(tuple(l['a']),tuple(l['M']))
 if key in seen:continue
 seen.add(key);out=f.with_name(f.stem+'_A.json');stat=f.with_name(f.stem+'_A_stats.json')
 if stat.exists() and len(json.loads(stat.read_text()).get('counted_classes',[]))>=3:r=json.loads(stat.read_text())
 else:r=exenc.run(l['a'],'plus',[],2,out,2,False,True)
 good=[c for c in r.get('pareto',[]) if all(c['danger_vector_units'][j+1]==0 for j in l['M'])]
 good.sort(key=lambda c:(c['depth'],c['cx'],c['danger_units']))
 f.with_name(f.stem+'_A_filtered.json').write_text(json.dumps(good,indent=2)+'\n')
 summary.append(dict(layout=f.name,caught=len(good),best=good[0] if good else None,M=l['M'],hops=l['hops'],helpers=len(l['hBC'])))
 (here/'screen.json').write_text(json.dumps(summary,indent=2)+'\n')
 print('SCREEN',f.name,'caught',len(good),'best',[(c['depth'],c['cx']) for c in good[:3]],flush=True)
