"""Fully noisy abstract shared-basis logical-W preparation with small cats.

Every gate, reset, measurement, and elapsed-time channel remains noisy.
The abstract coordinate assignment is NOT a legal grid submission. The official
ideal-state oracle is used separately from adjacency, and native embedding is
an independent requirement.
"""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='1'
import argparse,contextlib,hashlib,io,json,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
for lane in ('END2_20261027','REBUILD20261027','PREFIX2_20261027'):
    sys.path.insert(0,str(ROOT/'work/lanes'/lane))
sys.path.insert(0,str(ROOT/'work/tools'))
from qtools.evaluator import frontend as f,sparse_walsh as sw
from qtools.version import EVALUATOR_VERSION
from joint import emit
from partial_square import ENC,PIV,prep,ideal_contract_check
import record_contract,pairs

D=list(range(7));A=list(range(7,14));B=list(range(14,21));C=list(range(21,28))
GROUPS={1:[[0,1,3,5,2,4,6]],2:[[0,1,3],[2,4,5,6]],3:[[0,1,3],[2,4],[5,6]],
        4:[[0,1],[2,3],[4,5],[6]],5:[[0,1],[2,3],[4],[5],[6]],
        6:[[0,1],[2],[3],[4],[5],[6]],7:[[i]for i in range(7)]}


def tree(n):
    result=[];known=[0];next_index=1
    while next_index<n:
        layer=[]
        for control in known[:]:
            if next_index==n:break
            layer.append((control,next_index));next_index+=1
        result.append(layer);known+= [b for a,b in layer]
    return result


