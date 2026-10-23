"""Resolve a cross-host roundoff difference by strict same-host sequential/parallel comparison."""
from search_v10 import *
import math
for label in sys.argv[1:]:
    path=HERE/(label+'.json');meta=json.loads(path.read_text())
    direct=meta['direct_tprep'];assert direct['passed'] and direct['shots']==10**8
    r=fast_check.check((HERE/(label+'.qasm')).read_text(),meta['data_qubits'],shots=10**8,seed=0,procs=3)
    row={'passed':bool(r.passed),'score':float(r.score),'seed':0,'shots':10**8,'report':str(r),
         'bit_identical_to_sequential':bool(r.score==direct['score']),'saved_score_delta':float(direct['score']-meta['score']),
         'saved_score_ulp_delta':float((direct['score']-meta['score'])/math.ulp(meta['score']))}
    meta=json.loads(path.read_text());meta['same_host_crosscheck']=row
    b=json.loads((HERE/'v10_reference.json').read_text())
    meta['winner_confirmed']=bool(r.passed and row['bit_identical_to_sequential'] and meta['mean']<b['mean'] and meta['holdout']['mean']<b['holdout']['mean'])
    path.write_text(json.dumps(meta,indent=2)+'\n');print(label,json.dumps(row),flush=True)
    assert row['bit_identical_to_sequential'],row
