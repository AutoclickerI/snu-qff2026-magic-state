"""Calibrate and optimize complete DEM objectives for distinct order classes."""
import argparse
import time
import numpy as np
from common import *
from cpsat import Schedule, compact
from ordered_objective import OrderedObjective,SCALE
from global_search import order_key

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('files',nargs='*'); ap.add_argument('--tag',default='refined'); ap.add_argument('--lmax',type=int,default=9); ap.add_argument('--count',type=int,default=100); ap.add_argument('--seconds',type=float,default=15); ap.add_argument('--workers',type=int,default=8); ap.add_argument('--calibrate-only',action='store_true')
    args=ap.parse_args(); m=g2.Model(EXTRAS); samples=[]; seen=set()
    files=[Path(f) for f in args.files] if args.files else sorted(WORK.glob('gen2_t1c13+t2c42_*.json'))
    for f in files:
        for idx,r in enumerate(json.load(open(f))):
            a,o=decode(r); a=compact(a); key=order_key(a,o)
            if key in seen or max(a.values())>args.lmax: continue
            seen.add(key); proxy=m.cost(a,o)
            if proxy is not None: samples.append((proxy,a,o,f.name,idx))
    samples.sort(key=lambda r:r[0]); results=[]; runs=[]; calibration=[]
    for n,(p,a,o,source,idx) in enumerate(samples[:args.count]):
        start=time.time()
        try: obj=OrderedObjective(a,o)
        except Exception as ex:
            runs.append(dict(n=n,source=source,idx=idx,error=repr(ex))); save(args.tag+'_runs.json',runs); raise
        formula=obj.value(a)
        calibration.append(dict(source=source,idx=idx,proxy=p,formula=formula,difference=formula-p))
        assert abs(p-formula)<1e-12,(p,formula,source,idx)
        if not args.calibrate_only:
            sc=Schedule(args.lmax,(a,o),fixed_order=True); obj.install(sc); solver,status=sc.solve(args.seconds,args.workers,n)
            row=dict(n=n,source=source,idx=idx,input_proxy=p,status=solver.status_name(status),bound=solver.best_objective_bound/(2*SCALE**2),rounding_error_bound=obj.rounding_bound,seconds=time.time()-start)
            if status in (2,4):
                aa,oo=sc.extract(solver); measured=m.cost(aa,oo)
                assert measured is not None
                assert abs(measured-obj.value(aa))<1e-12
                row.update(proxy=measured,objective=solver.objective_value/(2*SCALE**2))
                results.append(encode(measured,aa,oo,f'{args.tag}:{n}')); results.sort(key=lambda r:r[0]); save(args.tag+'.json',results)
            runs.append(row); save(args.tag+'_runs.json',runs); print(row,flush=True)
        save(args.tag+'_calibration.json',calibration)
    if len(calibration)>1:
        aa=np.array([r['proxy'] for r in calibration]); bb=np.array([r['formula'] for r in calibration])
        corr=float(np.corrcoef(aa,bb)[0,1]); error=float(np.max(np.abs(aa-bb)))
        summary=dict(n=len(calibration),pearson=corr,max_abs_error=error,rmse=float(np.sqrt(np.mean((aa-bb)**2))))
        save(args.tag+'_calibration_summary.json',summary); print(summary,flush=True)

if __name__=='__main__': main()
