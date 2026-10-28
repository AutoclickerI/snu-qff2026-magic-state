"""Build hashed publication inventories; never change git refs or submit."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def entry(path):
    path = Path(path)
    raw = path.read_bytes()
    return dict(path=str(path.relative_to(ROOT)), bytes=len(raw),
                sha256=hashlib.sha256(raw).hexdigest())


def main():
    paths = set()
    for path in HERE.iterdir():
        if (path.is_file() and path.suffix in {'.py', '.json', '.md', '.log'}
                and path.name not in {'publish_manifest.json', 'checkpoint_manifest.json',
                                      'prior_native_candidates.json'}):
            paths.add(path)
    for directory in ['native_best', 'geometry_cand']:
        paths.update(p for p in (HERE / directory).iterdir()
                     if p.suffix in {'.qasm', '.json', '.log'})
    for pattern in ['*_best.json', '*_0.json', '*_results.json']:
        paths.update((HERE / 'joint_modules').glob(pattern))
    paths.add(HERE / 'schedule/results.json')
    parent = HERE / 'schedule/lateprep_0_25_11_61195e875ba71064_d6_20_19_10_2_22_16'
    paths.update(parent.with_suffix(suffix) for suffix in ['.qasm', '.json', '.result.json'])
    selected = [entry(p) for p in sorted(paths)]
    own_manifest = dict(
        scope='Selected root research files; every score is classified in REPORT.md.',
        status='SOTA not reached; no submission or production promotion.',
        selected_files=selected,
        total_selected_bytes=sum(r['bytes'] for r in selected),
        excluded=['Unselected schedule QASM', 'solver/evaluator caches', 'lock files',
                  'downloaded external environments', 'unlicensed third-party full source'],
    )
    (HERE / 'publish_manifest.json').write_text(json.dumps(own_manifest, indent=2) + '\n')

    all_paths = set(paths)
    all_paths.add(HERE / 'publish_manifest.json')
    summaries = []
    for lane, key in [('SOTA_SOURCE_20261028', 'selected_files'),
                      ('SOTA_RESOURCE_20261028', 'entries'),
                      ('SOTA_DETECT_20261028', 'files')]:
        folder = ROOT / 'work/lanes' / lane
        manifest = folder / 'publish_manifest.json'
        doc = json.loads(manifest.read_text())
        rows = doc[key]
        for row in rows:
            path = Path(row['path'])
            path = ROOT / path if str(path).startswith('work/') else folder / path
            actual = entry(path)
            assert actual['bytes'] == row['bytes'], actual['path']
            assert actual['sha256'] == row['sha256'], actual['path']
            all_paths.add(path)
        all_paths.add(manifest)
        summaries.append(dict(lane=lane, files=len(rows), bytes=sum(r['bytes'] for r in rows)))
    all_paths.update(ROOT / p for p in ['docs/PLAN.md', 'docs/SOTA.md'])
    rows = [entry(p) for p in sorted(all_paths)]
    for row in rows:
        assert not any(s in row['path'] for s in
                       ['/compiler_deps/', '/spidercss_src/', '/.venv/', '/vendor/', '/__pycache__/'])
    checkpoint = dict(
        scope='Selected publication inventory; excludes this self-referential inventory file.',
        status=own_manifest['status'],
        previous_research_head='c645a5f77ebfcb7db00c48c35e006d046e729470',
        prepared_main='82657bf8e1de91f40e9137f5a517e6f4dacd7518',
        publication='Blocked by automatic approval review pending explicit approval; branch unchanged.',
        upstream_files='Unchanged additional main files are listed in upstream_integration.json.',
        lanes=summaries, files=rows, count=len(rows),
        total_bytes=sum(r['bytes'] for r in rows),
    )
    (HERE / 'checkpoint_manifest.json').write_text(json.dumps(checkpoint, indent=2) + '\n')
    print(json.dumps(dict(root_files=len(selected), root_bytes=own_manifest['total_selected_bytes'],
                          checkpoint_files=len(rows), checkpoint_bytes=checkpoint['total_bytes'],
                          lanes=summaries)))


if __name__ == '__main__':
    main()
