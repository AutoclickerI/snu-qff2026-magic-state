"""Small matched all-noisy controls, at most two single-thread workers."""
import concurrent.futures,contextlib,io,json,time
from pathlib import Path
import smallcat as s

JOBS=[
 dict(ncat=2,herald=False,interleaved=True),
 dict(ncat=2,herald=True,staggered=True,interleaved=True),
 dict(ncat=3,herald=True,late_bc=True),
 dict(ncat=4,herald=False,interleaved=True),
 dict(ncat=4,herald=True,staggered=True,interleaved=True),
 dict(ncat=5,herald=True,staggered=True,interleaved=True),
 dict(ncat=6,herald=True,staggered=True,interleaved=True),
 dict(ncat=7,herald=True,staggered=True,interleaved=True),
]

def run(args):
    st=time.perf_counter();stem,out=s.build(**args)
    if out['raw']['ok']:
        ops,dets=s.f.parse_current(stem.with_suffix('.qasm').read_text())
        s.f.DATA=out['data_qubits'];out['singles']=s.record_contract.singles(s.f.make_model(ops,dets))
        with contextlib.redirect_stdout(io.StringIO()):p=s.pairs.audit(stem)
        out['c2']=p['c2']
        if out['singles']['c1']<1e-10:out['exact']=s.exact(stem)
    out['seconds']=time.perf_counter()-st
    out['completed']=True
    stem.with_suffix('.result.json').write_text(json.dumps(out,indent=2)+'\n')
    return dict(name=stem.name,raw=out['raw']['ok'],c1=out.get('singles',{}).get('c1'),c2=out.get('c2'),
                loss=out.get('exact',{}).get('loss'),acceptance=out.get('exact',{}).get('acceptance'),cx=out['cx'],ticks=out['ticks'])

if __name__=='__main__':
    rows=[]
    with concurrent.futures.ProcessPoolExecutor(max_workers=2)as ex:
        for row in ex.map(run,JOBS):rows.append(row);print(json.dumps(row),flush=True)
    (s.HERE/'screen2.json').write_text(json.dumps(dict(process_completed=True,rows=rows),indent=2)+'\n')
