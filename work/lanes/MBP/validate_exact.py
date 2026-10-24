"""Compare MB detector-frame triples with unchanged exact2.third_order."""
from mbp import *
import fast_third
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stem');p.add_argument('--procs',type=int,default=7);a=p.parse_args()
    stem=OUT/a.stem;meta=json.loads(stem.with_suffix('.json').read_text());text=stem.with_suffix('.qasm').read_text()
    if meta.get('grid_free'):relax(meta['n_qubits'])
    else:physical()
    nd=stim_verify(text,meta['n_qubits']);ch=check(text,meta['data_qubits'],meta['n_qubits']);assert ch['correct'],ch
    ev=exact2.Eval(text,meta['data_qubits']);r=exact2.run(ev,a.procs,third=True);assert abs(r['loss1'])<1e-12
    fast=fast_third.third_order(ev,a.procs)[0];print('fast third raw',fast,flush=True)
    start=time.time();slow=fast_third.SLOW_THIRD(ev,a.procs)[0];elapsed=time.time()-start
    assert abs(fast-slow)<1e-14,(fast,slow)
    out=dict(stem=a.stem,stim_detectors=nd,check=ch,c1=r['loss1'],second=r['loss2'],fast_raw=fast,unchanged_exact2_raw=slow,absolute_error=abs(fast-slow),third=slow+r['t3bc'],total=r['loss']+slow+r['t3bc'],slow_seconds=elapsed)
    (OUT/'exact_validation.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out),flush=True)
