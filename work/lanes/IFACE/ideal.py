import json,sys
from pathlib import Path
from tprep.qasm import convert
from tprep.exact import verify
from tprep.noise import schedule

def check(stem):
    p=Path(stem);md=json.loads(p.with_suffix('.json').read_text())
    stim,labels,errors=convert(p.with_suffix('.qasm').read_text())
    if errors:return dict(ok=False,errors=errors)
    result=verify(stim,md['data_qubits'])
    prog,steps,gaps=schedule(stim)
    return dict(ok=not result['errors'],exact=result,native_depth=max(t for groups in steps for _,t in groups)+1)

if __name__=='__main__':
    for s in sys.argv[1:]:print(s,json.dumps(check(s)),flush=True)
