"""Exact-through-third-order selection of every first-use measurement site."""
import argparse,json,os,re,subprocess
from pathlib import Path
from evaluate import score
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];PY=str(ROOT/'.venv/bin/python')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('stem');ap.add_argument('--procs',type=int,default=22);ap.add_argument('--mc',action='store_true');a=ap.parse_args()
    stem=Path(a.stem).resolve();meta=json.loads(stem.with_suffix('.json').read_text())
    r=score(stem,a.procs,a.mc);base=r['exact']['total'];assert base is not None
    dest=HERE/(stem.name+'_init');dest.mkdir(exist_ok=True)
    subprocess.run([PY,str(HERE/'minit.py'),str(stem),str(dest)],check=True)
    picked=[];results={}
    # Evaluate each single-site transform and the simultaneous all-site transform.
    for p in sorted(dest.glob('*.qasm'),key=lambda p:(not p.stem.endswith('_mall'),p.name)):
        m=re.search(r'_m(\d+)$',p.stem);sites=[int(m.group(1))] if m else 'all'
        p.with_suffix('.json').write_text(json.dumps(dict(meta,first_use_measured=sites),indent=2))
        x=score(p.with_suffix(''),a.procs,a.mc)
        results[p.stem]=x
        if m and x.get('exact',{}).get('total',float('inf'))<base:
            picked.append(int(m.group(1)))
    receipt=dict(base=base,picked=picked,results=results)
    (HERE/(stem.name+'.minit_scan.json')).write_text(json.dumps(receipt,indent=2))
    if picked:
        subprocess.run([PY,str(HERE/'minit.py'),str(stem),str(HERE),','.join(map(str,picked))],check=True)
        target=HERE/(stem.name+'_m'+'_'.join(map(str,picked)))
        target.with_suffix('.json').write_text(json.dumps(dict(meta,first_use_measured=picked),indent=2))
        r=score(target,a.procs,a.mc)
        print('SELECTED',target,r.get('exact'),r.get('mean'),flush=True)

if __name__=='__main__':main()
