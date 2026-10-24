import sys,os
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
import json,subprocess
from general_atoms import analyze,HERE,ROOT
D=HERE/'r37';rows=[]
fixtures=[('v35b',HERE/'r36/inputs/v35b',0,5.97254),('sx_full',HERE/'r35/sx_full',212,176.5965),('v24',ROOT/'work/lanes/MAIN/v24',1,113.09094),('q8_reuse_v25k',ROOT/'work/lanes/XTIM/q8_reuse_v25k',127,129.3801),('region2_d11_reuseA',ROOT/'work/lanes/ENDSTATE/joint/region2_d11_reuseA',103,117.45303301955573),('region2_k56_A2_safe_dest',ROOT/'work/lanes/ENDSTATE/joint/region2_k56_A2_safe_dest',0,4.965214399271645),('v35b_reuse8',HERE/'r35/v35b_reuse8',118,218.53185),('v36b',ROOT/'work/lanes/MAIN/v36b',0,4.01)]
for name,stem,count,speed in fixtures:
 if not stem.with_suffix('.qasm').exists():
  old=stem;stem=D/'inputs'/name
  for suffix in ('.qasm','.json'):
   relative=str(old.with_suffix(suffix).relative_to(ROOT));data=subprocess.run(['git','show','a58eca7:'+relative],cwd=ROOT,capture_output=True,check=True).stdout;stem.with_suffix(suffix).write_bytes(data)
 try:
  r=analyze(stem,True);assert r['general_atoms']==count,(name,r['general_atoms'],count);assert sum(g['atoms'] for g in r['offending_gates'])==count
  r.update(reference_seconds_per_1e6=speed,expected_general_atoms=count,measured_class='SLOW' if speed>=20 else 'FAST',validation_pass=r['prediction']==('SLOW' if speed>=20 else 'FAST'))
  assert r['validation_pass'];rows.append(r);print(name,count,r['prediction'],round(r['seconds'],4),flush=True)
 except Exception as e:rows.append(dict(name=name,error=repr(e)));print('ERROR',name,repr(e),flush=True)
(D/'predictor_validation.json').write_text(json.dumps(rows,indent=2))
