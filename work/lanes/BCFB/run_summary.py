"""Freeze measured search coverage after every budget and finite sweep exits."""
import os,sys
sys.dont_write_bytecode=True
import json,sqlite3
from pathlib import Path
H=Path(__file__).resolve().parent
rows=[]
for p in sorted((H/'runs').glob('*.receipt.json')):rows.append(dict(file=p.name,**json.loads(p.read_text())))
long=[r for r in rows if r['file'].startswith('fast_s')]
assert len(long)==20 and all(r['status']=='BUDGET_FINISHED' for r in long),len(long)
assert any(r['file']=='initbest_fast_d15_c105_s526_00356_all.receipt.json' and r['status']=='COMPLETE' and r['prices']==16384 for r in rows)
exits=[json.loads(p.read_text()) for p in (H/'runs').glob('fast_s*.exit.json')];assert len(exits)==20 and all(r['exit_code']==0 for r in exits)
with sqlite3.connect(H/'search.sqlite') as db:
 groups=[dict(kind=k,stored=n,scored=s,best=b) for k,n,s,b in db.execute("select kind,count(*),count(value),min(value) from prices where kind!='prior_evidence' group by kind")]
 statuses=[dict(kind=k,status=s,count=n) for k,s,n in db.execute("select kind,json_extract(row,'$.status'),count(*) from prices where kind!='prior_evidence' group by kind,json_extract(row,'$.status')")]
out=dict(status='ALL_REQUESTED_BUDGETS_COMPLETE',long_seeds=long,receipts=rows,groups=groups,statuses=statuses,long_wall_seconds=sum(r['seconds'] for r in long),long_solver_seconds=sum(r['solver_seconds'] for r in long));(H/'RUN_SUMMARY.json').write_text(json.dumps(out,indent=2));print(json.dumps(dict(long_seeds=len(long),stored=sum(g['stored'] for g in groups),groups=groups)))
