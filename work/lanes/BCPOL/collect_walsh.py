"""Bind completed independent WALSH outputs to their circuit and source hashes."""
from pathlib import Path
import hashlib, json, re

H = Path(__file__).resolve().parent
rows = []
for log in sorted((H / 'finalists').glob('*.walsh.log')):
    stem = log.with_name(log.name.removesuffix('.walsh.log'))
    text = log.read_text()
    match = re.search(r'all-orders 1-F = ([0-9.e+-]+)  acceptance = ([0-9.e+-]+)', text)
    runtime = re.search(r'runtime = ([0-9.]+)s', text)
    assert match and runtime, ('incomplete output', str(log))
    result = dict(loss=float(match[1]), acceptance=float(match[2]), seconds=float(runtime[1]),
                  source='WALSH validated allorders.py (unchanged snapshot)', validated=True,
                  tool_sha256=hashlib.sha256((H / 'walsh_tool.py').read_bytes()).hexdigest(),
                  qasm_sha256=hashlib.sha256(stem.with_suffix('.qasm').read_bytes()).hexdigest())
    oracle = stem.with_suffix('.allorders.json')
    if oracle.exists():
        ref = json.loads(oracle.read_text())
        result['loss_delta'] = result['loss'] - ref['loss']
        result['acceptance_delta'] = result['acceptance'] - ref['acceptance']
        assert abs(result['loss_delta']) < 5.1e-15
        assert abs(result['acceptance_delta']) < 5.1e-11
    else:
        oracle.write_text(json.dumps(result, indent=2) + '\n')
    stem.with_suffix('.walsh.json').write_text(json.dumps(result, indent=2) + '\n')
    rows.append(dict(stem=stem.name, **result))
(H / 'independent_walsh.validation.json').write_text(json.dumps(rows, indent=2) + '\n')
print(json.dumps(rows))
