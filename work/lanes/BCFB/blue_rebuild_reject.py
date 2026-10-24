import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import sqlite3,json,zlib
from build import build,H
from evaluate import score
D=H/'blue';tag='blue_d15_c90_s708_00718'
with sqlite3.connect(D/'snapshot.sqlite') as db:raw,w=db.execute('select row,witness from prices where tag=?',(tag,)).fetchone()
w=json.loads(zlib.decompress(w));old=json.loads(raw);text,md=build(w['prep'],w['options']);r=score(text,md);assert abs(old['total']-r['total'])<1e-15;r.update(tag='reject_'+tag,context=w['options']['context'],options=md['options'],CX=md['CX']);p=D/'finalists'/r['tag'];p.with_suffix('.qasm').write_text(text);p.with_suffix('.json').write_text(json.dumps(md,indent=2));p.with_suffix('.screen.json').write_text(json.dumps(r,indent=2));print(r['tag'],r['total'],r['exp_minus_A1'])
