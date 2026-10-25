"""Controller signaling, finite-threshold scheduling, comparator wiring. Never runs live scripts."""
import json
import math
import multiprocessing as mp
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time

LANE = Path(__file__).resolve().parents[1]
REPO = LANE.parents[2]
sys.path[:0] = [str(LANE/'patched/work'),str(REPO/'work')]
sys.path.insert(0,str(LANE/'stages/04-safe/work'))
import race
from race_checkpoint import Journal
from race_control import register_controller, request_stop
from race_threshold import controller_threshold, cx_count, first_losing


def signal_child(path, pipe):
    stopped = False
    def handler(*_):
        nonlocal stopped
        stopped = True
    signal.signal(signal.SIGUSR1,handler)
    register_controller(path,'isolated-test')
    pipe.send('ready')
    while not stopped:
        signal.pause()


def main():
    results = {}
    with tempfile.TemporaryDirectory(dir=LANE/'receipts') as td:
        root = Path(td)
        (root/'receipts').mkdir();(root/'submissions').mkdir()
        (root/'receipts/race_incumbent.json').write_text((LANE/'patched/work/receipts/race_incumbent.json').read_text())
        # Mirror only the required non-secret receipts and submitted metadata.
        for p in (REPO/'work/receipts').glob('seq_*.txt'):
            (root/'receipts'/p.name).write_text(p.read_text())
            meta = REPO/'work/submissions'/f'{p.stem[4:]}.json'
            if meta.exists():
                (root/'submissions'/meta.name).write_bytes(meta.read_bytes())
        cut = controller_threshold(REPO/'work/lanes/MAIN/v36h.qasm',root)
        records = [(3.53e-5,327,'task incumbent')]
        for receipt in (root/'receipts').glob('seq_*.txt'):
            if 'RESULT: PASS' in receipt.read_text():
                meta=json.loads((root/'submissions'/f'{receipt.stem[4:]}.json').read_text())
                records.append((float(format(meta['score'],'.3g')),meta['n_2q'],receipt.name))
        key,cx,source=min(records)
        assert cut == first_losing(key,cx,327)
        results['receipt_wiring'] = dict(cut=cut,cx=cx_count(REPO/'work/lanes/MAIN/v36h.qasm'),
                                         strongest_receipt=dict(key=key,cx=cx,source=source))
        # Only this child PID is signaled; exit is observed through pidfd + join.
        parent,child = mp.Pipe()
        proc = mp.Process(target=signal_child,args=(root/'pid.json',child))
        proc.start();assert parent.recv() == 'ready'
        try:
            assert request_stop(root/'pid.json')
            proc.join();assert proc.exitcode == 0
        finally:
            if proc.is_alive():
                os.kill(proc.pid,signal.SIGUSR1)
                proc.join()
        assert request_stop(root/'absent.json') is False
        assert request_stop(root/'pid.json') is False
        results['controller'] = 'PASS: registered test child SIGUSR1 and exit; absent racer skipped'
        # Finite threshold selection: very good prefix beats fresh cost, bad prefix defers.
        rng = race.np.random.default_rng(123)
        a,loss = .5016415049479505,3.815473322483099e-5
        tau = 3.525e-5
        race._G.update(exact=(a,a*loss),totals=list(rng.normal(1e6*a*loss,4.,128)),
                       kepts=[501641]*128)
        header = dict(variant=99)
        outcomes = []
        for name,s in [('good',10.),('bad',30.)]:
            with Journal(root/f'{name}.json',header) as journal:
                for _ in range(30):
                    journal.append((501641,0,s,s*s),race._G['totals'],race._G['kepts'])
                choice = race._resume_worthwhile(journal,tau)
                assert choice == (name == 'good')
                outcomes.append(dict(prefix=name,resume=choice))
        results['finite_threshold_scheduler'] = outcomes
        fresh_p,fresh_cost = race._fresh_value(tau)
        assert 0 < fresh_p < 1 and 1 <= fresh_cost <= 100
        results['fresh_model'] = dict(win_probability=fresh_p,expected_chunks=fresh_cost)
    for path in (LANE/'patched/work').glob('*.sh'):
        subprocess.run(['bash','-n',str(path)],check=True)
    for path in (LANE/'patched/work/receipts').glob('*.sh'):
        subprocess.run(['bash','-n',str(path)],check=True)
    # Compile in memory: no writes of pyc to any live directory.
    for path in (LANE/'patched').rglob('*.py'):
        compile(path.read_text(),str(path),'exec')
    (LANE/'receipts/integration.json').write_text(json.dumps(dict(status='PASS',results=results),indent=2)+'\n')
    print(json.dumps(results))


if __name__ == '__main__':
    main()
