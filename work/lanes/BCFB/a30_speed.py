from a30_common import *
import importlib.util,time,subprocess
stem=Path(sys.argv[1]).resolve();spec=importlib.util.spec_from_file_location('bcfb_xtim_speed',H/'xtim_speed_snapshot.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);xtim.cache_dir=str(D/'.xtim_cache')
r=m.predict(str(stem));Path(str(stem)+'.speed.json').write_text(json.dumps(r,indent=2));print(json.dumps(r),flush=True)
if r['classification']!='FAST':sys.exit(2)
if '--probe' in sys.argv:sys.exit(0)
import tprep
start=time.monotonic();r=tprep.check(stem.with_suffix('.qasm').read_text(),json.loads(stem.with_suffix('.json').read_text())['data_qubits'],shots=10**6,seed=0)
v=dict(passed=bool(r.passed),acceptance=float(r.acceptance),score=float(r.score),format_ok=bool(r.format_ok),class_ok=bool(r.class_ok),correct_ok=bool(r.correct_ok),acceptance_ok=bool(r.acceptance_ok),seconds=time.monotonic()-start);Path(str(stem)+'.check.json').write_text(json.dumps(v,indent=2));print(json.dumps(v),flush=True)
start=time.monotonic()
with Path(str(stem)+'.fast.log').open('w') as log:p=subprocess.run([sys.executable,str(ROOT/'work/fast_check.py'),str(stem)+'.qasm',str(stem)+'.json','1000000','1'],cwd=D,stdout=log,stderr=subprocess.STDOUT)
v=dict(returncode=p.returncode,seconds=time.monotonic()-start);Path(str(stem)+'.fast.json').write_text(json.dumps(v,indent=2));print(json.dumps(v),flush=True);assert p.returncode==0
