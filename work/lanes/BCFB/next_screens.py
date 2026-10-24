"""Event-ordered screens occupying a fixed four-core allocation."""
import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import subprocess,json
from pathlib import Path
H=Path(__file__).resolve().parent
jobs=[['identity_ablation.py'],['init_best.py','fb_d14_c98_s517_00020','--workers','4','--radius','2'],['pairs.py','finalists/fb_d14_c98_s517_00020','--workers','4'],['scan.py','timing','--stem','finalists/fb_d14_c98_s517_00020','--workers','4','--rounds','12','--radius','12'],['order_joint.py'],['retry.py','--workers','4','--kind','retime','--limit','2500']]
for args in jobs:
 name=args[0][:-3];name+=('_'+args[1] if len(args)>1 and '/' not in args[1] else '')
 with (H/'runs'/f'next_{name}.log').open('w') as log:r=subprocess.run([sys.executable,str(H/args[0]),*args[1:]],stdout=log,stderr=subprocess.STDOUT)
 print(json.dumps(dict(args=args,exit_code=r.returncode)),flush=True)
 if r.returncode:raise RuntimeError((args,r.returncode))
