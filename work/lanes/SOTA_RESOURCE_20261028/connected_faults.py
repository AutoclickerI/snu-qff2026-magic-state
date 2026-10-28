import os,sys,json,collections
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
R=Path.cwd();H=R/'work/lanes/SOTA_RESOURCE_20261028';sys.path[:0]=[str(R/'work/tools'),str(R/'work/lanes/REBUILD20261027')]
from qtools.evaluator import frontend as f
from record_contract import singles
name=H/f'{sys.argv[1]}_diagnostic';meta=json.loads(name.with_suffix('.json').read_text());c=json.loads((H/f'{sys.argv[1]}_module.json').read_text())['roles'];f.DATA=meta['data_qubits'];ops,det=f.parse_current(name.with_suffix('.qasm').read_text());model=f.make_model(ops,det)
for ft in model.faults:
 op=model.labels[ft['ins']]
 if op.time<meta['R'] and (set(op.qs)<=set(c['D']) or set(op.qs)<=set(c['A'])):ft['p']=0
r=singles(model);by=collections.defaultdict(float)
for x in r['harmful_faults']:by[(x['time'],x['operation'],tuple(x['qubits']))]+=x['c1_contribution']
out={'c1':r['c1'],'fault_components':r['fault_components'],'top_operations':[{'time':t,'kind':k,'qubits':q,'c1':v} for (t,k,q),v in sorted(by.items(),key=lambda x:-x[1])[:40]],'harmful':r['harmful_faults']}
(H/f'{sys.argv[1]}_faults.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='harmful'},indent=2))
