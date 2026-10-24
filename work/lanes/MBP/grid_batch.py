"""All six D4 classes of the 48 legal prefix embeddings."""
import os,sys,json,subprocess,concurrent.futures
from pathlib import Path
HERE=Path(__file__).resolve().parent
def run(rc):
    r,c=rc;name=f'grid_tree_r{r}c{c}'
    if (r,c)==(0,0):return dict(name='grid_u_h2t2_auto',external_process=True)
    cmd=[sys.executable,str(HERE/'grid.py'),name,'--kinds','u,h2t,h2t','--block-hop','--block-hops','2','--automorphisms','--row',str(r),'--col',str(c),'--seconds','180','--workers','1','--first']
    assert os.getloadavg()[0]<os.cpu_count()
    with (HERE/(name+'.log')).open('w') as f:p=subprocess.Popen(cmd,stdout=f,stderr=subprocess.STDOUT);rc=p.wait()
    row=dict(name=name,exit=rc);print(json.dumps(row),flush=True);return row
if __name__=='__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:rows=list(ex.map(run,[(r,c) for r in range(3) for c in range(2)]))
    (HERE/'all_embeddings.receipt.json').write_text(json.dumps(rows,indent=2)+'\n')
