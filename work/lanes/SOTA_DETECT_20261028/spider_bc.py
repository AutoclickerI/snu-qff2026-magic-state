import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import numpy as np
from spidercss.cat_at_origin import row_optimized_cat_at_origin
from spidercss.resource_targets import ReuseTarget
masks=[85,102,120]
rows=[[int((mask>>i)&1) for i in range(7)]*2 for mask in masks]
rows += [[0]*7+[int((mask>>i)&1)for i in range(7)] for mask in [7,25,42,64]]
H=np.array(rows,dtype=np.uint8)
c=row_optimized_cat_at_origin(H,3,basis='Z',max_basis_tries=200,analyze_hook_errors=True,reuse_target=ReuseTarget.DEPTH,is_perfect_code=False)
print(c,flush=True)
