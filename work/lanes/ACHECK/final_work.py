from common import *
import subprocess
for args in [['internal_star.py'],['validate_fast.py'],['batch.py','base','verify_9_15','verify_2_9_15','verify_1_2_9_15'],['mc.py','combo_9_15_8','16']]:
 r=subprocess.run([sys.executable,*args],cwd=HERE);assert r.returncode==0,args
