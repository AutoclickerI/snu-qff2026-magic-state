"""Run the official minit transform at every remaining first-use Z reset."""
import concurrent.futures
import json
from pathlib import Path
import re
import subprocess
import sys
import score

P='/home/jihoon/competitions/quantumn/.venv/bin/python'
stem=sys.argv[1]
rootmeta=json.loads(Path(stem+'.json').read_text())
dest=Path(stem+'_init_scan');dest.mkdir(exist_ok=True)
subprocess.run([P,'minit.py',stem,str(dest)],check=True)

def quick(p):
    meta=json.loads(p.with_suffix('.json').read_text());text=p.read_text()
    check=score.tprep.check(text,meta['data_qubits'],shots=10**6,seed=0)
    r=dict(check_1e6=score.record(check))
    if check.passed:
        ev=score.exact2.Eval(text,meta['data_qubits']);x=score.exact2.run(ev,1)
        r['quick']=dict(c1=x['loss1'],second=x['loss2'])
    p.with_suffix('.score.json').write_text(json.dumps(r,indent=2))
    return p.stem,r

if __name__=='__main__':
    with concurrent.futures.ProcessPoolExecutor(max_workers=4) as pool:
        results=dict(pool.map(quick,sorted(dest.glob('*.qasm'))))
    base=json.loads(Path(stem+'.score.json').read_text())['exact']['second']
    picked=[]
    for name,r in results.items():
        match=re.search(r'_m(\d+)$',name)
        if match and r.get('quick',{}).get('second',1)<base-1e-12:
            picked.append(int(match.group(1)))
    Path(stem+'.init_scan.json').write_text(json.dumps(dict(base=base,picked=picked,results=results),indent=2))
    print('PICKED',picked,flush=True)
    if picked:
        subprocess.run([P,'minit.py',stem,'.',','.join(map(str,picked))],check=True)
        out=stem+'_m'+'_'.join(map(str,picked))
        rootmeta['additional_first_use_measured']=picked
        Path(out+'.json').write_text(json.dumps(rootmeta,indent=2))
        score.score(out,4)
