from common import *
sys.path.insert(0,str(ROOT/'work'))
import fast_check,tprep
name=sys.argv[1];procs=int(sys.argv[2]);p=HERE/name
text=p.with_suffix('.qasm').read_text();data=json.loads(p.with_suffix('.json').read_text())['data_qubits']
r=tprep.check(text,data,shots=10**6,seed=0);p.with_suffix('.check.log').write_text(str(r)+'\n')
out=dict(check_passed=r.passed,check_acceptance=r.acceptance,seeds=[]);print(str(r),flush=True)
for seed in (0,1000,2000):
 r=fast_check.check(text,data,shots=10**8,seed=seed,procs=procs)
 out['seeds'].append(dict(seed=seed,score=r.score,acceptance=r.acceptance,sem=r.sem,passed=r.passed))
 out['mean']=sum(x['score'] for x in out['seeds'])/len(out['seeds']);p.with_suffix('.mc.json').write_text(json.dumps(out,indent=1));print(out['seeds'][-1],flush=True)
print('mean',out['mean'],flush=True)
