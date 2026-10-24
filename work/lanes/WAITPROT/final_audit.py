"""Check completed receipts against their source bytes and independent screens."""
import hashlib
import json
import re
from pathlib import Path

from report import get, ref

H = Path(__file__).resolve().parent
rows = get('tick_singles.json') + get('subset_reference.json') + get('multi_reference.json')
assert len(rows) == len({r['stem'] for r in rows}) == 78
screens = {r['stem']: r for r in get('subset_screen.json') + get('multi_screen.json')}
screens.update({r['stem']: get(r['stem'] + '.screen.json') for r in get('tick_singles.json')})
receipts = []
for row in rows:
    stem = row['stem']
    digest = hashlib.sha256((H / (stem + '.qasm')).read_bytes()).hexdigest()
    receipt = get(stem + '.ref.exit.json')
    assert receipt['returncode'] == 0 and receipt['sha256'] == digest, stem
    values = ref(stem)
    assert all(k in values for k in ('second', 'third', 'total', 'acceptance_proxy')), stem
    log = (H / (stem + '.ref.log')).read_text()
    assert 'noiseless acceptance 1.000000' in log, stem
    first = float(re.search(r'first order : c1 p = ([0-9.e+-]+)', log).group(1))
    assert abs(first) < 1e-15, (stem, first)
    screen = screens[stem]
    for k in ('second', 'third', 'total'):
        assert float(f'{screen[k]:.6g}') == values[k], (stem, k, screen[k], values[k])
    assert screen['exp_minus_A1'] >= .5002, stem
    assert float(f'{screen["exp_minus_A1"]:.5f}') == values['acceptance_proxy'], stem
    receipts.append(dict(stem=stem, sha256=digest, unchanged_reference=True,
                         screen_matches_cli_printed_precision=True))

finalists = []
for p in sorted(H.glob('*.mc.json')):
    mc = json.loads(p.read_text())
    stem = mc['stem']
    gate = get(stem + '.gates.json')
    ao = get(stem + '.allorders.json')
    digest = hashlib.sha256((H / (stem + '.qasm')).read_bytes()).hexdigest()
    assert mc['returncode'] == 0 and [s['seed'] for s in mc['seeds']] == [0, 1000, 2000]
    assert all(s['acceptance'] >= .5 for s in mc['seeds']), stem
    assert gate['passed'] and gate['format'] and gate['correctness'], stem
    assert gate['speed']['classification'] == 'FAST', stem
    assert gate['sha256'] == ao['sha256'] == digest, stem
    assert ao['acceptance'] >= .5, stem
    assert ao['frontend_audit']['all_fault_signatures_match'], stem
    assert ao['frontend_audit']['all_rotations_projectors_observables_match'], stem
    finalists.append(dict(stem=stem, sha256=digest, gate_pass=True, fast=True,
                          mc_seeds=[0, 1000, 2000], allorders_audited=True))
assert len(finalists) == 7

artifacts = []
for alias in ('best', 'seed0_best'):
    metrics = get(alias + '.metrics.json')
    source = metrics['source_stem']
    for suffix in ('.qasm', '.json'):
        assert (H / (alias + suffix)).read_bytes() == (H / (source + suffix)).read_bytes()
    artifacts.append(dict(alias=alias, source=source, byte_identical=True))

report = (H / 'REPORT.md').read_text()
assert 'pending reference' not in report and 'MC is still running' not in report
width = None
for line in report.splitlines():
    if not line.startswith('|'):
        width = None
        continue
    current = len(line.split('|'))
    if width is None:
        width = current
    assert width == current, line
for target in re.findall(r'\]\(([^)]+)\)', report):
    assert (H / target).exists(), target

out = dict(status='COMPLETE', references=receipts, finalists=finalists,
           aliases=artifacts, reference_count=len(receipts), finalist_count=len(finalists),
           report_tables_and_links_valid=True)
(H / 'final_audit.json').write_text(json.dumps(out, indent=2) + '\n')
print(json.dumps({k: v for k, v in out.items() if k not in ('references', 'finalists', 'aliases')}))
