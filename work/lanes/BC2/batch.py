"""Bounded solver batch. Waits on process exits; logs capacity before each launch."""
import argparse
import concurrent.futures
import json
import os
from pathlib import Path
import subprocess
import sys

P = '/home/jihoon/competitions/quantumn/.venv/bin/python'
for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'


def run(job):
    name, args = job
    cores = int(subprocess.check_output(['nproc', '--all']))
    load = Path('/proc/loadavg').read_text().strip()
    print('LAUNCH', name, 'nproc', cores, 'loadavg', load, flush=True)
    if float(load.split()[0]) + 1 > .75 * cores:
        Path(name + '.capacity.json').write_text(json.dumps(dict(cores=cores, load=load, status='capacity blocked')))
        return name, 'capacity blocked'
    with open(name + '.log', 'w') as log:
        p = subprocess.run([P, 'sat6.py', *args, '--out', name], stdout=log, stderr=subprocess.STDOUT)
    print('EXIT', name, p.returncode, flush=True)
    return name, p.returncode


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('mode', choices=['global', 'local'])
    ap.add_argument('--workers', type=int, default=12)
    a = ap.parse_args()
    jobs = []
    if a.mode == 'global':
        for rule in ('clean_literal', 'clean', 'robust', 'pairs'):
            for depth in (13, 14, 15, 16):
                for cap in (82, 100):
                    name = f'{rule}_d{depth}_k{cap}'
                    args = ['--rule', rule, '--depth', str(depth), '--cap', str(cap), '--seed', str(depth*100+cap), '--seconds', '240']
                    jobs.append((name, args))
    else:
        for rule in ('robust', 'clean', 'base'):
            for start in (0, 3, 6, 9):
                for cap in (78, 82):
                    name = f'window_{rule}_{start}_k{cap}'
                    args = ['--rule', rule, '--depth', '14', '--cap', str(cap), '--seed', str(start+cap), '--seconds', '150',
                            '--initial', 'baseline_prep.json', '--free', ','.join(map(str,range(start,min(start+5,14))))]
                    jobs.append((name, args))
    with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as pool:
        results = list(pool.map(run, jobs))
    Path('batch_' + a.mode + '.json').write_text(json.dumps(results, indent=2))
