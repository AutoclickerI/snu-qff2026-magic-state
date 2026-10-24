import json
from pathlib import Path
h = Path(__file__).resolve().parent
rows = json.loads((h / 'control_R38.guard_candidates.json').read_text())
valid = [r for r in rows if 'stem' in r]
valid.sort(key=lambda r: (
    r['action']['type'] == 'echo',
    0 if r['action'].get('q') in (13, 26) else 1,
    -(r['action'].get('last', 0) - r['action'].get('first', 0)),
))
names = [r['stem'] for r in valid]
(h / 'hippo_guards_queue.json').write_text(json.dumps(names[::3]))
(h / 'tom_guards_queue.json').write_text(json.dumps([n for i, n in enumerate(names) if i % 3]))
print('guard plans', len(names))
