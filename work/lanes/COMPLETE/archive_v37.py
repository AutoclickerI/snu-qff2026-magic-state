import os,sys,json,random,hashlib,io,contextlib
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
sys.dont_write_bytecode=True
import v37
H=v37.H
sys.path.insert(0,str(H.parent/'BUNDLE'));from ev import sw,EVH
def run():
    seen=set();rows=[];attempts=[]
    families=[('root9',lambda:v37.rooted(9),0),('root7',lambda:v37.rooted(7),1),('root14',lambda:v37.rooted(14),1),('bell',lambda:v37.blue_bell(),0),('early',lambda:v37.early_bell(),-1)]
    for seed in range(20):
        for fam,builder,shift in families:
            if len(rows)>=30:break
            rng=random.Random(19000+seed);weights={b:rng.choice([-3,-1,0,1,3]) for b in sorted(v37.RELEASE)}
            name=f'v37_arch_{fam}_{seed:02}';st,info=v37.schedule(builder(),name,shift,seed=seed,seconds=3,weights=weights)
            if st is None:attempts.append(dict(name=name,**info));continue
            sig=tuple((r['bit'],r['cell'],r['release']) for r in info['release_profile'])
            if sig in seen:continue
            try:
                with contextlib.redirect_stdout(io.StringIO()):sw.prepare(st,True)
            except Exception as e:attempts.append(dict(name=name,error=repr(e)));continue
            seen.add(sig);rows.append(dict(id=f'v{len(rows):02}',stem=st.name,family=fam,sha256=info['sha256'],release_profile=info['release_profile'],ideal=True,round_shift=shift,weights=weights))
            print('archive',len(rows),st.name,flush=True)
        if len(rows)>=30:break
    out=dict(base='v37a',evaluator_hash=EVH,profiles=rows,rejected_or_unsolved=attempts,selection='Release-vector diversity before loss; no suffix-score filtering')
    (H/'archive_v37.json').write_text(json.dumps(out,indent=2)+'\n')
    assert len(rows)>=20,len(rows)
if __name__=='__main__':run()
