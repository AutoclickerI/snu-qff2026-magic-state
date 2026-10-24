"""Three official-sized draws; physical circuits use the unchanged judge.
Grid-free diagnostics retain their declared adjacency/helper-count relaxation.
"""
from mbp import *
sys.path.insert(0,str(ROOT/'work'))
import fast_check
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stems',nargs='+');p.add_argument('--procs',type=int,default=1);a=p.parse_args()
    for name in a.stems:
        assert os.getloadavg()[0]<os.cpu_count()
        stem=OUT/name;meta=json.loads(stem.with_suffix('.json').read_text());text=stem.with_suffix('.qasm').read_text();n=meta.get('n_qubits',36)
        if meta.get('grid_free'):relax(n)
        else:physical()
        nd=stim_verify(text,n);ch=check(text,meta['data_qubits'],n);print(name,'check',ch,flush=True)
        rows=[]
        for seed in [0,1000,2000]:
            r=fast_check.check(text,meta['data_qubits'],shots=10**8,seed=seed,procs=a.procs,n_qubits=n)
            row=dict(seed=seed,score=r.score,sem=r.sem,acceptance=r.acceptance,passed=r.passed);rows.append(row);print(name,json.dumps(row),flush=True)
        result=dict(stem=name,grid_free=meta.get('grid_free',False),stim_detectors=nd,check=ch,seeds=rows,mean=sum(x['score'] for x in rows)/3)
        stem.with_suffix('.mc.json').write_text(json.dumps(result,indent=2)+'\n');print(name,'mean',result['mean'],flush=True)
