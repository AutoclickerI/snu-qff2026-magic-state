from search import *
import runpy

def verify_one(stem):
 p=OUT/stem;text=p.with_suffix('.qasm').read_text();data=json.loads(p.with_suffix('.json').read_text())['data_qubits'];row=json.loads(p.with_suffix('.exact.json').read_text())
 t=time.monotonic();preview=fast_check.check(text,data,shots=100_000,seed=0,procs=1);elapsed=time.monotonic()-t
 row['runtime_1e5_seconds']=elapsed;row['runtime_pass']=elapsed<3.0
 print(stem,'1e5',elapsed,'seconds',flush=True)
 if row['runtime_pass']:
  t=time.monotonic();r=tprep.check(text,data,shots=1_000_000,seed=0);row.update(check=r.passed,check_acceptance=float(r.acceptance),check_repr=str(r),judge_seconds=time.monotonic()-t)
 else:row.update(check=False,exclusion='1e5 judge >3 sec; state-reuse slow branch')
 p.with_suffix('.verified.json').write_text(json.dumps(row,indent=2)+'\n')
 with(OUT/'verified_results.jsonl').open('a')as f:f.write(json.dumps(row)+'\n')
 report();print(json.dumps(row),flush=True)
 return row

if __name__=='__main__':
 if sys.argv[1]=='mc':
  sys.argv=[str(OUT/'inputs/mc3.py'),*sys.argv[2:]];runpy.run_path(str(OUT/'inputs/mc3.py'),run_name='__main__')
 elif sys.argv[1]=='exact':
  sys.argv=[str(OUT/'inputs/exact2.py'),*sys.argv[2:]];runpy.run_path(str(OUT/'inputs/exact2.py'),run_name='__main__')
 else:
  for name in sys.argv[1:]:verify_one(name)
