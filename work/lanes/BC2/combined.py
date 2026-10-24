import concurrent.futures
import json
from pathlib import Path
import batch

base=json.loads(Path('baseline_prep.json').read_text()); jobs=[]
for depth in (13,14,15,16):
    seed=dict(base,ops=(base['ops']+[[],[]])[:depth])
    Path(f'prime_d{depth}.json').write_text(json.dumps(seed))
    for rule in ('both','allpairs'):
        for cap in (82,100):
            name=f'combined_{rule}_d{depth}_k{cap}'
            args=['--depth',str(depth),'--cap',str(cap),'--rule',rule,'--seed',str(14000+depth*100+cap),
                  '--initial',f'prime_d{depth}.json','--seconds','240','--helpers','','--fix-pivots']
            jobs.append((name,args))
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
    results=list(pool.map(batch.run,jobs))
Path('batch_combined.json').write_text(json.dumps(results,indent=2))
