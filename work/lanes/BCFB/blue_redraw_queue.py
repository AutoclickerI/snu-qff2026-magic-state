"""Event-driven redraw queue; the plan is reread only when a subprocess exits."""
import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import argparse,json,subprocess,time,hashlib
from pathlib import Path
H=Path(__file__).resolve().parent;D=H/'blue'
p=argparse.ArgumentParser();p.add_argument('--plan',required=True);p.add_argument('--procs-file',required=True);a=p.parse_args();done=set()
while True:
 remaining=[s for s in json.loads(Path(a.plan).read_text()) if s not in done]
 if not remaining:break
 name=remaining[0];f=D/'finalists'/name;v=json.loads(f.with_suffix('.verify.json').read_text());assert v.get('exact_verified') and v.get('gates_pass'),(name,v)
 identity=dict(stem=name,qasm_sha256=hashlib.sha256(f.with_suffix('.qasm').read_bytes()).hexdigest(),data_qubits=json.loads(f.with_suffix('.json').read_text())['data_qubits'])
 inp=D/'runs'/(name+'.redraw_input.json')
 if inp.exists():assert json.loads(inp.read_text())==identity
 else:inp.write_text(json.dumps(identity,indent=2))
 rows={}
 for prior in (D/'runs').glob(name+'_redraw_*.jsonl'):
  for line in prior.read_text().splitlines():
   r=json.loads(line);k=r['draw']
   if k in rows:assert rows[k]==r
   rows[k]=r
 assert set(rows)==set(range(len(rows))) and len(rows)<=100
 start_index=len(rows);n=int(Path(a.procs_file).read_text());print(json.dumps(dict(event='REDRAW_STEM_START',stem=name,start=start_index,cores=os.cpu_count(),load=os.getloadavg(),procs=n)),flush=True)
 start=time.monotonic();rc=0
 if start_index<100:rc=subprocess.run([sys.executable,str(H/'blue_redraw.py'),name,'--start',str(start_index),'--draws',str(100-start_index),'--procs-file',a.procs_file],cwd=D).returncode
 rec=dict(stem=name,returncode=rc,start=start_index,seconds=time.monotonic()-start);(D/'runs'/(name+'.redraw_exit.json')).write_text(json.dumps(rec,indent=2));assert rc==0,rec;done.add(name);print(json.dumps(dict(event='REDRAW_STEM_FINISHED',**rec)),flush=True)
