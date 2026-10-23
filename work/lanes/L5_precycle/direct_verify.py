"""Independent sequential tprep.check, official shots and seed, against fast_check receipt."""
from search_v10 import *
for label in sys.argv[1:]:
    p=HERE/(label+'.json');meta=json.loads(p.read_text());qasm=(HERE/(label+'.qasm')).read_text()
    start=time.monotonic();r=tprep.check(qasm,meta['data_qubits'],shots=10**8,seed=0)
    row={'passed':bool(r.passed),'score':float(r.score),'seed':0,'shots':10**8,'seconds':time.monotonic()-start,'report':str(r),'bit_identical_to_fast_check':bool(r.score==meta['score']),
         'gates':{'format':bool(r.format_ok),'class':bool(r.class_ok),'correctness':bool(r.correct_ok),'acceptance':bool(r.acceptance_ok)}}
    parallel=fast_check.check(qasm,meta['data_qubits'],shots=10**8,seed=0,procs=3)
    row['same_host_parallel_score']=parallel.score
    row['bit_identical_same_host']=bool(parallel.score==r.score)
    row['saved_score_delta']=float(r.score-meta['score'])
    meta=json.loads(p.read_text())
    meta['direct_tprep']=row
    b=json.loads((HERE/'v10_reference.json').read_text())
    meta['winner_confirmed']=bool(r.passed and row['bit_identical_same_host'] and meta['mean']<b['mean'] and meta.get('holdout',{}).get('mean',1)<b['holdout']['mean'])
    p.write_text(json.dumps(meta,indent=2)+'\n');(HERE/(label+'_tprep.txt')).write_text(str(r)+'\n'+json.dumps(row)+'\n')
    print(label,json.dumps(row),flush=True)
    if not r.passed or not row['bit_identical_same_host']:raise RuntimeError('sequential verification mismatch')
