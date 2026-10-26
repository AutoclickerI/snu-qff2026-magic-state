#!/usr/bin/env python3
"""True-native-tick noise cuts; fixed QASM and all accepted-state semantics.

These are diagnostic counterfactuals, never proposed physical circuits.
The source evaluator is pinned at 1d56e6b; unchanged at bb98bed.
"""
import argparse, contextlib, copy, hashlib, io, json, math, os, sys, time
from pathlib import Path
for name in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[name]='1'
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]


def channel_metadata(m):
    prog,blocks=fa.noise_blocks(m.native,.001,first_order=False)
    _,steps,gaps=fa.schedule(m.native)
    gap={(i,q):(t,n) for i,q,t,n in gaps}
    meta=[]
    for cid,ch in enumerate(m.chans):
        i=ch['ins'];op=m.labels[i];k=blocks[i].index(prog[i].text)
        is_idle=ch['name']=='DEPOLARIZE1' and ch['jl']>=k+2
        assert len(steps[i])==1
        tick=steps[i][0][1]
        assert tick==op.time,(i,tick,op.time)
        if is_idle:
            start,n=gap[(i,ch['qs'][0])]
            assert abs(ch['p']-.75*(1-(1-4*.001/3)**n))<1e-13
            category='idle';end=start+n
        else:
            start=tick;end=tick+1;n=1
            if ch['jl']<k:
                category='readout_or_initial' if op.kind in ('M','MX') else 'initial'
            elif op.kind in ('R','RX'):category='reset'
            elif op.kind in ('M','MX'):category='measurement_backaction'
            elif op.kind=='CX':category='gate2'
            else:category='gate1'
        meta.append(dict(channel=cid,start=start,end=end,n=n,category=category,owner_tick=tick,owner_kind=op.kind,owner_qubits=list(op.qs),qubits=ch['qs'],p=ch['p']))
    return meta


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--repo',type=Path,default=ROOT/'source')
    ap.add_argument('--circuit',type=Path)
    ap.add_argument('--out-dir',type=Path)
    ap.add_argument('--cuts',default='0,47,46,45,44,40,36')
    ap.add_argument('--processes',type=int,default=4)
    a=ap.parse_args()
    assert a.processes>=1
    sys.path.insert(0,str(a.repo.resolve()/'work/lanes/MAIN/sparse'))
    global fa
    import frontend as fa
    import sparse_walsh as sw
    base=Path(__file__).resolve().parent
    stem=(a.circuit or base/'source/work/lanes/MAIN/v37g.qasm').resolve().with_suffix('')
    out=a.out_dir or base/'results';out.mkdir(parents=True,exist_ok=True)
    started=time.perf_counter()
    with contextlib.redirect_stdout(io.StringIO()):
        m,eng,groups,nd,ks,psi,where,dense=sw.prepare(stem,True)
    meta=channel_metadata(m)
    (out/'channel_metadata.json').write_text(json.dumps(meta,indent=2)+'\n')
    allrows=[]
    for cut in map(int,a.cuts.split(',')):
        begin=time.perf_counter();mm=copy.copy(m);mm.chans=[dict(c) for c in m.chans]
        kept={};removed=partial=0
        for cid,fs in groups.items():
            md=meta[cid];n=max(0,md['end']-max(md['start'],cut))
            if n==0:removed+=1;continue
            if n==md['n']:kept[cid]=fs;continue
            assert md['category']=='idle'
            partial+=1
            pnew=.75*(1-(1-4*.001/3)**n);scale=pnew/md['p']
            mm.chans[cid]['p']=pnew
            kept[cid]=[dict(f,p=f['p']*scale) for f in fs]
        with contextlib.redirect_stdout(io.StringIO()):
            compiled,elim=sw.compile_best(mm,eng,kept,nd,ks)
            sw._CTX.update(eng=eng,ks=ks,psi=psi,where=where,compiled=compiled,elim=elim)
            keys=[None]+eng.keys
            import multiprocessing as mp
            with mp.get_context('fork').Pool(a.processes) as pool:
                rows=list(pool.imap(sw._row,keys))
        A=rows[0]['value'];obs=sum(w*b*r['value'] for w,b,r in zip(eng.W,eng.beta,rows[1:]))
        ea=rows[0]['absolute_kernel_omission_bound']
        eo=sum(abs(w*b)*r['absolute_kernel_omission_bound'] for w,b,r in zip(eng.W,eng.beta,rows[1:]))
        bound=eo/(2*(A-ea))+abs(obs)*ea/(2*A*(A-ea))
        r=dict(name=f'noise_only_ticks_ge_{cut}',noise_start_tick=cut,loss=(A-obs)/(2*A),acceptance=A,
               unnormalized_loss_numerator=(A-obs)/2,fidelity_observable=obs,
               noisy_channels=len(kept),removed_channels=removed,partly_retained_idle_runs=partial,
               width=elim['width'],seconds=time.perf_counter()-begin,conditional_loss_kernel_omission_bound=bound,
               bound_scope='Sparse cutoff only, excludes floating-point roundoff',physical_candidate=False,
               qasm_sha256=hashlib.sha256(stem.with_suffix('.qasm').read_bytes()).hexdigest(),moments=rows)
        (out/f'cut_{cut:02d}.json').write_text(json.dumps(r,indent=2)+'\n')
        allrows.append({k:v for k,v in r.items() if k!='moments'})
        (out/'cut_summary.json').write_text(json.dumps(allrows,indent=2)+'\n')
        print(json.dumps(allrows[-1]),flush=True)
    print(json.dumps(dict(done=True,seconds=time.perf_counter()-started)),flush=True)

if __name__=='__main__':main()
