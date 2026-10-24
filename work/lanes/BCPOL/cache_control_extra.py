import os,sys
sys.dont_write_bytecode=True
from pathlib import Path
H=Path(__file__).resolve().parent
from synth import verify
from build import build
from boundary_api import *
import json
base=json.loads((H/'inputs/base.prep.json').read_text());base.update(kind='policy',value=9)
_,md=build(base,dict(timing='project'));init=md['init_times'];base['ops'][7].append([6,12]);base['ops'][8].append([6,12]);v=verify(base);assert v['stim_target_pass'] and v['policy_pass']
text,md=build(base,dict(timing='alap',fixed_init=init));stem=H/'inputs/cache_insert_6_12';stem.with_suffix('.qasm').write_text(text);stem.with_suffix('.json').write_text(json.dumps(md,indent=2));c=AllOrdersCache(H/'inputs/replay_policy.boundary_allorders.npz');p=prepare_candidate(stem);out=c.score(p);stem.with_suffix('.cached_allorders.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
