import os, sys, json, time, contextlib, io, hashlib, types
from pathlib import Path
sys.dont_write_bytecode = True
root=Path(__file__).resolve().parents[3]
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'): os.environ[k]='1'
folder=root/'work/lanes/MAIN/sparse'
audit=json.loads((Path(__file__).parent/'source_audit.json').read_text())['files']
lane=sys.argv[1].split('/')[0]
for name, hashes in audit.items():
 assert hashlib.sha256((folder/name).read_bytes()).hexdigest()==hashes['MAIN_sha256'], (lane,name,'source drift')
sys.path.insert(0,str(folder))
if lane == 'MAIN':
 import sparse_walsh as sw
else:
 # Reconstruct the audited MERGE diff in memory: remote lane copies can be stale.
 source=(folder/'sparse_walsh.py').read_text()
 old="""    ops, cost = min((search_basis(m, eng, groups, nd, set(kernel_scope), w, trials=0) for w in warms),
                    key=lambda r: r[1])
    if min(cost, (elim['work_entries'], elim['width']))[1] > SEARCH_WIDTH:
        ops = min((search_basis(m, eng, groups, nd, set(kernel_scope), w) for w in warms), key=lambda r: r[1])[0]
"""
 new="""    (ops, cost), best_warm = min(((search_basis(m, eng, groups, nd, set(kernel_scope), w, trials=0), w) for w in warms),
                               key=lambda r: r[0][1])
    if min(cost, (elim['work_entries'], elim['width']))[1] > SEARCH_WIDTH:
        # Refinement changes contraction coordinates only. Refine the cheapest
        # replay once; retraining every saved basis repeated the same costly
        # hill-climb for each neighbouring circuit.
        ops = search_basis(m, eng, groups, nd, set(kernel_scope), best_warm)[0]
"""
 assert source.count(old)==1
 source=source.replace(old,new)
 assert hashlib.sha256(source.encode()).hexdigest()==audit['sparse_walsh.py']['MERGE_sha256']
 sw=types.ModuleType('sparse_walsh'); sw.__file__=str(folder/'sparse_walsh.py')
 sys.modules[sw.__name__]=sw
 exec(compile(source,sw.__file__,'exec'),sw.__dict__)
if len(sys.argv)>3: sw.SEARCH_WIDTH=int(sys.argv[3])
if len(sys.argv)>4: sw.WARM=Path(sys.argv[4])
t=time.perf_counter()
with contextlib.redirect_stdout(io.StringIO()):
 m,e,g,nd,ks,psi,where,de=sw.prepare(Path(sys.argv[2]), True)
 prepared=time.perf_counter()-t
 compiled,elim=sw.compile_best(m,e,g,nd,ks)
 planned=time.perf_counter()-t
 sw._CTX.update(eng=e,ks=ks,psi=psi,where=where,compiled=compiled,elim=elim)
 rows=[sw._row(k) for k in [None]+e.keys]
A=rows[0]['value']; obs=sum(w*b*r['value'] for w,b,r in zip(e.W,e.beta,rows[1:]))
print(json.dumps(dict(source=sys.argv[1],stem=sys.argv[2],loss=(A-obs)/(2*A),acceptance=A,width=elim['width'],prepare_seconds=prepared,compile_seconds=planned-prepared,seconds=time.perf_counter()-t)),flush=True)
