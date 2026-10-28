import os,sys,json
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
R=Path(__file__).resolve().parents[3];H=Path(__file__).parent;sys.path[:0]=[str(R/'work/lanes/NATIVE2_20261027'),str(R/'work/lanes/REBUILD20261027'),str(R/'work/tools')]
from incumbent_a_sx import f
import record_contract
record_contract.fa=f
P=H/'redesign_five_valid_5505afaaef422fe1_d6_20_19_10_2_22_16.qasm';f.DATA=[6,20,19,10,2,22,16];r=record_contract.singles(f.make_model(*f.parse_current(P.read_text())));(H/'five_singles.json').write_text(json.dumps(r,indent=2)+'\n');print('c1',r['c1'],'harmful',len(r['harmful_faults']))
