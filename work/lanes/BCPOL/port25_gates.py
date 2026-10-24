"""Speed and all-orders scope gates for every distinct v25 port."""
import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
os.environ['QUANTUMN_REPO']=str(ROOT);os.environ['XTIM_TWIRL_CACHE_DIR']=str(H/'.xtim_cache');sys.path.insert(0,str(H/'audit'))
from fresh_exact_walsh import prepare
import json,subprocess,re,time,hashlib
py=str(ROOT/'.venv/bin/python');cal=H/'inputs/v22h_c2c9'
cmd=[py,str(ROOT/'work/fast_check.py'),str(cal)+'.qasm',str(cal)+'.json','1000000','1'];res=subprocess.run(cmd,capture_output=True,text=True,check=True);(H/'v25.calibration.speed.log').write_text(res.stdout+res.stderr);seconds=float(re.search(r'\(([0-9.]+)s, 1 procs',res.stdout)[1]);limit=20*seconds/2.3
rows=json.loads((H/'v25_ports.json').read_text());seen={};results=[]
for row in [dict(tag='v25k',input=True)]+rows:
 stem=(H/'inputs' if row.get('input') else H/'finalists')/row['tag'];qasm=stem.with_suffix('.qasm')
 if not qasm.exists():continue
 digest=hashlib.sha256(qasm.read_bytes()).hexdigest()
 if digest in seen:results.append(dict(tag=row['tag'],same_qasm_as=seen[digest]));continue
 seen[digest]=row['tag'];out=dict(tag=row['tag'],host=os.uname().nodename,qasm_sha256=digest,calibration=seconds,limit=limit)
 t=time.monotonic()
 try:
  res=subprocess.run([py,str(ROOT/'work/fast_check.py'),str(qasm),str(stem)+'.json','1000000','1'],capture_output=True,text=True,timeout=limit+15,check=True)
  log=res.stdout+res.stderr;stem.with_suffix('.speed.log').write_text(log);out['s_per_1e6']=float(re.search(r'\(([0-9.]+)s, 1 procs',log)[1]);out['speed_pass']=out['s_per_1e6']<=limit;out['judge_pass']='passed=True' in log
 except subprocess.TimeoutExpired as e:out.update(speed_pass=False,status='SPEED_TIMEOUT',timeout_seconds=limit+15)
 except subprocess.CalledProcessError as e:out.update(speed_pass=False,status='JUDGE_PROCESS_ERROR',stderr=e.stderr)
 try:
  m,eng,g,nd,ks,psi,where,elim=prepare(stem);out['allorders_scope']=dict(width=elim['width'],rotations=len(m.rots),active_bits=len(ks),supported=elim['width']<=23)
 except (ValueError,AssertionError) as e:out['allorders_scope']=dict(supported=False,error=str(e))
 out['seconds']=time.monotonic()-t;stem.with_suffix('.port_gates.json').write_text(json.dumps(out,indent=2));results.append(out);print(json.dumps(out),flush=True)
(H/'v25_gates.json').write_text(json.dumps(results,indent=2))
