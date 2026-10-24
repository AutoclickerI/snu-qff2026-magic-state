import importlib,json,sys
from pathlib import Path
ROOT=Path('/home/jihoon/competitions/quantumn'); OUT=ROOT/'work/lanes/PRE3'
sys.path[:0]=[str(ROOT/'upstream/snu-qff2026-problem'),str(ROOT/'work')]
# Grid-free wrapper: patch each module's imported adjacency symbol, including parse.check_format.
for mod in ('tprep.grid','tprep.parse','tprep.qasm'):
    m=importlib.import_module(mod); m.adjacent=lambda a,b: True
from tprep import check
for p in sorted(OUT.glob('*.qasm')):
    if p.stem.endswith('.qasm'): continue
    meta=json.loads((p.with_suffix('.json')).read_text())
    r=check(p.read_text(),meta['data_qubits'],shots=10**6,seed=0)
    rep={'score':r.score,'sem':r.sem,'acceptance':r.acceptance,'n_2q':r.n_2q,
         'passed':r.passed,'format':r.format_ok,'class':r.class_ok,'correctness':r.correct_ok,
         'acceptance_ok':r.acceptance_ok,'format_errors':r.format_errors,'class_error':r.class_error,
         'correctness_errors':r.correctness_errors}
    (OUT/(p.stem+'.check.json')).write_text(json.dumps(rep,indent=2)+'\n')
    print(p.stem,rep['passed'],rep['correctness'],rep['score'],rep['acceptance'],rep['correctness_errors'][:1])
# Real-grid check for the baseline only: this suffix is intentionally a grid-free price.
import importlib as _i
# reload symbols from grid for true format checking (the check function's qasm module sees the restored function).
g=_i.import_module('tprep.grid'); pa=_i.import_module('tprep.parse'); qa=_i.import_module('tprep.qasm')
# source function is imported from grid module itself
orig=g.__dict__['adjacent']
pa.adjacent=qa.adjacent=orig
p=OUT/'base.qasm'; meta=json.loads((OUT/'base.json').read_text()); r=check(p.read_text(),meta['data_qubits'],shots=10**3,seed=0)
(OUT/'base.real_grid.check.json').write_text(json.dumps({'format_errors':r.format_errors,'class_error':r.class_error,'correctness_errors':r.correctness_errors,'passed':r.passed},indent=2)+'\n')
print('real_grid',r.passed,r.format_errors[:2])
