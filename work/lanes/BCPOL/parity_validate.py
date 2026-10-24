import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
H=Path(__file__).resolve().parent
from synth import Model,verify
import json
stem=H/'inputs/cache_rank5_parity';d=json.loads(stem.with_suffix('.json').read_text())['prep'];d['extra_check']=True
v=verify(d);assert v['stim_target_pass'] and v['policy_pass'];m=Model(len(d['ops']),sum(map(len,d['ops'])),997,d['kind'],d['value'],extra_check=True)
for t,ss in enumerate(m.sel):
 active={tuple(e) for e in d['ops'][t]}
 for e,z in ss.items():m.add([z if e in active else -z]);m.cut((t+1,e))
for t in range(m.D+1):
 for q in m.cells:m.cut((t,(q,)))
assert m.s.solve();vv=verify(m.candidate());assert vv['stim_target_pass'] and vv['policy_pass']
(H/'parity.model.validation.json').write_text(json.dumps(dict(fixed_seed_sat=True,verification=vv,signature_bits=len(m.h[0][m.cells[0]])),indent=2));print('EXTRA_PARITY_MODEL_VALIDATED')
