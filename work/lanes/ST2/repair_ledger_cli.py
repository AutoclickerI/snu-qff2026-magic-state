import sys,json
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));from ledger_batch import job,H
labels=['no:prefix_ops','no:prefix_idles','no:data_wait','no:BC','no:A','no:round']
rows=[]
with ThreadPoolExecutor(3) as pool:
    for f in as_completed([pool.submit(job,'cli',l,1) for l in labels]):
        r=f.result();rows.append(r);print(json.dumps(r),flush=True)
(H/'ledger_cli_repairs.json').write_text(json.dumps(rows,indent=2))
assert all(r['returncode']==0 for r in rows)
