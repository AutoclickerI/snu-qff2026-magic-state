import os,sys,json,subprocess,concurrent.futures
from pathlib import Path
sys.dont_write_bytecode=True
H=Path(__file__).resolve().parent;ROOT=H.parents[2];PY=ROOT/'.venv/bin/python'
choices=[('abstract_staticA_h2_opt_w011','abstract_opt11'),('abstract_staticA_h2_opt_w010','abstract_opt10'),('abstract_staticA_h2_opt_w008','abstract_opt08'),('legacy_staticA_h2_opt_w048','legacy_opt48'),('legacy_staticA_h2_opt_w046','legacy_opt46'),('abstract_staticA_h2_R60_w000','abstract_initial')]
for src,name in choices:
 with(H/(name+'.build.log')).open('w')as f:r=subprocess.run([str(PY),str(H/'build_schedule.py'),str(H/(src+'.schedule.json')),name],stdout=f,stderr=subprocess.STDOUT)
 if r.returncode:print(name,'BUILD_ERROR',flush=True);continue
 with(H/(name+'.screen.log')).open('w')as f:r=subprocess.run([str(PY),str(H/'evaluate.py'),'screen',str(H/name)],stdout=f,stderr=subprocess.STDOUT)
 print(name,'screen',r.returncode,flush=True)
