"""Seed equivalence cache only from completed exact2 receipts."""
from common import *
import categorical_cache as cc
import concurrent.futures
def one(p):
 stem=p.with_suffix('').with_suffix('');row=json.loads(p.read_text())
 if abs(row['c1'])>=1e-12:return None
 ev=exact2.Eval(stem.with_suffix('.qasm').read_text(),json.loads(stem.with_suffix('.json').read_text())['data_qubits']);key=cc.fingerprint(ev);q=cc.path(key)
 if q.exists():
  prev=json.loads(q.read_text());assert abs(prev['second']-row['second'])<1e-15 and abs(prev['third']-row['third'])<1e-15,(p,prev,row)
 else:cc.store(key,dict(stem=str(stem),second=row['second'],third=row['third']))
 return key
if __name__=='__main__':
 paths=list(H.glob('*.price.json'))
 with concurrent.futures.ThreadPoolExecutor(4)as pool:keys=list(pool.map(one,paths))
 print(json.dumps(dict(completed_receipts=len(paths),distinct_keys=len(set(keys)),all_equalities_checked=True)),flush=True)
