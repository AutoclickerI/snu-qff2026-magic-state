import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import json
from separate import build,HERE,D,write_stem,price,raw_check
out=[]
for checks,prechecks,uncompute in [(2,'Z','matching'),(2,'Z','none'),(1,'Z','full'),(2,'','full')]:
    c,meta=build(checks,prechecks,uncompute)
    name=f'separate_w{checks}_{uncompute}'+(f'_pc{prechecks}' if prechecks else '')
    stem=write_stem(c.text(),D,HERE/'cand',name,source=meta)
    r=dict(stem=str(stem),**meta,raw=raw_check(c.text(),D))
    if r['raw']['ok']:r['price']=price(stem,processes=1)
    (HERE/f'{name}.result.json').write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps(r),flush=True);out.append(r)
(HERE/'separate_screen.json').write_text(json.dumps(out,indent=2)+'\n')
