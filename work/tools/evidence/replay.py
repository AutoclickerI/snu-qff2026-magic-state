"""Cheaply rank saved coordinate programs without doing contractions or training."""
import json
from pathlib import Path
import sys
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
from qtools.evaluator import sparse_walsh as sw
from qtools.registry import load_registry

all_bases = load_registry()['bases']
for path in sorted((HERE / 'tests/fixtures/bases').glob('earlier*.json')):
    for key, ops in json.loads(path.read_text())['bases'].items():
        all_bases[path.stem + ':' + key] = ops
for name in ('v37h', 'v37i'):
    m, e, groups, nd, ks, *_ = sw.prepare(HERE / 'tests/fixtures' / name, True)
    records = []
    for key, warm in all_bases.items():
        ops, cost = sw.search_basis(m, e, groups, nd, set(ks), warm, trials=0)
        records.append(dict(key=key, work=cost[0], width=cost[1], operations=len(ops)))
    print(json.dumps(dict(name=name, replays=sorted(records, key=lambda r: (r['work'], r['width'])))), flush=True)
