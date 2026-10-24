from pathlib import Path
import sys,json,time,resource,hashlib,multiprocessing as mp
import numpy as np
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'source/work/lanes/MAIN/sparse'))
import sparse_walsh as sw
stem=ROOT/'benchmark_input/v36c'
prep=time.perf_counter();m,e,g,nd,ks,psi,where,_=sw.prepare(stem,True)
original=sw.compile_channels(m,g,nd,ks)
certificate=json.loads((ROOT/'basis_width_probe.json').read_text())
U=[1<<i for i in range(nd)]
for i,j in certificate['elementary_row_xors']:
    assert i!=j and e.projs[i]==(0,0,1) and e.projs[j]==(0,0,1)
    U[i]^=U[j]
old=[f['d'] for f in m.faults]
for f in m.faults:
    d=f['d'];f['d']=sum(((d&row).bit_count()%2)<<i for i,row in enumerate(U))
optimized=sw.compile_channels(m,g,nd,ks)
assert all(f['d']==sum(((d&row).bit_count()%2)<<i for i,row in enumerate(U)) for f,d in zip(m.faults,old))
elim={mode:sw.minfill([set(s) for s,_,_ in c]) for mode,c in [('original',original),('optimized',optimized)]}
assert elim['optimized']['work_entries']==certificate['after']['work_entries']
keys=[None]+e.keys
sw._CTX.update(eng=e,ks=ks,psi=psi,where=where)
out={'qasm_sha256':hashlib.sha256(stem.with_suffix('.qasm').read_bytes()).hexdigest(),
     'channels':len(m.chans),'detectors':nd,'moments':len(keys),'processes':4,
     'prepare_and_transform_seconds':time.perf_counter()-prep,
     'order':'ABBA: original, optimized, optimized, original',
     'repeats':[],'basis_rank':None}
rankbasis={}
for row in U:
    while row:
        p=row.bit_length()-1
        if p not in rankbasis:rankbasis[p]=row;break
        row^=rankbasis[p]
out['basis_rank']=len(rankbasis);assert len(rankbasis)==nd
reference=None
for mode in ['original','optimized','optimized','original']:
    sw._CTX.update(compiled=original if mode=='original' else optimized,elim=elim[mode])
    before=resource.getrusage(resource.RUSAGE_CHILDREN);ts=time.perf_counter()
    with mp.get_context('fork').Pool(4) as pool:rows=list(pool.imap(sw._row,keys))
    elapsed=time.perf_counter()-ts;after=resource.getrusage(resource.RUSAGE_CHILDREN)
    vals=np.array([r['value'] for r in rows])
    if reference is None:reference=vals
    A=vals[0];O=sum(w*b*v for w,b,v in zip(e.W,e.beta,vals[1:]));loss=(A-O)/(2*A)
    rec={'mode':mode,'seconds':elapsed,'child_cpu_seconds':after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime,
         'acceptance':A,'loss':loss,'max_moment_difference':float(np.abs(vals-reference).max()),
         'max_peak_bucket_elements':max(r['peak_bucket_elements'] for r in rows),
         'conditioned_width':elim[mode]['width'],'work_entries':elim[mode]['work_entries'],
         'moments':rows}
    out['repeats'].append(rec)
    (ROOT/'basis_validate.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in rec.items() if k!='moments'}),flush=True)
for typ in ['seconds','child_cpu_seconds']:
    out[typ+'_ratio']=float(np.mean([r[typ] for r in out['repeats'] if r['mode']=='original'])/np.mean([r[typ] for r in out['repeats'] if r['mode']=='optimized']))
(ROOT/'basis_validate.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='repeats'}),flush=True)
