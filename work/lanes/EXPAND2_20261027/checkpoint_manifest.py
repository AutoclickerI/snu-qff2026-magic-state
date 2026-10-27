"""Select reproducible source, circuit witnesses, and experiment ledgers."""
import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
old=json.loads((HERE/'selected_files.json').read_text())
old=old if isinstance(old,list) else old['files']
paths={ROOT/r['path'] for r in old}
paths.update(HERE.glob('*.py'))
paths.update(HERE/p for p in ['REPORT.md','axis_frontend_verification.json',
    'relaxed_a_results.json','parked_results.json','original_a_results.json',
    'leaderboard_20261027.json'])
for folder in ['axis_echo','between_checks','b_phase']:
    paths.update(p for p in (HERE/folder).rglob('*') if p.suffix in ('.qasm','.json') and not p.name.endswith('.pairs.json') and p.name!='control_pairs.json')
paths.update((HERE/'logical_readout').glob('results*.json'))
paths.add(HERE/'logical_readout/choices.json')
for folder in (HERE/'source_variants').iterdir():
    if folder.is_dir():
        paths.update(p for p in folder.rglob('*') if p.suffix in ('.qasm','.json') and not p.name.endswith('.pairs.json'))
paths.add(HERE/'between_checks.log')
rows=[]
for path in sorted(paths):
    assert path.is_file(),path
    value=path.read_bytes()
    rows.append(dict(path=str(path.relative_to(ROOT)),bytes=len(value),sha256=hashlib.sha256(value).hexdigest()))
(HERE/'selected_files.json').write_text(json.dumps(rows,indent=2)+'\n')
print(json.dumps(dict(files=len(rows),bytes=sum(r['bytes'] for r in rows))))
