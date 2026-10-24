import argparse,json,os,subprocess
from pathlib import Path
from run_synth import workers
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];PY=str(ROOT/'.venv/bin/python')
def one(stem):
    stem=Path(stem).resolve();meta=json.loads(stem.with_suffix('.json').read_text());R=meta.get('R',50)
    for tag,flags in [('pairs',['--pairs']),('waitscale',['--wait-scale','0,0.5,1'])]:
        out=Path(str(stem)+'.'+tag+'.log')
        if out.exists() and ('weight-3 term' if tag=='pairs' else 'wait x1.000') in out.read_text():continue
        n=workers(22)
        cmd=[PY,str(HERE/'ablate.py'),str(stem.with_suffix('.qasm')),'--pre-end','32','--round-start',str(R),'--a','1,14,8,9,2,16,15','--procs',str(n)]+flags
        with out.open('w') as f:subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,check=True)
        print('ABLATION',stem.name,tag,flush=True)
        if os.environ.get('COMBO5_SYNC_ABLATION')=='1':
            subprocess.run(['rsync','-az','-e','ssh -q -o ControlMaster=no -o ControlPath=none','--exclude','.submit_credentials',str(out),f'sunfish:{out.parent}/'],check=True)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('stems',nargs='*');a=ap.parse_args()
    if a.stems:stems=[Path(x) for x in a.stems]
    else:
        scan=json.loads((HERE/'clean_d14_late3_s0.minit_scan.json').read_text())
        name='clean_d14_late3_s0_m'+'_'.join(map(str,scan['picked']))
        stems=[HERE/name,HERE/'clean_d14_late3_s0_init/clean_d14_late3_s0_mall',HERE/'clean_d14_late3_s0_init/clean_d14_late3_s0_m27']
    for stem in stems:one(stem)
