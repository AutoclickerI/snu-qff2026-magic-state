"""End-to-end paired subprocess benchmark, including startup and result serialization.

16 workers are intentionally not run: this task permits at most 8 processes.
"""
import json
import os
from pathlib import Path
import statistics
import subprocess
import sys
import time

LANE = Path(__file__).resolve().parents[1]
REPO = LANE.parents[2]
REL = Path('work/lanes/MAIN/sparse/sparse_walsh.py')
CIRCUITS = [REPO/f'work/lanes/MAIN/{s}' for s in ('v36h','v36g','v36c')]
CIRCUITS += [REPO/'work/lanes/MAIN/sparse/examples/v29c']
CIRCUITS += [REPO/f'work/lanes/IFACE/builds/{s}' for s in ('if_d','if_h','if_e','if_j','if_hdej')]

def main():
    receipt = dict(status='RUNNING', timings=[], process_limit=8, untested_process_counts=[16])
    target = LANE/'receipts/02_selector.json'
    if target.exists():
        receipt = json.loads(target.read_text())
    for stem in CIRCUITS:
        for workers in (1, 7):
            if any(r['circuit'] == str(stem.relative_to(REPO)) and r['workers'] == workers for r in receipt['timings']):
                continue
            pairs = []
            for repeat in range(3):
                got = {}
                for version in (('baseline','patched') if repeat % 2 == 0 else ('patched','baseline')):
                    script = LANE/version/REL
                    begin = time.perf_counter()
                    run = subprocess.run([sys.executable,str(script),str(stem),'72','canonical',str(workers)],
                                         cwd=LANE, capture_output=True, text=True)
                    elapsed = time.perf_counter()-begin
                    log = LANE/f'receipts/selector_{stem.name}_{workers}_{repeat}_{version}.log'
                    log.write_text(run.stdout+'\n'+run.stderr)
                    if run.returncode:
                        raise RuntimeError(f'{log}: exit {run.returncode}')
                    out = json.loads(script.with_name(stem.name+'_canonical_sparse_result.json').read_text())
                    got[version] = (elapsed,out)
                old, new = got['baseline'], got['patched']
                delta = max(abs(a['value']-b['value']) for a,b in zip(old[1]['results'],new[1]['results']))
                assert len(old[1]['results']) == len(new[1]['results']) == 73
                assert delta <= 1e-15, (stem,workers,delta)
                pairs.append(dict(baseline_seconds=old[0],patched_seconds=new[0],max_moment_delta=delta,
                                  acceptance=new[1]['acceptance'], loss=new[1]['loss']))
            oldtime = statistics.median(p['baseline_seconds'] for p in pairs)
            newtime = statistics.median(p['patched_seconds'] for p in pairs)
            row = dict(circuit=str(stem.relative_to(REPO)),workers=workers,pairs=pairs,
                       baseline_median=oldtime,patched_median=newtime,speedup=oldtime/newtime)
            receipt['timings'].append(row)
            target.write_text(json.dumps(receipt,indent=2)+'\n')
            print(json.dumps(row),flush=True)
    receipt['status'] = 'REJECT_DEPLOYMENT: numerics pass; parallel regressions; 16 processes prohibited'
    receipt['max_moment_delta'] = max(p['max_moment_delta'] for r in receipt['timings'] for p in r['pairs'])
    receipt['summary'] = {str(w):dict(min_speedup=min(r['speedup'] for r in receipt['timings'] if r['workers']==w),
                                     max_speedup=max(r['speedup'] for r in receipt['timings'] if r['workers']==w),
                                     median_speedup=statistics.median(r['speedup'] for r in receipt['timings'] if r['workers']==w))
                          for w in (1,7)}
    receipt['16_process_seconds'] = None
    target.write_text(json.dumps(receipt,indent=2)+'\n')

if __name__ == '__main__':
    main()
