import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
import json,subprocess,time
H=Path(__file__).resolve().parent;D=H/'blue';stems=[c+'_'+s for c in ['v25k','v26n'] for s in ['ic_fast_d15_c105_s526_00356_11_19_preserve_rt1','fast_d15_c105_s526_00331_preserve_rt1','fast_d15_c105_s526_00356_preserve_rt1','fb_d14_c98_s517_00020_preserve','fb_d15_c105_s506_00008_preserve_rt1']]
old={s:json.loads((D/'finalists'/s).with_suffix('.verify.json').read_text()) for s in stems};(D/'pre_cache_speed_receipts.json').write_text(json.dumps(old,indent=2))
rc=subprocess.run([sys.executable,str(H/'blue_verify.py'),*stems]).returncode;assert rc==0
rows=[]
for s in stems:
 r=json.loads((D/'finalists'/s).with_suffix('.verify.json').read_text());a=old[s];row=dict(stem=s,old_score=a['score'],score=r['score'],old_acceptance=a['acceptance'],acceptance=r['acceptance'],score_identical=a['score']==r['score'],acceptance_identical=a['acceptance']==r['acceptance'],speed_seconds=r['speed_seconds'],passed=r['speed_pass']);assert row['score_identical'] and row['acceptance_identical'] and row['passed'],row;rows.append(row)
(D/'cache_audit.json').write_text(json.dumps(rows,indent=2));print('CACHE LOCATION AUDIT PASS',len(rows),flush=True)
