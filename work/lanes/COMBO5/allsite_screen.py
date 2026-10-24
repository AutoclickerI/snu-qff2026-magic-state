import argparse,json,subprocess
from pathlib import Path
from evaluate import score
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];PY=str(ROOT/'.venv/bin/python')
def make(name):
    base=HERE/name;dest=HERE/(name+'_allsite_build');dest.mkdir(exist_ok=True)
    subprocess.run([PY,str(HERE/'minit.py'),str(base),str(dest)],check=True)
    target=HERE/(name+'_mall')
    source=dest/(name+'_mall.qasm')
    target.with_suffix('.qasm').write_bytes(source.read_bytes())
    meta=json.loads(base.with_suffix('.json').read_text());meta['first_use_measured']='all'
    target.with_suffix('.json').write_text(json.dumps(meta,indent=2))
    for f in dest.iterdir():f.unlink()
    dest.rmdir()
    return target
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('names',nargs='+');ap.add_argument('--procs',type=int,default=16);a=ap.parse_args()
    for name in a.names:score(make(name),a.procs,True)
