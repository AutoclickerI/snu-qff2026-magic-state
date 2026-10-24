from a30_common import *
import subprocess,concurrent.futures
cases=['base','no_A_CX','no_A_init_checks','no_A_encoder','no_A_idle','no_A_coupling','no_A_readout','no_A_all','no_data_wait','no_pre_stage','no_A_all_data_wait','no_A_all_pre_stage','no_A_CX_data_wait','no_A_CX_pre_stage']
def run(case):
 print('START',case,os.cpu_count(),os.getloadavg(),flush=True)
 with (D/'runs'/('decomp_'+case+'.log')).open('w') as log:r=subprocess.run([sys.executable,str(H/'a30_decompose.py'),'--procs','6','--case',case],cwd=D,stdout=log,stderr=subprocess.STDOUT)
 print('EXIT',case,r.returncode,flush=True);assert r.returncode==0
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as e:list(e.map(run,cases))
