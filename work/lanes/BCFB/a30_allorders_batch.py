from a30_common import *
import sqlite3,zlib,hashlib,concurrent.futures,subprocess,argparse
p=argparse.ArgumentParser();p.add_argument('--procs',type=int,default=6);p.add_argument('--count',type=int,default=12);p.add_argument('--prefix',default='near');p.add_argument('--databases',nargs='+',default=['library','acheck','local']);a=p.parse_args()
rows=[]
for name in a.databases:
 db=sqlite3.connect(D/f'{name}.sqlite')
 for i,r,q,m in db.execute('select id,row,qasm,md from results'):
  r=json.loads(r)
  if r.get('exp_minus_A1',0)>=.5002 and r.get('total',1)<7e-5:rows.append((r['total'],name,i,r,q,m))
seen=set();chosen=[]
for f in (D/'sparse').glob('*_canonical_sparse_result.json'):
 result=json.loads(f.read_text());screen=Path(result['source']+'.screen.json')
 if screen.exists():
  r=json.loads(screen.read_text());seen.add((round(r['total'],14),round(r['exp_minus_A1'],12)))
for value,name,i,r,q,m in sorted(rows,key=lambda r:r[:3]):
 key=(round(value,14),round(r['exp_minus_A1'],12))
 if key in seen:continue
 seen.add(key);stem=D/'finalists'/f'a30_{a.prefix}_{name}_{i:05}'
 stem.with_suffix('.qasm').write_text(zlib.decompress(q).decode());stem.with_suffix('.json').write_text(m);stem.with_suffix('.screen.json').write_text(json.dumps(r,indent=2));chosen.append(str(stem))
 if len(chosen)>=a.count:break
(D/f'{a.prefix}_allorders_manifest.json').write_text(json.dumps(chosen,indent=2))
def run(stem):
 print('START',stem,os.cpu_count(),os.getloadavg(),flush=True)
 with (D/'runs'/(Path(stem).name+'.allorders.log')).open('w') as log:r=subprocess.run([sys.executable,str(D/'sparse/sparse_walsh.py'),stem,'72','canonical'],cwd=D,stdout=log,stderr=subprocess.STDOUT)
 print('EXIT',stem,r.returncode,flush=True);assert r.returncode==0
 result=json.loads((D/'sparse'/(Path(stem).name+'_canonical_sparse_result.json')).read_text())
 print('RESULT',Path(stem).name,json.dumps({k:result[k] for k in ('loss','acceptance','seconds','conditional_loss_kernel_omission_bound')}),flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=a.procs) as e:list(e.map(run,chosen))
