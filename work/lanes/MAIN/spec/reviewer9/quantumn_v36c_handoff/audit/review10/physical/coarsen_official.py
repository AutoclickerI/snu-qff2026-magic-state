from pathlib import Path
import json,sys,dataclasses,time
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parents[2]/'official'))
import tprep
rows=json.loads((ROOT/'coarsen_results.json').read_text())['results']
receipts=[]
for row in rows:
 stem=ROOT/('v36c_coarse_'+row['name'])
 qasm=stem.with_suffix('.qasm').read_text();meta=json.loads(stem.with_suffix('.json').read_text())
 t=time.perf_counter();r=tprep.check(qasm,meta['data_qubits'],shots=1000000,seed=0)
 receipt={'name':row['name'],'seconds':time.perf_counter()-t,'official_commit':'76fe47c0324f1c1f8b72a7d55af200e88043b522','shots':1000000,'seed':0,'report':dataclasses.asdict(r)}
 receipts.append(receipt)
 (ROOT/'coarsen_official_receipts.json').write_text(json.dumps(receipts,indent=2))
 print(json.dumps({'name':row['name'],'gates':{k:getattr(r,k)for k in ['format_ok','class_ok','correct_ok','acceptance_ok','passed']},'seconds':receipt['seconds']}),flush=True)
