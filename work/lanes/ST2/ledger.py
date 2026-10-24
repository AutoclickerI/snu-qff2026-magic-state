"""Disjoint physical-lifetime noise masks; unchanged exact2 and sparse Walsh.

Masks change probabilities only. No operations, frames or accepted outcomes
are removed. Full-gap probabilities use the judge's exact composed idle map.
"""
import os,sys,json,re,math,contextlib,io,time,collections,itertools,runpy
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
sys.dont_write_bytecode=True
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
os.environ['XTIM_TWIRL_CACHE_DIR']=str(H/'.xtim_cache')
sys.path[:0]=[str(ROOT/'work/lanes/EVAL'),str(ROOT/'work/lanes/BCPOL'),str(H)]
import exact2,model,moments_batch as mom
import xtim
xtim.cache_dir=str(H/'.xtim_cache')
REGIONS=['prefix_ops','prefix_idles','data_wait','BC','A','round']
A_START={1:42,2:42,8:41,9:40,14:41,15:41,16:44}
BC_START={6:45,26:36,13:37,11:37,4:40,23:36,27:36,12:41,25:37,19:37,17:36,5:39,29:36,28:36}
DATA={0,20,7,10,3,22,21};R=48
# Last prefix/transfer CX on each output wire; Tdag can slide through its wait.
WAIT_START={0:40,20:40,7:39,10:39,3:33,22:44,21:40}
STEM=H/'ledger_v30g'
def region(qs,t,idle=False):
    if t>=R:return 'round'
    if idle and len(qs)==1 and qs[0] in WAIT_START and t>=WAIT_START[qs[0]]:return 'data_wait'
    if all(q in BC_START and t>=BC_START[q] for q in qs):return 'BC'
    if all(q in A_START and t>=A_START[q] for q in qs):return 'A'
    return 'prefix_idles' if idle else 'prefix_ops'

def mask_noise(original,schedule,keep,omit_zero=False):
    def masked(text,p,*args,**kw):
        prog,blocks=original(text,p,*args,**kw);_,steps,gaps=schedule(text)
        idle=collections.defaultdict(list)
        for i,q,first,n in gaps:idle[i].append((q,first,n))
        for i,(ins,block) in enumerate(zip(prog,blocks)):
            t=min((s for _,s in steps[i]),default=0);nidle=len(idle[i]);start=len(block)-nidle
            for j,line in enumerate(block):
                if '(' not in line or not line.startswith(('DEPOLARIZE','X_ERROR','Z_ERROR')):continue
                if j>=start and nidle:
                    q,first,n=idle[i][j-start]
                    count=sum(region([q],tt,True) in keep for tt in range(first,first+n))
                    value=.75*(1-(1-4*p/3)**count)
                    block[j]=re.sub(r'\([^)]*\)',f'({value})',line,count=1)
                elif region(ins.qubits,t) not in keep:
                    block[j]=re.sub(r'\([^)]*\)','(0)',line,count=1)
                if omit_zero and re.search(r'\(0(?:\.0+)?\)',block[j]):
                    # Keep the block slot (and its gap provenance) but omit a
                    # zero-probability channel from fault enumeration.
                    block[j]='# ledger: zero-probability noise channel'
        return prog,blocks
    return masked

def keep_for(label):
    if label=='all':return set(REGIONS)
    mode,reg=label.split(':',1)
    return {reg} if mode=='only' else set(REGIONS)-{reg}

def cubic(text,keep):
    old=model.noise_blocks
    model.noise_blocks=mask_noise(old,model.schedule,keep)
    try:
        ev=exact2.Eval(text,list(DATA_ORDER));r=mom.evaluate(ev)
    finally:model.noise_blocks=old
    return r,ev

DATA_ORDER=[0,20,7,10,3,22,21]
def cli(label,procs=1,pruned=False):
    # Built and validated once by main(); never concurrently rewrite the input.
    stem=STEM.with_name(STEM.name+'_detorder')
    assert stem.with_suffix('.qasm').exists()
    old=model.noise_blocks;model.noise_blocks=mask_noise(old,model.schedule,keep_for(label),omit_zero=True)
    sys.argv=[str(ROOT/'work/lanes/EVAL/exact2.py'),str(stem.with_suffix('.qasm')),'--third','--procs',str(procs),'--top','0']
    try:
        if pruned:
            import importlib.util
            spec=importlib.util.spec_from_file_location('ledger_pruned',H/'fast_third.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
            exact2.third_order=mod.third_order
            exact2.main()
        else:runpy.run_path(sys.argv[0],run_name='__main__')
    finally:model.noise_blocks=old

def sparse(label):
    sys.path.insert(0,str(H/'sparse'))
    import sparse_walsh as sw
    outdir=H/'sparse'/label.replace(':','_');outdir.mkdir(exist_ok=True)
    sw.__file__=str(outdir/'sparse_walsh.py')
    keep=keep_for(label);old=sw.fa.noise_blocks
    sw.fa.noise_blocks=mask_noise(old,sw.fa.schedule,keep)
    try:
        with contextlib.redirect_stdout(io.StringIO()):r=sw.run(STEM,72,True,procs=1)
    finally:sw.fa.noise_blocks=old
    r.pop('results');r['label']=label
    (H/('ledger_'+label.replace(':','_')+'.sparse.json')).write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps(r),flush=True)

