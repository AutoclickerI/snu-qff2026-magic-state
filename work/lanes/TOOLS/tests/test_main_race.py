"""Real xtim via main(): SIGUSR1, pool exit, next-hour content-keyed resume and promotion output."""
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys

LANE=Path(__file__).resolve().parents[1]
REPO=LANE.parents[2]
PATCH=LANE/'patched/work'
sys.path[:0]=[str(PATCH),str(REPO/'work')]
sys.path.insert(0,str(LANE/'stages/04-safe/work'))


def child(mode,root):
    import race
    os.chdir(root)
    race.N_CHUNKS=6
    parent_pid=os.getpid()
    orig=race._chunk
    seen=[]
    def sample(circuit,plan,k):
        out=orig(circuit,plan,k)
        # Writes are confined to this test directory, and signal only its controller.
        with (root/f'{mode}_sampled.txt').open('a') as f: f.write(str(k)+'\n')
        if mode == 'cut' and k == 1:
            os.kill(parent_pid,signal.SIGUSR1)
        return out
    race._chunk=sample
    stem=root/('hour_one' if mode=='cut' else 'hour_two')
    sys.argv=['race.py',str(stem),'1' if mode=='cut' else '0','1','830022']
    race.main()


def main():
    root=LANE/'receipts/main_race'
    if root.exists(): shutil.rmtree(root)
    root.mkdir()
    for name in ('hour_one','hour_two'):
        for suffix in ('.qasm','.json'):
            (root/(name+suffix)).write_bytes((REPO/'work/lanes/MAIN/v36h').with_suffix(suffix).read_bytes())
        (root/(name+'.exact.json')).write_bytes((LANE/'receipts/v36h.exact.json').read_bytes())
    for mode in ('cut','resume'):
        with (root/f'{mode}.log').open('w') as log:
            subprocess.run([sys.executable,__file__,mode,str(root)],cwd=root,
                           env=dict(os.environ,RACE_THRESHOLD='inf'),stdout=log,stderr=subprocess.STDOUT,check=True)
        if mode=='cut':
            assert not (root/'reorder/hour_one_r830022.json').exists()
    sampled={m:[int(x) for x in (root/f'{m}_sampled.txt').read_text().splitlines()] for m in ('cut','resume')}
    assert sampled == dict(cut=[0,1],resume=[2,3,4,5]),sampled
    out=json.loads((root/'reorder/hour_two_r830022.json').read_text())
    from race_checkpoint import Journal,replay
    checkpoint=next((root/'reorder/checkpoints').glob('*/r830022.json'))
    saved=Journal.read(checkpoint)
    assert saved['state']=='published' and len(saved['chunks'])==6
    vals=[(r['kept'],r['corrected'],float.fromhex(r['loss']),float.fromhex(r['loss_sq'])) for r in saved['chunks']]
    kept,corrected,total,sq=replay(vals)
    assert out['score']==max(total/kept,0.) and out['acceptance']==kept/6000000
    receipt=dict(status='PASS',sampled_indices=sampled,promotion_file=str(root/'reorder/hour_two_r830022.json'),
                 partial_promotion_absent=True,old_hour_to_new_hour_resume=True,final=out)
    (LANE/'receipts/04_main_race.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt))


if __name__=='__main__':
    if len(sys.argv)>1: child(sys.argv[1],Path(sys.argv[2]))
    else: main()
