import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import numpy as np
from spidercss.cat_at_origin import row_optimized_cat_at_origin
from spidercss.resource_targets import ReuseTarget
H=[]
for block,ms in [(0,[85,102,120,7]),(1,[85,102,120]),(2,[85,102,120,7])]:
 for m in ms:
  row=[0]*21
  for i in range(7):row[block*7+i]=(m>>i)&1
  H.append(row)
c=row_optimized_cat_at_origin(np.array(H,dtype=np.uint8),3,basis='Z',max_basis_tries=200,analyze_hook_errors=True,reuse_target=ReuseTarget.QUBITS,is_perfect_code=False)
print(c,flush=True)
