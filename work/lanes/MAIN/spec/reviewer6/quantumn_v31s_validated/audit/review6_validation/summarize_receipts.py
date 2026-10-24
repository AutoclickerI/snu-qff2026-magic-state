"""Summarize completed official receipts without rerunning any circuit."""
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
rows = []
for path in sorted(HERE.glob('*.official_*.json')):
    if path.name.endswith('.progress.json'):
        continue
    data = json.loads(path.read_text())
    report = data.get('report', {})
    stage_name = f"_sample({data['shots']} shots)"
    rows.append(dict(
        name=path.name.split('.official_')[0],
        sha256=data['target']['qasm_sha256'],
        shots=data['shots'],
        all_gates_passed=data.get('gates', {}).get('passed'),
        check_seconds=data.get('check_seconds'),
        sampling_seconds=next((s['seconds'] for s in data.get('stages', []) if s['stage'] == stage_name), None),
        acceptance=report.get('acceptance'), score=report.get('score'),
        sem=report.get('sem'), CX=report.get('n_2q'), depth=data.get('native_depth')))
(HERE / 'summary.json').write_text(json.dumps(rows, indent=2) + '\n')
print(json.dumps({'completed_receipts':len(rows), 'all_pass':all(r['all_gates_passed'] for r in rows)}))
