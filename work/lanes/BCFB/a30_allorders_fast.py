from a30_common import *
import subprocess,concurrent.futures
stems=json.loads((D/'fastpick_manifest.json').read_text())
def run(stem):
 with Path(stem+'.allorders.log').open('w') as log:r=subprocess.run([sys.executable,str(D/'sparse/sparse_walsh.py'),stem,'72','canonical'],cwd=D,stdout=log,stderr=subprocess.STDOUT)
 print('EXIT',Path(stem).name,r.returncode,flush=True);assert r.returncode==0
 x=json.loads((D/'sparse'/(Path(stem).name+'_canonical_sparse_result.json')).read_text());print('RESULT',Path(stem).name,x['loss'],x['acceptance'],flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=12) as e:list(e.map(run,stems))
