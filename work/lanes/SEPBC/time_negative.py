"""A real 1e6 judge run, stopped only after exceeding the lane's speed gate."""
from common import *
import subprocess
stem=Path(sys.argv[1]);start=time.monotonic();cmd=[str(ROOT/'.venv/bin/python'),'-u',str(ROOT/'work/fast_check.py'),str(stem.with_suffix('.qasm')),str(stem.with_suffix('.json')),'1000000','1']
p=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
try:out,_=p.communicate(timeout=22);timed_out=False
except subprocess.TimeoutExpired:p.kill();out,_=p.communicate();timed_out=True
elapsed=time.monotonic()-start;stem.with_suffix('.speed.log').write_text(out)
r=dict(returncode=p.returncode,wall_seconds=elapsed,exceeded_20_seconds=elapsed>20,terminated_after_gate=timed_out,stdout=out)
stem.with_suffix('.speed.json').write_text(json.dumps(r,indent=2));append_result(stem.name,r,'Direct 1e6 judge/speed gate; timeout establishes runtime failure, not acceptance.');print(json.dumps(r),flush=True)
