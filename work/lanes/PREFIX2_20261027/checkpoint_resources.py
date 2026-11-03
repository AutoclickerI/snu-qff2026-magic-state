"""Refresh the resource-work manifest without rewriting the prefix report."""
import datetime
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def main():
    manifest_path = HERE / 'selected_files.json'
    manifest = json.loads(manifest_path.read_text())
    selected = set(HERE.glob('*.py'))
    selected.update(HERE.glob('*.json'))
    selected.add(HERE / 'REPORT.md')
    selected.update(p for p in (HERE / 'retimed').glob('*') if p.is_file() and p.suffix in ('.py', '.json', '.qasm', '.log'))
    for ledger in (HERE / 'retimed').glob('*/results.json'):
        selected.add(ledger)
        data = json.loads(ledger.read_text())
        rows = data.get('candidates', [])
        representatives = rows[:1] + [r for r in rows if r.get('gate') == [6, 12] and r.get('times') == [38, 43]]
        for row in representatives:
            if 'stem' in row:
                p = Path(row['stem'])
                selected.update(p.with_suffix(s) for s in ('.qasm', '.json', '.pairs.json') if p.with_suffix(s).is_file())
        if (ledger.parent / 'base.pairs.json').is_file():
            selected.add(ledger.parent / 'base.pairs.json')
    selected.update(HERE.glob('retimed48*.log'))
    selected.discard(manifest_path)
    # Preserve the earlier selected prefix winners without expanding every
    # rejected stem mentioned by an old search ledger or another manifest.
    snapshot = json.loads((HERE / 'checkpoint_results.json').read_text())
    stems = {Path(r['stem']) for r in snapshot['families']}
    stems.update([HERE / 'cand/guarded_003_first0', HERE / 'cand/wide_constructive_s0',
                  HERE.parent / 'PREFIX20261027/cand/final_phase_random_1'])
    for stem in stems:
        selected.update(stem.with_suffix(s) for s in ('.qasm', '.json') if stem.with_suffix(s).is_file())
    for name in ('synth.py', 'search_phase.py', 'REPORT.md', 'selected_files.json'):
        selected.add(HERE.parent / 'PREFIX20261027' / name)
    for name in ('qcirc.py', 't14a.qasm', 't14a.stage.json'):
        selected.add(HERE.parent / 'T14' / name)
    native = HERE.parent / 'NATIVE2_20261027'
    for name in ('measured_assemble.py', 'dual_old_a_module.json', 'old_b_module.json',
                 'prefix_product_states.json', 'swapped_strong_b18.pairs.json'):
        selected.add(native / name)
    swap = native / 'boundary/swapped_strong_b18_5c0762c512b06bb7_d6_20_19_10_2_22_16'
    selected.update(swap.with_suffix(s) for s in ('.qasm', '.json', '.integration.json') if swap.with_suffix(s).is_file())
    discovery = set((HERE / 'retimed').glob('*.json'))
    discovery.update(p for p in selected if p.name.startswith('b_connected_cp') and p.suffix == '.json')
    discovery.add(native / 'dual_old_a_module.json')
    discovery.add(swap.with_suffix('.integration.json'))
    visited = set()

    def references(value):
        if isinstance(value, dict):
            for v in value.values():
                references(v)
        elif isinstance(value, list):
            for v in value:
                references(v)
        elif isinstance(value, str) and (value.startswith(str(ROOT) + '/') or value.startswith('work/')):
            path = Path(value) if value.startswith('/') else ROOT / value
            if path.is_file() and path.suffix in ('.py', '.json', '.qasm'):
                selected.add(path)
                if path.suffix == '.json' and path.name != 'selected_files.json':
                    discovery.add(path)
            if path.with_suffix('.qasm').is_file():
                for suffix in ('.qasm', '.json', '.integration.json', '.exact.json'):
                    p = path.with_suffix(suffix)
                    if p.is_file():
                        selected.add(p)
                        if p.suffix == '.json':
                            discovery.add(p)

    while True:
        pending = [p for p in discovery - visited if p.is_file()]
        if not pending:
            break
        for path in pending:
            visited.add(path)
            references(json.loads(path.read_text()))
    rows = []
    for path in sorted(selected):
        if path == manifest_path or not path.is_file():
            continue
        content = path.read_bytes()
        rows.append(dict(path=str(path.relative_to(ROOT)), bytes=len(content),
                         sha256=hashlib.sha256(content).hexdigest()))
    manifest.update(timestamp_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    files=rows, status='Native 48-tick verified factory and full noisy measurements retained; no incumbent improvement')
    manifest_path.write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps(dict(files=len(rows), bytes=sum(r['bytes'] for r in rows), manifest=str(manifest_path))))


if __name__ == '__main__':
    main()
