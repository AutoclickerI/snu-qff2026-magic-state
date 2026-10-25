"""Exact structural checks of EVALF/sparse against EVALF/base on one stem: modelcheck.py <stem>.
- every fault's (x, z, p, chan, s, d, e, record_flips) is identical between the two frontends;
- the bitset minfill returns base minfill's order, width and work on the channel scopes (plain and chosen basis);
- every channel's character table has two levels up to roundoff (uniform channel), and merging keeps every channel exactly once.
Prints one JSON line."""
import importlib.util, json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent

def load(d, name):
    sys.path.insert(0, str(HERE / d))
    for mod in ('frontend', 'fastfill', 'judge_subset', 'judge_subset.noise', 'judge_subset.qasm', 'judge_subset.parse',
                'judge_subset.grid'):
        sys.modules.pop(mod, None)
    spec = importlib.util.spec_from_file_location(name, HERE / d / 'sparse_walsh.py')
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    sys.path.pop(0)
    return mod

stem = Path(sys.argv[1]).resolve()
base = load('base', 'sw_base')
new = load('sparse', 'sw_new')
mb, eb, gb, nd, ksb, *_ = base.prepare(stem, True)
mn, en, gn, ndn, ksn, *_ = new.prepare(stem, True)
assert nd == ndn and ksb == ksn
keys = ('x', 'z', 'p', 'chan', 's', 'd', 'e', 'record_flips', 'm', 'pauli')
fault_mismatch = sum(any(fb[k] != fn[k] for k in keys) for fb, fn in zip(mb.faults, mn.faults)) + abs(len(mb.faults) - len(mn.faults))
plain = base.compile_channels(mb, gb, nd, ksb)
ob = base.minfill([set(s) for s, _, _ in plain]); on = new.minfill([set(s) for s, _, _ in plain])
order_same = ob['order'] == on['order'] and ob['width'] == on['width'] and ob['work_entries'] == on['work_entries']
cb, elb = base.compile_best(mb, eb, gb, nd, ksb)
cn, eln = new.compile_best(mn, en, gn, nd, ksn)
best_same = elb['order'] == eln['order'] and elb['width'] == eln['width'] and elb['work_entries'] == eln['work_entries']
spread = max(float(abs(chi[1:] - chi[-1]).max(initial=0)) for e in cn for _, chi in e[3])   # nontrivial levels' spread
levels = {}
for e in cn:
    for c, chi in e[3]:
        levels.setdefault(len(chi), 0); levels[len(chi)] += 1
sources = sorted(c for e in cn for c, _ in e[3])
# each merged entry's scope equals the base scope of each of its channels (same plan coordinates)
base_scope = {c: s for c, (s, _, _) in zip(gb, cb)} if len(cb) == len(gb) else None
scope_same = base_scope is not None and all(base_scope[c] == e[0] for e in cn for c, _ in e[3] if base_scope[c] or e[0])
print(json.dumps(dict(stem=stem.name, faults=len(mn.faults), fault_mismatch=fault_mismatch, minfill_order_same=order_same,
                      compile_best_plan_same=best_same, channels=len(gn), entries=len(cn), channels_once=sources == sorted(gn),
                      scopes_match_base=scope_same, nontrivial_level_spread=spread, generators_per_channel=levels,
                      width=eln['width'], work=eln['work_entries'])), flush=True)
