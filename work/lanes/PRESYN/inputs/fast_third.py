"""Exact2 third-order evaluator with algebraically impossible triples pruned.

A projector whose action on the occupied orbit is a scalar is unaffected by
any rotation-sign pattern. Its detector flip must therefore be zero. Indexing
fault groups by these bits avoids evaluating triples with zero acceptance.
The surviving triples use exact2's unchanged arithmetic and channel masks.
"""
import os,sys,inspect,numpy as np,time,json,argparse
from pathlib import Path
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'work/lanes/EVAL'))
import exact2
from model import Basis
SLOW_THIRD=exact2.third_order
SLOW_CHUNK=exact2._triple_chunk

def live_cs(ga,gb):
    key=exact2.G['group_syndromes'][ga]^exact2.G['group_syndromes'][gb]
    cs=exact2.G['scalar_groups'].get(key,np.empty(0,dtype=int))
    return cs[cs>=gb]

source=inspect.getsource(SLOW_CHUNK)
old='cs = np.arange(gb, len(ev.gkeys))'
assert source.count(old)==1
source=source.replace(old,'cs = _trep2_live_cs(ga, gb)\n        if len(cs) == 0:\n            continue')
ns=dict(exact2.__dict__,_trep2_live_cs=live_cs)
exec(compile(source,str(OUT/'fast_third.py')+':filtered_chunk','exec'),ns)
FAST_CHUNK=ns['_triple_chunk']

def third_order(ev,procs):
    mask=sum(1<<i for i,(x,z,c)in enumerate(ev.e.projs)if x==0 and z==0)
    basis=Basis();indices=[];constraints=[]
    for i,(x,z,c)in enumerate(ev.e.projs):
        vector=x|(z<<ev.e.r);combo=basis.express(vector)
        if combo is None:basis.add(vector);indices.append(i)
        else:
            relation=1<<i
            for j,bi in enumerate(indices):
                if combo>>j&1:relation^=1<<bi
            constraints.append(relation)
    def syndrome(d):return sum(((d&h).bit_count()%2)<<j for j,h in enumerate(constraints))
    groups={}
    syndromes=[syndrome(d)for s,d in ev.gkeys]
    for i,sy in enumerate(syndromes):groups.setdefault(sy,[]).append(i)
    exact2.G['group_syndromes']=syndromes
    exact2.G['dependent_detector_constraints']=constraints
    exact2.G['scalar_mask']=mask;exact2.G['scalar_groups']={k:np.array(v,dtype=int)for k,v in groups.items()}
    exact2._triple_chunk=FAST_CHUNK
    try:return SLOW_THIRD(ev,procs)
    finally:exact2._triple_chunk=SLOW_CHUNK

if __name__=='__main__':
    if '--validate' in sys.argv:
        ap=argparse.ArgumentParser();ap.add_argument('stem');ap.add_argument('--validate',action='store_true');ap.add_argument('--procs',type=int,default=4);a=ap.parse_args()
        stem=OUT/a.stem;ev=exact2.Eval(stem.with_suffix('.qasm').read_text(),json.loads(stem.with_suffix('.json').read_text())['data_qubits'])
        t=time.time();fast=third_order(ev,a.procs)[0];fasttime=time.time()-t;print('fast',fast,fasttime,flush=True)
        t=time.time();slow=SLOW_THIRD(ev,a.procs)[0];slowtime=time.time()-t
        row=dict(fast=fast,slow=slow,absolute_error=abs(fast-slow),fast_seconds=fasttime,slow_seconds=slowtime,scalar_detector_bits=exact2.G['scalar_mask'].bit_count())
        assert abs(fast-slow)<1e-14,row
        (OUT/(a.stem+'.third_validation.json')).write_text(json.dumps(row,indent=2)+'\n');print(json.dumps(row),flush=True)
    else:
        exact2.third_order=third_order
        exact2.main()
