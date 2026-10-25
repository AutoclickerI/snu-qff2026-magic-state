import sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path('base').resolve())); import sparse_walsh as old
m, eng, groups, nd, ks, psi, where, dense = old.prepare(Path(sys.argv[1]).resolve(), True)
sys.path.pop(0)
import importlib.util
spec = importlib.util.spec_from_file_location('swn', Path('sparse/sparse_walsh.py')); new = importlib.util.module_from_spec(spec)
sys.modules.pop('frontend'); sys.modules.pop('fastfill', None); sys.path.insert(0, str(Path('sparse').resolve())); spec.loader.exec_module(new)
for key in [None] + eng.keys[:3]:
    raw = (psi.conj()*psi).real if key is None else None
    if key is None:
        g = np.stack([raw[:, idx].sum(axis=1) for idx in where], axis=1)
    else:
        mj, wj, c = eng.Qs[key]
        raw = (psi[:, eng.idx.astype(int)^mj].conj()*c*eng.sgn(wj)[None, :]*psi).real
        g = np.stack([raw[:, idx].sum(axis=1) for idx in where], axis=1)
    a, b = old.fwht(g.reshape(-1)), new.fwht(g)
    sa, sb = np.abs(a) < 1e-12, np.abs(b) < 1e-12
    print(key, 'max|diff|', np.abs(a-b).max(), 'flips', int((sa != sb).sum()), 'exact zeros old/new', int((a == 0).sum()), int((b == 0).sum()),
          'max |a| among small', np.abs(a[sa]).max(), 'abs sum small old/new', np.abs(a[sa]).sum(), np.abs(b[sb]).sum(),
          'flipped |a|', np.sort(np.abs(a[sa != sb]))[-3:])