def main():
    text=STEM.with_suffix('.qasm').read_text()
    from canonical_detectors import canonical
    canonical_stem,proof=canonical(STEM)
    text=canonical_stem.with_suffix('.qasm').read_text()
    rows={};ev=None
    for label in ['all']+[f'{mode}:{r}' for mode in ['no','only'] for r in REGIONS]:
        r,e=cubic(text,keep_for(label));rows[label]=r
        if label=='all':ev=e
        print(label,json.dumps(r),flush=True)
    # Multilinear presence/absence interactions through third order, including
    # signed conditional-normalization terms. They sum to the full cubic loss.
    subsets={0:dict(second=0.,third=0.,total=0.)}
    for mask in range(1,1<<len(REGIONS)):
        ks={r for i,r in enumerate(REGIONS) if mask>>i&1}
        known=next((x for x in rows if keep_for(x)==ks),None)
        subsets[mask]=rows[known] if known else cubic(text,ks)[0]
    components=[]
    for mask in range(1,1<<len(REGIONS)):
        vals={key:sum((-1)**(mask.bit_count()-sub.bit_count())*subsets[sub][key]
                     for sub in range(mask+1) if sub&mask==sub) for key in ['second','third','total']}
        if abs(vals['total'])>1e-15:components.append(dict(regions=[r for i,r in enumerate(REGIONS) if mask>>i&1],**vals))
    components.sort(key=lambda r:r['total'],reverse=True)
    # The unchanged exact2 pair kernel, pruning only impossible detector parity.
    import core as C
    sy=C.setup_syndromes(ev);pairs=[(a,b) for a in range(len(sy)) for b in range(a,len(sy)) if sy[a]==sy[b]]
    exact2.G.update(ev=ev,pairs=pairs,third=False)
    p2,_,_,big,_=exact2._pair_chunk((0,len(pairs),0))
    classes=collections.Counter();examples={};ownership=[]
    for cid,ch in enumerate(ev.m.chans):
        lab=ev.chan_label(cid)
        if ch['gap']:
            q,first,n=ch['gap'];parts=collections.Counter(region([q],tt,True) for tt in range(first,first+n))
            assert len(parts)==1,('gap crosses ownership boundary',cid,parts)
            reg=next(iter(parts))
        else:reg=region(lab['qubits'],int(lab['steps']))
        ownership.append(reg)
    for value,i,j,*_ in big:
        regs=tuple(sorted([ownership[int(ev.fch[i])],ownership[int(ev.fch[j])]]));classes[regs]+=value
        if value>examples.get(regs,[0])[0]:examples[regs]=[value,ev.fault_label(i),ev.fault_label(j)]
    pairs_out=[dict(regions=list(k),value=v,example=examples[k]) for k,v in classes.most_common()]
    out=dict(rows=rows,components=components,pair_classes=pairs_out,second_pair_sum=p2,
             channel_ownership=dict(collections.Counter(ownership)),A_START=A_START,BC_START=BC_START,WAIT_START=WAIT_START,R=R,
             note='Presence/absence components include all within-region quadratic/cubic terms and signed conditional denominator terms; no-region deltas overlap and are not additive.')
    (H/'ledger_cubic.json').write_text(json.dumps(out,indent=2)+'\n')
    print('LEDGER',json.dumps(out),flush=True)

if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]=='cli':cli(sys.argv[2],int(sys.argv[3]) if len(sys.argv)>3 else 1)
    elif len(sys.argv)>1 and sys.argv[1]=='enumerate':cli(sys.argv[2],int(sys.argv[3]) if len(sys.argv)>3 else 1,True)
    elif len(sys.argv)>1 and sys.argv[1]=='sparse':sparse(sys.argv[2])
    else:main()
