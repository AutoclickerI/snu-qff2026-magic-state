"""Record every data-path wait and every adjacent helper's free overlap."""
import json
import tick_build as t

rows = []
for logical, path in t.TRAJECTORIES.items():
    for q, begin, end in path:
        for before, after in zip(t.QOPS[q], t.QOPS[q][1:]):
            lo = max(18, begin, before['tick'] + 1)
            hi = min(47, end, after['tick'] - 1)
            if lo > hi:
                continue
            neighbours = []
            for h in t.adjacent(q):
                seq = [dict(name='UNUSED', tick=-1)] + t.QOPS[h] + [dict(name='END', tick=51)]
                free = []
                for prev, nxt in zip(seq, seq[1:]):
                    if prev['name'] not in ('UNUSED', 'M', 'MX'):
                        continue
                    flo, fhi = prev['tick'] + 1, nxt['tick'] - 1
                    if max(flo, lo) > min(fhi, hi):
                        continue
                    gadgets = []
                    for axis in ('Z', 'X'):
                        restore = ((axis == 'Z' and nxt['name'] == 'M') or
                                   (axis == 'X' and nxt['name'] == 'MX' and prev['name'] == 'MX'))
                        start, stop = max(lo, flo + 1), min(hi, fhi - 1 - int(restore))
                        if stop > start:
                            gadgets.append(dict(axis=axis, cx=[start, stop]))
                    free.append(dict(interval=[flo, fhi], previous=prev['name'],
                                     next=nxt['name'], fitting_gadgets=gadgets))
                neighbours.append(dict(helper=h, free_overlaps=free))
            rows.append(dict(logical_output=logical, stored_cell=q, idle=[lo, hi],
                             adjacent_helpers=neighbours))
# Including cells8 and9 independently confirms the output21 exclusion.
assert not any(g for r in rows if r['logical_output'] == 21
               for h in r['adjacent_helpers'] for f in h['free_overlaps']
               for g in f['fitting_gadgets'])
(t.H / 'trajectory_windows.json').write_text(json.dumps(dict(
    trajectories=t.TRAJECTORIES, idle_windows=rows,
    output21_has_no_fixed_schedule_helper=True), indent=2) + '\n')
print(json.dumps(dict(data_idle_windows=len(rows), output21_has_no_fixed_schedule_helper=True)))
