"""Real xtim: 8 x 1e6 shots, split after chunk 3 across independent processes."""
import importlib.util
import json
import math
import multiprocessing as mp
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

LANE = Path(__file__).resolve().parents[1]
REPO = LANE.parents[2]
PATCH = LANE/'patched/work'
sys.path[:0] = [str(PATCH),str(REPO/'work')]
sys.path.insert(0,str(LANE/'stages/04-safe/work'))
from race_checkpoint import Journal, replay


def child(mode, directory):
    import race
    from race_identity import load_mean
    os.chdir(LANE)
    stem = REPO/'work/lanes/MAIN/v36h'
    text = stem.with_suffix('.qasm').read_text()
    data = json.loads(stem.with_suffix('.json').read_text())['data_qubits']
    exact = load_mean(LANE/'receipts/v36h.exact.json',text,data)
    race.N_CHUNKS = 8
    stop = mp.Event()
    race._init(text.split('\n'),data,race.signature(text),mp.Value('d',math.inf),
               str(directory/'threshold'),exact,stop,str(directory))
    seen = []
    original = race._chunk
    def sample(circuit,plan,k):
        out = original(circuit,plan,k)
        seen.append(k)
        if mode == 'partial' and k == 2:
            stop.set()
        return out
    race._chunk = sample
    begin = time.perf_counter()
    k,out,n,state = race.race(830021)
    elapsed = time.perf_counter()-begin
    if mode == 'partial':
        assert out is None and state == 'paused' and seen == [0,1,2]
    else:
        assert state == 'complete'
    obj = dict(mode=mode,seen=seen,new_chunks=n,state=state,seconds=elapsed,
               out=None if out is None else {k:v for k,v in out.items() if k != 'text'})
    (directory/f'{mode}.json').write_text(json.dumps(obj,indent=2)+'\n')
    print(json.dumps(obj),flush=True)


def main():
    root = LANE/'receipts/checkpoint'
    if root.exists():
        shutil.rmtree(root)
    root.mkdir()
    args = [sys.executable,str(PATCH/'race_exact.py'),str(REPO/'work/lanes/MAIN/v36h'),
            '--output',str(LANE/'receipts/v36h.exact.json'),
            '--evaluator',str(LANE/'baseline/work/lanes/MAIN/sparse')]
    subprocess.run(args,cwd=LANE,check=True)
    outputs = {}
    for mode,subdir in [('full','full'),('partial','split'),('resume','split')]:
        directory = root/subdir
        directory.mkdir(exist_ok=True)
        with (root/f'{mode}.log').open('w') as log:
            subprocess.run([sys.executable,__file__,mode,str(directory)],cwd=LANE,
                           stdout=log,stderr=subprocess.STDOUT,check=True)
        outputs[mode] = json.loads((directory/f'{mode}.json').read_text())
    keys = ('kept','corrected','total','total_sq','score','sem','acceptance','n_2q','passed')
    a,b = outputs['full']['out'],outputs['resume']['out']
    for k in keys:
        assert a[k] == b[k],(k,a[k],b[k])
    assert outputs['resume']['seen'] == [3,4,5,6,7]
    path = root/'split/r830021.json'
    saved = Journal.read(path)
    wrong = dict(saved['header'],environment_sha256='changed')
    try:
        with Journal(path,wrong):
            pass
    except ValueError:
        pass
    else:
        raise AssertionError('wrong environment accepted')
    # An interrupted temporary write never replaces the last durable snapshot.
    (root/'split/r830021.json.incomplete.tmp').write_text('{"broken":')
    assert Journal.read(path) == saved
    bad = root/'corrupt.json'
    obj = json.loads(path.read_text());obj['chunks'][0]['loss']='0x0p+0'
    bad.write_text(json.dumps(obj))
    try: Journal.read(bad)
    except ValueError: pass
    else: raise AssertionError('corrupt checkpoint accepted')
    receipt = dict(status='PASS',inputs=dict(stem='v36h',variant=830021,chunk_shots=1000000,
                   n_chunks=8,cut_after=3,threshold='inf'),outputs=outputs,
                   bit_identical_fields=list(keys),saved_chunks=3,saved_shots=3000000,
                   verification=['real xtim in distinct processes','seed indices resume at 3',
                                 'environment mismatch rejected','partial temp ignored','checksum rejects corruption'],
                   limitations=['finite-threshold tail throughput not measured','distributed cut not exercised'])
    (LANE/'receipts/04_checkpoint.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt))


if __name__ == '__main__':
    if len(sys.argv)>1:
        child(sys.argv[1],Path(sys.argv[2]))
    else:
        main()
