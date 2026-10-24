#!/usr/bin/env python3
import json, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'work/lanes/EVAL'))
from exact2 import Eval,run
import numpy as np
lo=int(sys.argv[1]); hi=int(sys.argv[2]); pat=sys.argv[3] if len(sys.argv)>3 else '*.qasm'; paths=sorted(HERE.glob(pat))[lo:hi]
rows=[]
for path in paths:
    meta=json.loads(path.with_suffix('.json').read_text()); ev=Eval(path.read_text(),meta['data_qubits']); r=run(ev,procs=4)
    rows.append(dict(name=path.stem,loss2=r['loss'],first=r['loss1'],A1=r['A1'],acc1=r['acc1'],acc2=r['acc2'],expA=float(np.exp(-r['A1'])),n_2q=sum(x.name=='CX' for x in ev.m.prog)))
Path(HERE/f'exact_{lo}_{hi}.json').write_text(json.dumps(rows,indent=2)+'\n')
for x in rows: print(x['name'],x['loss2'],flush=True)
