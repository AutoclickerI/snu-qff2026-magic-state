import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));import pop36_support as v
from concurrent.futures import ProcessPoolExecutor,as_completed
p=Path(sys.argv[1]);jobs=json.loads(p.read_text());rows=[]
with ProcessPoolExecutor(int(sys.argv[2]))as pool:
 fs={pool.submit(v.a.score,(str(v.H/j['stem']),j['description'])):j for j in jobs if not(v.H/j['stem']).with_suffix('.score.json').exists()}
 for f in as_completed(fs):
  r=f.result();rows.append(r);print(r['stem'],r.get('loss'),r.get('acceptance'),r.get('error'),flush=True)
p.with_name('results.json').write_text(json.dumps(dict(rows=rows),indent=2))
