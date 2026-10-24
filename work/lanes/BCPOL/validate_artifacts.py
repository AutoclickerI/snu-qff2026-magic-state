"""Check retained receipts against the actual circuits and full reference logs."""
from pathlib import Path
import hashlib, json, math, re

H = Path(__file__).resolve().parent
out = []
for p in sorted((H / 'finalists').glob('*.verified.json')):
    tag = p.name.removesuffix('.verified.json')
    stem = p.with_name(tag)
    receipt = json.loads(p.read_text())
    sha = hashlib.sha256(stem.with_suffix('.qasm').read_bytes()).hexdigest()
    assert sha == receipt['qasm_sha256'], tag
    md = json.loads(stem.with_suffix('.json').read_text())
    screen = json.loads(stem.with_suffix('.screen.json').read_text())
    speed = stem.with_suffix('.speed.log').read_text()
    exact = stem.with_suffix('.exact.log').read_text()
    assert ('passed=True' in speed) == receipt['judge_pass'], tag
    seconds = float(re.search(r'\(([0-9.]+)s, 1 procs', speed)[1])
    assert seconds == receipt['s_per_1e6'], tag
    assert (seconds <= 20 * receipt['calibration_s_per_1e6'] / 2.3) == receipt['speed_pass'], tag
    assert int(re.search(r'n_2q=(\d+)', speed)[1]) == md['CX'], tag
    match = re.search(r'first order : c1 p = ([0-9.e+-]+)', exact)
    assert match, (tag, 'missing completed exact output')
    c1 = float(match[1])
    total = float(re.search(r'1-F \(to 3rd order\) = ([0-9.e+-]+)', exact)[1])
    assert abs(c1) < 1e-12 and abs(screen['c1']) < 1e-12, tag
    # exact2 prints six significant figures; compare at that precision.
    assert abs(total - screen['total']) <= 5.1e-6 * abs(total), (tag, total, screen['total'])
    record = dict(stem=tag, qasm_sha256=sha, cli_cubic=total,
                  cubic_screen=screen['total'], s_per_1e6=seconds,
                  judge_pass=receipt['judge_pass'], speed_pass=receipt['speed_pass'])
    mc = stem.with_suffix('.mc.log')
    if receipt.get('mc'):
        text = mc.read_text()
        seeds = [(int(s), float(v), float(a)) for s, v, a in re.findall(
            r' (0|1000|2000) ([0-9.e+-]+) .*? acc ([0-9.]+)', text)]
        assert [r[0] for r in seeds] == [0, 1000, 2000], tag
        mean = float(re.search(r' mean ([0-9.e+-]+)', text)[1])
        assert abs(mean - sum(r[1] for r in seeds)/3) < 1e-11, tag
        assert seeds[0][2] >= .5 and screen['exp_minus_A1'] >= .5002, tag
        record.update(mc_mean=mean, seeds=seeds)
    oracle = stem.with_suffix('.allorders.json')
    if oracle.exists():
        record['allorders'] = json.loads(oracle.read_text())
    record['files'] = {q.name: hashlib.sha256(q.read_bytes()).hexdigest()
                       for q in (stem.with_suffix('.qasm'), stem.with_suffix('.json'),
                                 p, stem.with_suffix('.exact.log'), stem.with_suffix('.speed.log'))}
    out.append(record)
(H / 'artifacts.validation.json').write_text(json.dumps(out, indent=2) + '\n')
print(json.dumps(dict(checked=len(out), mc_finalists=sum('mc_mean' in r for r in out))))
