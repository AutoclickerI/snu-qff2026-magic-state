"""Verified seed-0 re-draw means; retain receipts, no loose bulk QASM."""
import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
CODE=Path(__file__).resolve().parent;ROOT=CODE.parents[2];H=CODE/'blue'
os.environ['XTIM_TWIRL_CACHE_DIR']=str(H/'.xtim_cache');sys.path.insert(0,str(ROOT/'work'))
import xtim
xtim.cache_dir=str(H/'.xtim_cache')
import reorder
import argparse,json,random,statistics,math,time
p=argparse.ArgumentParser();p.add_argument('stem');p.add_argument('--draws',type=int,default=100);p.add_argument('--procs',type=int,default=20);p.add_argument('--start',type=int,default=0);p.add_argument('--procs-file');a=p.parse_args();stem=Path(a.stem);stem=stem if stem.is_absolute() else H/'finalists'/stem
text=stem.with_suffix('.qasm').read_text();md=json.loads(stem.with_suffix('.json').read_text());lines=text.split('\n');ref=reorder.signature(text);rows=[]
out=H/'runs'/f'{stem.name}_redraw_{a.start}'
with out.with_suffix('.jsonl').open('w') as log:
 for k in range(a.start,a.start+a.draws):
  var='\n'.join(reorder.shuffle(lines,random.Random(k)));assert reorder.signature(var)==ref
  procs=int(Path(a.procs_file).read_text()) if a.procs_file else a.procs
  assert 1<=procs<=os.cpu_count()
  print(json.dumps(dict(event='capacity',cores=os.cpu_count(),load=os.getloadavg(),procs=procs)),flush=True)
  draw_start=time.monotonic()
  r=reorder.check(var,md['data_qubits'],shots=10**8,seed=0,procs=procs);assert r.passed and r.acceptance>=.5
  row=dict(draw=k,seconds=time.monotonic()-draw_start,score=r.score,acceptance=r.acceptance,sem=r.sem,procs=procs);rows.append(row);log.write(json.dumps(row)+'\n');log.flush();print(json.dumps(row),flush=True)
summary=dict(stem=str(stem),draws=len(rows),start=a.start,mean=statistics.mean(r['score'] for r in rows),sd=statistics.stdev(r['score'] for r in rows) if len(rows)>1 else None,sem=statistics.stdev(r['score'] for r in rows)/math.sqrt(len(rows)) if len(rows)>1 else None,min_acceptance=min(r['acceptance'] for r in rows));out.with_suffix('.summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary),flush=True)
