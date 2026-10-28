import os,sys
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
R=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'work/lanes/SOTA_RESOURCE_20261028'))
import resource_pairs as rp
D={6,20,19,10,2,22,16};A={7,14,13,9,8,21,15};BC={12,26,25,11,3,28,17,18,27,24,5,4,29,23,30,31,32,33,34,35}
def stage(c,t):
 q=set(c['qubits']);k=c['kind']
 if t<14:return 'encoder_'+k
 if q<=D:return 'data_'+k
 if q<=BC:return 'BC_'+k
 if q<=A:return ('cat_' if t<32 else 'terminal_A_')+k
 if q&(D|A) and t<32:return 'cat_coupling_'+k
 return 'terminal_other_'+k
rp.stage=stage;rp.nr.HERE=H;rp.nr.STEM=next(H.glob('repair_cat7_opt_t11_m0_d21_*.qasm')).with_suffix('');rp.run();(H/'resource_pairs.json').rename(H/'pairs_repaired.json')
