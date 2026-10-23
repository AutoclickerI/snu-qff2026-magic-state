"""Full-circuit official verification; never disables adjacency."""
import argparse
import hashlib
import math
import sys
import time
from common import *
import batch_score
import fast_check
import tprep

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('file'); ap.add_argument('--count',type=int,default=5); ap.add_argument('--start',type=int,default=0); ap.add_argument('--procs',type=int,default=8); ap.add_argument('--tag',default='official')
    ap.add_argument('--accept-roundoff',action='store_true',help='Lane-specific performance exception: keep strict result and require c1 <= machine epsilon plus empty harmful-instruction list.')
    args=ap.parse_args(); assert 1<=args.procs<=8
    original_path=Path(args.file).resolve(); rows=json.load(open(original_path)); results=[]
    path=HERE/(args.tag+'_schedules.json'); save(path,rows)
    for idx in range(args.start,min(len(rows),args.start+args.count)):
        a,o=decode(rows[idx]); proxy=g2.Model(EXTRAS).cost(a,o)
        assert proxy is not None
        c,data=batch_score.make(dict(kind='gen2',file=str(path),idx=idx,lazy=True)); text=c.text()
        (HERE/f'{args.tag}_{idx}.qasm').write_text(text)
        start=time.time(); rep=fast_check.check(text,data,shots=10**8,seed=0,procs=args.procs)
        r=dict(file=path.name,idx=idx,proxy=proxy,passed=rep.passed,score=rep.score,sem=rep.sem,acceptance=rep.acceptance,n_2q=rep.n_2q,shots=10**8,seed=0,check_seconds=time.time()-start,qasm_sha256=hashlib.sha256(text.encode()).hexdigest(),data_qubits=data)
        print('check',r,flush=True)
        if rep.passed:
            start=time.time(); scan=tprep.fault_scan(text,data,processes=args.procs)
            r.update(c1=scan.c1,n_faults=scan.n_faults,scan_seconds=time.time()-start,scan=str(scan),by_instruction=scan.by_instruction)
            r['strict_verified']=bool(scan.c1==0)
            r['numerical_zero']=bool(math.isfinite(scan.c1) and abs(scan.c1)<=sys.float_info.epsilon and not scan.by_instruction)
            r['verified']=bool(r['strict_verified'] or (args.accept_roundoff and r['numerical_zero']))
            if args.accept_roundoff:
                r['verification_exception']='Lane-specific roundoff exception under user performance-priority instruction of 2026-10-23; literal c1 equality is separately reported.'
        else:
            r.update(verified=False,report=str(rep))
        results.append(r); save(args.tag+'.json',results); print('verified',r,flush=True)
    assert all(r['passed'] and r.get('verified') for r in results), 'verification failed; see saved evidence'

if __name__=='__main__': main()
