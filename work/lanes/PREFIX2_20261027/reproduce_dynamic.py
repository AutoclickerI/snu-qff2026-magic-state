"""Rebuild representative phase/flag networks and verify exact QASM hashes."""
import hashlib, json
from pathlib import Path
import dynamic_guard
import dynamic_schedule
import flag6
H = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    dest = H / 'rebuilt'
    dest.mkdir(exist_ok=True)
    families = ['flag6', 'guarded', 'guarded_layer', 'dynamic9', 'dynamic11', 'dynamic_schedule']
    out = []
    for family in families:
        rec = json.loads((H / f'{family}_best.json').read_text())
        original = Path(rec['stem'])
        meta = json.loads(original.with_suffix('.json').read_text())
        if family == 'dynamic_schedule':
            rebuilt = dynamic_schedule.build(Path(meta['parent']), str(dest / original.name),
                                             meta['early'], meta['omit_dead_reset'])
        elif family.startswith('dynamic'):
            rebuilt = dynamic_guard.build(meta['synthesis'], str(dest / original.name))
        else:
            rebuilt = flag6.build(meta['synthesis'], str(dest / original.name))
        expected = sha(original.with_suffix('.qasm'))
        actual = sha(rebuilt.with_suffix('.qasm'))
        row = dict(family=family, original=str(original), rebuilt=str(rebuilt),
                   expected_qasm_sha256=expected, actual_qasm_sha256=actual, identical=expected == actual)
        out.append(row)
        print(json.dumps(row), flush=True)
        assert expected == actual, row
    (H / 'reproduction.json').write_text(json.dumps(out, indent=2) + '\n')


if __name__ == '__main__':
    main()
