import json
from pathlib import Path
import subprocess
import sys
import os
import concurrent.futures
import merge
import score
from steane_full import LAYOUTS,MOVES

P='/home/jihoon/competitions/quantumn/.venv/bin/python'
def one(p):
        prep=json.loads(p.read_text()); name=p.name[:-10]
        receipt=json.loads(Path(name+'.receipt.json').read_text())
        text,data,R,pre_end=merge.build({'a':json.load(open('../DR/prepA_L5_s7307.json')),'bc':prep},['a','bc'],LAYOUTS['L5'],MOVES['L5'])
        Path(name+'.qasm').write_text(text)
        meta=dict(data_qubits=data,prep_cx=sum(map(len,prep['ops'])),depth=len(prep['ops']),round_start=R,rule=receipt['rule'])
        Path(name+'.json').write_text(json.dumps(meta,indent=2))
        subprocess.run([P,'minit.py',name,'.','27,29'],check=True)
        stem=name+'_m27_29'; meta['minit_requested']=[27,29]
        Path(stem+'.json').write_text(json.dumps(meta,indent=2))
        print('BUILT',stem,meta,flush=True)
        score.score(stem,int(os.environ.get('BC2_SCORE_PROCS','8')))

if __name__=='__main__':
    paths=sorted({p for pattern in sys.argv[1:] for p in Path('.').glob(pattern) if p.name.endswith('.prep.json')})
    with concurrent.futures.ProcessPoolExecutor(max_workers=2) as pool:
        list(pool.map(one,paths))
