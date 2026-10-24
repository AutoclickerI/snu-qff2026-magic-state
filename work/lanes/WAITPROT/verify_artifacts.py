import os,sys,json,hashlib,math,time
from pathlib import Path
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
sys.path.insert(0,str(ROOT/'work'))
import fast_check,xtim,tick_build as tb
xtim.cache_dir=str(H/'.xtim_cache')
rows=[]
for alias in ('best','seed0_best'):
 md=json.loads((H/(alias+'.json')).read_text());summary=json.loads((H/(alias+'.metrics.json')).read_text());src=summary['source_stem'];raw=(H/(alias+'.qasm')).read_bytes();sha=hashlib.sha256(raw).hexdigest()
 assert raw==(H/(src+'.qasm')).read_bytes()
 assert md==json.loads((H/(src+'.json')).read_text())
 assert sha==summary['allorders']['sha256']==json.loads((H/(src+'.ref.exit.json')).read_text())['sha256']
 audit=tb.check(H/alias)
 t=time.monotonic();r=fast_check.check(raw.decode(),md['data_qubits'],shots=10**6,seed=0,procs=1)
 assert r.passed and r.n_2q==md['cx']==201,str(r)
 assert r.acceptance==summary['gate']['acceptance'],(r.acceptance,summary['gate']['acceptance'])
 assert math.isclose(float(r.score),summary['gate']['score'],rel_tol=1e-10,abs_tol=1e-14)
 out=dict(alias=alias,source=src,sha256=sha,byte_identical=True,native_audit=audit,passed=r.passed,score=float(r.score),acceptance=r.acceptance,cx=r.n_2q,seconds=time.monotonic()-t,host=os.uname().nodename)
 rows.append(out);print(json.dumps(out),flush=True)
(H/'final_artifact_check.json').write_text(json.dumps(rows,indent=2))