def build(ncat=3,herald=False,groups=None,reverse_second=False,name=None,staggered=False,late_bc=False,interleaved=False,second_groups=None,round_groups=None,coupling_layers=None,tail_delay=0,first_coupling=11,prechecks=True):
    groups=groups or GROUPS[ncat]
    assert sorted(i for g in groups for i in g)==list(range(7)) and len(groups)==ncat
    if second_groups is not None:
        assert sorted(i for g in second_groups for i in g)==list(range(7)) and len(second_groups)==ncat
    rounds=round_groups or [groups,second_groups or groups]
    for gs in rounds:assert len(gs)==ncat and sorted(i for g in gs for i in g)==list(range(7))
    reps=len(rounds)
    assert reps==2 or ncat*reps<=8
    ops=[]
    for i,q in enumerate(D):ops.append(f.Op('RX'if i in PIV|{2}else'R',(q,),0))
    ops += [f.Op('T',(D[2],),1),f.Op('CX',(D[2],D[4]),2),f.Op('CX',(D[2],D[5]),3)]
    for k,layer in enumerate(ENC):ops += [f.Op('CX',(D[a],D[b]),4+k)for a,b in layer]
    # Both physical prechecks are real noisy circuits, with resources prepared
    # just before their own data interaction. Their measurements are preserved.
    if prechecks is True or prechecks=='A':
        prep(ops,A,3,True)
        ops += [f.Op('CX',(d,a),7)for d,a in zip(D,A)]
        ops += [f.Op('M',(a,),8,i)for i,a in enumerate(A)]
    if prechecks is True or prechecks=='B':
        bt=8 if prechecks is True else 7
        prep(ops,B,bt-4,False)
        ops += [f.Op('CX',(b,d),bt)for b,d in zip(B,D)]
        ops += [f.Op('MX',(b,),bt+1,7+i)for i,b in enumerate(B)]
    width=max(map(len,groups+(second_groups or [])));first=first_coupling;second=first+width;end=second+width
    if interleaved:
        width=max(2,width);second=first;end=first+width
    if coupling_layers is not None:
        assert interleaved
        width=len(coupling_layers);second=first;end=first+width
    # Seven-cat control fits 36 physical wires by borrowing the final C block
    # before its preparation. Smaller controls use the unused cells only.
    cats=[C[:ncat],list(range(28,28+ncat))] if ncat>=5 else [list(range(28+r*ncat,28+(r+1)*ncat))for r in range(reps)]
    layers=tree(ncat)
    interactions=[];cat_reads=[]
    for rep,(cat,begin)in enumerate(zip(cats,[first]+[second]*(reps-1))):
        start=begin-len(layers)-1
        ops += [f.Op('RX'if i==0 else'R',(q,),start)for i,q in enumerate(cat)]
        for j,layer in enumerate(layers,1):ops += [f.Op('CX',(cat[a],cat[b]),start+j)for a,b in layer]
        chosen=rounds[rep]
        chosen=[list(reversed(g))for g in chosen] if rep and reverse_second else chosen
        if rep and interleaved and second_groups is None and round_groups is None:chosen=[g[1:]+g[:1] for g in chosen]
        if coupling_layers is None:
            for j in range(width):
                for q,group in zip(cat,chosen):
                    if j>=len(group):continue
                    tick=begin+j+int(bool(interleaved and rep and len(group)==1))
                    interactions.append(dict(round=rep,control=q,data=group[j],time=tick))
                    ops.append(f.Op('CX',(q,D[group[j]]),tick))
        else:
            for j,layer in enumerate(coupling_layers):
                for r,ci,di in layer:
                    if r!=rep:continue
                    assert di in chosen[ci]
                    interactions.append(dict(round=rep,control=cat[ci],data=di,time=begin+j))
                    ops.append(f.Op('CX',(cat[ci],D[di]),begin+j))
            assert sorted(o['data']for o in interactions if o['round']==rep)==list(range(7))
        read=max(o['time'] for o in interactions if o['round']==rep)+1
        cat_reads.append(read)
        ops += [f.Op('MX',(q,),read,14+rep*ncat+i)for i,q in enumerate(cat)]
    ops += [f.Op('T',(d,),first-1)for d in D]
    terminal=end+1
    if ncat>=5:terminal=max(terminal,cat_reads[0]+5)
    terminal+=tail_delay
    early={0,1} if herald and staggered else set()
    for i,d in enumerate(D):
        tick=end
        if i in early and terminal-1==end:
            last=max(o['time']for o in interactions if o['data']==i)
            # Z-diagonal TDG commutes through this data-control CX into A.
            # If the earlier slot is busy, put TDG after that early tap.
            tick=end-1 if last<end-1 else end+1
        ops.append(f.Op('TDG',(d,),tick))
    # Standard encoded resources, with actual C verification of B. They are
    # intentionally simple controls, not assumed to be the optimal tail.
    bc=terminal+int(herald and late_bc and not staggered)
    prep(ops,A,terminal-4-int(bool(early)),True);prep(ops,B,bc-4,False);prep(ops,C,bc-4,False)
    ops += [f.Op('CX',(d,a),terminal-int(i in early))for i,(d,a)in enumerate(zip(D,A))]
    ops += [f.Op('CX',(b,c),bc)for b,c in zip(B,C)]
    ops += [f.Op('M',(c,),bc+1,100+i)for i,c in enumerate(C)]
    if herald:
        shift=int(staggered)
        ops += [f.Op('CX',(A[1],A[0]),terminal+1-shift),f.Op('CX',(A[2],A[1]),terminal+2-shift)]
        final=terminal+3-shift;bd=terminal+2-shift
        ops += [f.Op('MX'if i==2 else'M',(a,),final,107+i)for i,a in enumerate(A)]
    else:
        final=terminal+2;bd=terminal+1
        ops += [f.Op('M',(a,),terminal+1,107+i)for i,a in enumerate(A)]
    ops += [f.Op('CX',(b,d),bd)for b,d in zip(B,D)]
    ops += [f.Op('MX',(b,),final,114+i)for i,b in enumerate(B)]
    ops.sort(key=lambda o:o.time)
    occupied={}
    for i,o in enumerate(ops):
        for q in o.qs:
            assert (o.time,q)not in occupied,(o,occupied.get((o.time,q)))
            occupied[o.time,q]=o
    f.DATA=D
    m=f.make_model(ops,[]);contract=record_contract.complete(m,[])
    assert not any(r['reference']for r in contract['missing']),contract
    dets=[set(r['bits'])for r in contract['missing']]
    text=emit(ops,dets)
    raw=ideal_contract_check(text,D)
    name=name or f'cat{ncat}_herald{int(herald)}_reverse{int(reverse_second)}'+('_stagger'if staggered else'')+('_latebc'if late_bc else'')+('_interleaved'if interleaved else'')+('_nonline'if ncat==2 else'')
    stem=HERE/'cand'/name;stem.parent.mkdir(exist_ok=True)
    stem.with_suffix('.qasm').write_text(text)
    meta=dict(data_qubits=D,roles=dict(D=D,A=A,B=B,C=C,cats=cats),cat_groups=groups,
        cat_n=ncat,cat_first=first,cat_second=second,cat_second_reversed=reverse_second,second_groups=second_groups,
        interleaved=interleaved,cat_reads=cat_reads,cat_interactions=interactions,round_groups=rounds,cat_rounds=reps,early_prechecks=prechecks,
        tail_start=terminal,A_logical_X_herald=herald,A_staggered=staggered,B_check_time=bc,
        cx=sum(o.kind=='CX'for o in ops),ticks=max(o.time for o in ops)+1,T=sum(o.kind in('T','TDG')for o in ops),
        raw=raw,record_contract=contract,qasm_sha256=hashlib.sha256(text.encode()).hexdigest(),
        diagnostic_only=True,grid_valid=False,
        scope='Complete abstract circuit with every real gate, reset, read and waiting channel noisy; adjacency is not claimed. No channel is idealized.',
        evaluator_version=EVALUATOR_VERSION)
    stem.with_suffix('.json').write_text(json.dumps(meta,indent=2)+'\n')
    return stem,meta


