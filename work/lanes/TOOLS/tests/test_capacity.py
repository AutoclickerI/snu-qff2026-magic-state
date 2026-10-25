import importlib.util
import json
from pathlib import Path
import re

LANE = Path(__file__).resolve().parents[1]
REPO = LANE.parents[2]
spec = importlib.util.spec_from_file_location('capacity',LANE/'patched/work/race_capacity.py')
m = importlib.util.module_from_spec(spec);spec.loader.exec_module(m)


def main():
    # A finite unit check verifies units, not a claim about historical idle capacity.
    b = dict(host='test',boot_id='b',clock_ticks=100,cores=64,monotonic_ns=0,idle_ticks=0)
    a = dict(b,monotonic_ns=3600*10**9,idle_ticks=8*3600*100)
    assert m.idle_between(b,a)['idle_core_minutes'] == 480
    script = (REPO/'work/receipts/race_specs.sh').read_text()
    assert '[ $procs -lt 4 ] && continue' in script
    assert '[ $procs -lt 4 ] && procs=4' not in script
    entries = []
    for label in ('v36h_h2516','v36h_h2517'):
        for host in ('owl','tom','jerry','hippo','sunfish','zebra'):
            path = REPO/f'work/reorder/{label}_{host}.log'
            text = path.read_text()
            drops = [int(s) for s in re.findall(r'dropped after (\d+) chunks',text)]
            done = len(re.findall(r' 1-F \S+ acc \S+ 2q \d+ pass (?:True|False)',text))
            entries.append(dict(host=host,hour_label=label,input=str(path.relative_to(REPO)),recorded_drops=len(drops),
                                recorded_completions=done,recorded_chunks=sum(drops)+100*done,
                                idle_core_minutes=None,allocated_workers=None,
                                reason='No timestamped CPU counters, start/end allocation, or lane-release events in log.'))
    known = list((REPO/'work/receipts').glob('*capacity*'))+list((REPO/'work/reorder').glob('*capacity*'))
    receipt = dict(status='REJECT_LEASE_NO_MEASURED_IDLE_GAP',examined_hour_labels=['h2516','h2517'],
                   host_records=entries,capacity_records_found=[str(p.relative_to(REPO)) for p in known],
                   forced_minimum_removed=True,unit_test='PASS: 8 idle cores x 60 minutes = 480 core-minutes',
                   proposed_change='event snapshots only; no worker allocation or lease change',
                   lease_design=None)
    (LANE/'receipts/05_capacity.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt))


if __name__ == '__main__':
    main()
