import json,os,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
rows=[]
for p in HERE.glob('clean_*.score.json'):
    r=json.loads(p.read_text())
    if r.get('exact',{}).get('total') is not None:rows.append((r['exact']['total'],p.name[:-11]))
assert rows
rows.sort();print('EXACT RANK',rows,flush=True)
best=rows[0][1]
subprocess.run([str(ROOT/'.venv/bin/python'),str(HERE/'minit_scan.py'),str(HERE/best),'--procs',sys.argv[1],'--mc'],check=True)