def exact(stem):
    started=time.perf_counter()
    m,eng,groups,nd,ks,psi,where,initial=sw.prepare(stem,True)
    compiled,elim=sw.compile_best(m,eng,groups,nd,ks,save=False)
    sw._CTX.update(eng=eng,ks=ks,psi=psi,where=where,compiled=compiled,elim=elim)
    try:
        vals=[sw._row(k)for k in [None]+eng.keys]
        acceptance=vals[0]['value']
        obs=sum(w*b*v['value']for w,b,v in zip(eng.W,eng.beta,vals[1:]))
        da=vals[0]['absolute_kernel_omission_bound']
        do=sum(abs(w*b)*v['absolute_kernel_omission_bound']for w,b,v in zip(eng.W,eng.beta,vals[1:]))
        result=dict(loss=(acceptance-obs)/(2*acceptance),acceptance=acceptance,
            observable=obs,acceptance_kernel_omission_bound=da,observable_kernel_omission_bound=do,
            loss_kernel_omission_interval=[(1-(obs+do)/(acceptance-da))/2,(1-(obs-do)/(acceptance+da))/2],
            bound_scope='Analytic sparse-kernel omission only; not a floating-point roundoff certificate.',
            rows=vals,peak_bucket_elements=max(v['peak_bucket_elements']for v in vals),
            qasm_sha256=hashlib.sha256(stem.with_suffix('.qasm').read_bytes()).hexdigest(),
            seconds=time.perf_counter()-started,diagnostic_only=True,grid_valid=False,
            scope='All channels noisy; only adjacency requirement is relaxed.',evaluator_version=EVALUATOR_VERSION)
    finally:
        sw._CTX.clear();sw.COLUMNS.clear()
    stem.with_suffix('.exact.json').write_text(json.dumps(result,indent=2)+'\n')
    return result


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--cats',type=int,default=3);ap.add_argument('--herald',action='store_true')
    ap.add_argument('--reverse-second',action='store_true');ap.add_argument('--price',action='store_true');ap.add_argument('--no-pairs',action='store_true')
    ap.add_argument('--staggered',action='store_true');ap.add_argument('--late-bc',action='store_true')
    ap.add_argument('--interleaved',action='store_true')
    ap.add_argument('--groups');ap.add_argument('--second-groups');ap.add_argument('--name');args=ap.parse_args()
    started=time.perf_counter();groups=json.loads(args.groups)if args.groups else None
    stem,result=build(args.cats,args.herald,groups,args.reverse_second,args.name,args.staggered,args.late_bc,args.interleaved,json.loads(args.second_groups)if args.second_groups else None)
    print(json.dumps(dict(stem=str(stem),raw=result['raw'],cx=result['cx'],ticks=result['ticks'],T=result['T'])),flush=True)
    if result['raw']['ok']:
        ops,dets=f.parse_current(stem.with_suffix('.qasm').read_text());m=f.make_model(ops,dets)
        result['singles']=record_contract.singles(m)
        print(json.dumps(dict(c1=result['singles']['c1'],harmful=len(result['singles']['harmful_faults']),components=result['singles']['fault_components'])),flush=True)
        if not args.no_pairs:
            with contextlib.redirect_stdout(io.StringIO()):p=pairs.audit(stem)
            result['c2']=p['c2'];print(json.dumps(dict(c2=p['c2'])),flush=True)
        if args.price:result['exact']=exact(stem);print(json.dumps(result['exact']),flush=True)
    result['seconds']=time.perf_counter()-started
    stem.with_suffix('.result.json').write_text(json.dumps(result,indent=2)+'\n')


if __name__=='__main__':main()
