"""Screen flags at second order; exact third order and MC for contenders."""
import concurrent.futures
import json
import math
from pathlib import Path
import sys
import os
import subprocess
import score


def quick(stem):
    cores=int(subprocess.check_output(['nproc','--all']))
    load=Path('/proc/loadavg').read_text().strip()
    print('SCREEN',stem,cores,load,flush=True)
    text=Path(stem+'.qasm').read_text(); data=json.loads(Path(stem+'.json').read_text())['data_qubits']
    rep=score.tprep.check(text,data,shots=10**6,seed=0)
    out=dict(check_1e6=score.record(rep))
    if rep.passed:
        ev=score.exact2.Eval(text,data); r=score.exact2.run(ev,1)
        out['quick']=dict(c1=r['loss1'],second=r['loss2'],exp_minus_A1=math.exp(-r['A1']))
    Path(stem+'.score.json').write_text(json.dumps(out,indent=2))
    print('RESULT',stem,out.get('quick'),rep.passed,flush=True)
    return stem,out


if __name__=='__main__':
    stems=[x['stem'] for x in json.loads(Path('flags_manifest.json').read_text())]
    with concurrent.futures.ProcessPoolExecutor(max_workers=6) as pool:
        results=list(pool.map(quick,stems))
    ranked=sorted([(s,r['quick']['second']) for s,r in results if 'quick' in r],key=lambda x:x[1])
    Path('flags_quick.json').write_text(json.dumps(ranked,indent=2))
    for stem,second in ranked:
        # Every valid flag gets the requested third-order screen, including
        # candidates whose extra gate faults overwhelm the surrogate benefit.
        score.score(stem,12)
