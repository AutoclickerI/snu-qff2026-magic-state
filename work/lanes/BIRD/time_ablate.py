import os,sys
from pathlib import Path
sys.dont_write_bytecode=True
root=Path(__file__).resolve().parents[3]
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
sys.path[:0]=[str(root/'work/lanes/MAIN'),str(root/'work/lanes/TREP2')]
import fast_third,exact2,ablate
# Algebraically zero acceptance classes alone are skipped; arithmetic unchanged.
exact2.third_order=fast_third.third_order
ablate.main()
