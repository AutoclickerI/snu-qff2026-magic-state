#!/usr/bin/env python3
import json
import multiprocessing as mp
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
import sys
sys.path.insert(0, str(ROOT / 'work/lanes/EVAL'))
from exact2 import Eval, run


def one(path):
    meta = json.loads(path.with_suffix('.json').read_text())
    ev = Eval(path.read_text(), meta['data_qubits'])
    r = run(ev, procs=4)
    return dict(name=path.stem, loss2=r['loss'], first=r['loss1'], A1=r['A1'],
                acc1=r['acc1'], acc2=r['acc2'], expA=float(__import__('numpy').exp(-r['A1'])),
                n_channels=len(ev.m.chans), n_faults=ev.n_f, n_2q=sum(1 for x in ev.m.prog if x.name == 'CX'))


def main():
    paths = sorted(HERE.glob('*.qasm'))
    with mp.get_context('fork').Pool(min(6, len(paths))) as pool:
        rows = pool.map(one, paths)
    rows.sort(key=lambda x: x['loss2'])
    (HERE / 'exact2.json').write_text(json.dumps({'rows': rows}, indent=2) + '\n')
    for r in rows:
        print(f"{r['name']} loss2={r['loss2']:.9e} first={r['first']:.2e} A1={r['A1']:.6f} exp={r['expA']:.6f} acc2={r['acc2']:.6f}", flush=True)


if __name__ == '__main__':
    main()
