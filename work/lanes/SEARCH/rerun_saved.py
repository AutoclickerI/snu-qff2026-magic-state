"""Reproduce a saved screen without installing downloaded source packages.

Usage: .venv/bin/python work/lanes/SEARCH/rerun_saved.py [case_name ...]
No arguments reproduces all final cases (one process, one thread).
"""
import os
os.environ.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
import json,sys
from eval_clifford import OUT,score

names=sys.argv[1:]
paths=[OUT/(name+'.json') for name in names] if names else [p for p in sorted(OUT.glob('*.json')) if p.name!='summary.json']
for path in paths:
    old=json.loads(path.read_text())
    existing=old['scope'].startswith('ideal encoded input')
    text=path.with_suffix('.stim').read_text()
    if existing:
        first,text=text.split('\n',1)
        assert first=='I 0 1 2 3 4 5 6',first
    new=score(old['name'],text,old['stabilizer_supports'],bases=tuple(old['basis']),existing_input=existing,shots=old['shots_per_basis'])
    assert new['loss']==old['loss'],(old['name'],old['loss'],new['loss'])
    for basis in old['basis']:
        for key in ['bad','accepted']:
            assert new['basis'][basis][key]==old['basis'][basis][key]
