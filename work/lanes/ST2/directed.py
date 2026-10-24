"""Ledger-directed native-window population; selection uses sparse all orders."""
import os,sys,json,math,random,re,hashlib,copy,time,lzma,contextlib,io,argparse
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
sys.dont_write_bytecode=True
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
sys.path.insert(0,str(H));import core as C
import importlib.util
spec=importlib.util.spec_from_file_location('directed_mom',H/'moments_batch.py');mom=importlib.util.module_from_spec(spec);spec.loader.exec_module(mom)
sys.path.insert(0,str(H/'sparse'));import sparse_walsh as sw
C.xtim.cache_dir=str(H/'.xtim_cache');os.environ['XTIM_TWIRL_CACHE_DIR']=str(H/'.xtim_cache')
from ortools.linear_solver import pywraplp
from ortools.sat.python import cp_model

def normalize(c):
    # Use the actual register size, retaining the native folding assertions.
    old=C.textof
    def emit(d):
        d['h']=[re.sub(r'creg c\[\d+\]',f'creg c[{max(256,C.bit(d))}]',s) for s in d['h']]
        return old(d)
    C.textof=emit
    try:return C.normalize(c)
    finally:C.textof=old

def digest(c):
    # Parallel operation order carries no physical diversity; collapse it.
    key=[sorted(s for u,t in zip(c['u'],c['t']) if t==tt for s in ['|'.join(u.lines)]) for tt in sorted(set(c['t']))]
    return hashlib.sha256(json.dumps([key,sorted(c['tail'])]).encode()).hexdigest()[:14]

def weighted_window(c,rng,family):
    """Whole-window LP over per-wire precedence with a fixed round.

    Mixed per-wire ASAP/ALAP, measured-cell release, and weighted idle segment
    lifetime objectives. Every solution preserves the full per-wire order.
    """
    c=C.clone(c);us=c['u'];old=c['t'];R=c['meta']['R'];n=len(us)
    if family=='prefix_mix':lo,hi=0,min(32,R-1)
    elif family=='release':lo,hi=24,R-1
    elif family=='A_wait':lo,hi=30,R-1
    else:lo,hi=rng.choice([(0,R-1),(12,R-1),(18,R-1),(26,R-1)])
    m=pywraplp.Solver.CreateSolver('GLOP');tv=[m.NumVar(0,max(old),f't{i}') for i in range(n)]
    pred,_=C.S.build_dag(us)
    for j,ps in enumerate(pred):
        for i in ps:m.Add(tv[j]>=tv[i]+1)
    for i,t in enumerate(old):
        if not lo<=t<=hi:m.Add(tv[i]==t)
        else:m.Add(tv[i]>=lo);m.Add(tv[i]<=hi)
    weights=[0.]*n;byq={q:[i for i,u in enumerate(us) if q in u.qs] for q in range(36)}
    target=rng.choice([0,7,10,20,3,22,21]);polarity={q:rng.choice([-1,1]) for q in range(36)}
    for q,seq in byq.items():
        for ia,ib in zip(seq,seq[1:]):
            if old[ia]>=R:continue
            # Integrates exposure of complete intervals, rather than choosing
            # single-gate proposals from an early prefix of an iterator.
            w=rng.uniform(.2,1.3)
            if q in C.D:w*=rng.choice([1.,2.,4.])
            if q==target:w*=6
            if q in C.A and old[ia]>=33:w*=3
            if us[ia].name in ('MX','MEASURE') and us[ib].name in ('RX','RESET'):w=0
            weights[ib]+=w;weights[ia]-=w
        for i in seq:
            if family=='prefix_mix':weights[i]+=polarity[q]*rng.uniform(.05,.6)
            if family=='release' and us[i].name in ('MX','MEASURE') and 26<=old[i]<R:weights[i]+=rng.uniform(2,8)
            if family=='A_wait' and q in C.A and old[i]>=33:weights[i]+=rng.uniform(-.5,.5)
    m.Minimize(sum(w*t for w,t in zip(weights,tv)));status=m.Solve()
    if status!=pywraplp.Solver.OPTIMAL:return None,{}
    nt=[math.floor(v.solution_value()+1e-6) for v in tv]
    assert all(nt[j]>nt[i] for j,ps in enumerate(pred) for i in ps)
    c['t']=nt
    return normalize(c),dict(family=family,window=[lo,hi],target_wire=target,changes=sum(a!=b for a,b in zip(old,nt)))

def commute_window(c,rng):
    """Rewrite a complete CX window, permitting shared-control/target reorder."""
    c=C.clone(c);us=c['u'];old=c['t'];R=c['meta']['R'];cut=rng.choice([0,12,18,26,30])
    m=cp_model.CpModel();ts=[m.NewIntVar(0,max(old),f't{i}') for i in range(len(us))]
    seqs={q:[] for q in range(36)}
    for j,u in enumerate(us):
        m.AddHint(ts[j],old[j])
        if old[j]>=R or old[j]<cut:m.Add(ts[j]==old[j])
        else:m.Add(ts[j]>=cut);m.Add(ts[j]<R)
        for q in u.qs:seqs[q].append(j)
        for i,a in enumerate(us[:j]):
            if not set(a.qs)&set(u.qs):continue
            if old[i]>=cut and old[j]<R and C.commute(a,u):continue
            m.Add(ts[j]>ts[i])
    for seq in seqs.values():
        if seq:m.AddAllDifferent([ts[i] for i in seq])
    w=[rng.randint(-8,8) for _ in us]
    m.Minimize(sum(x*t for x,t in zip(w,ts)))
    s=cp_model.CpSolver();s.parameters.num_workers=1;s.parameters.max_time_in_seconds=2;s.parameters.random_seed=rng.randrange(100000)
    st=s.Solve(m)
    if st not in (cp_model.OPTIMAL,cp_model.FEASIBLE):return None,dict(family='commute_window',status=s.StatusName(st))
    c['t']=[s.Value(t) for t in ts]
    return normalize(c),dict(family='commute_window',window=[cut,R-1],changes=sum(a!=b for a,b in zip(old,c['t'])))

def idle_protect(c,rng):
    """Four-step native echoed parity check in an existing data idle interval.

    Helper initialization and measurement included. Only released/virgin helper
    cells are eligible; following reset/measurement must destroy the helper.
    """
    us=c['u'];ts=c['t'];R=c['meta']['R'];options=[]
    for q in C.D:
        qi=[i for i,u in enumerate(us) if q in u.qs]
        for ia,ib in zip(qi,qi[1:]):
            a,b=ts[ia]+1,min(ts[ib]-1,R-1)
            if b-a<3 or b<18:continue
            for h in range(36):
                if h in C.D or abs(q//6-h//6)+abs(q%6-h%6)!=1:continue
                his=[i for i,u in enumerate(us) if h in u.qs]
                for start in sorted({a,max(a,b-5)}):
                    end=b
                    if any(start<=ts[i]<=end for i in his):continue
                    prev=[i for i in his if ts[i]<start];nxt=[i for i in his if ts[i]>end]
                    if prev and us[prev[-1]].name not in ('MX','MEASURE'):continue
                    if nxt and us[nxt[0]].name not in ('RESET','RX','MEASURE','MX'):continue
                    options.append((q,h,start,end))
    if not options:return None,{}
    q,h,a,b=rng.choice(options);axis=rng.choice(['X','Z']);d=C.clone(c);bit=C.bit(d)
    init=[f'reset q[{h}];']+([f'h q[{h}];'] if axis=='Z' else [])
    edge=f'cx q[{q}],q[{h}];' if axis=='X' else f'cx q[{h}],q[{q}];'
    meas=[f'measure q[{h}] -> c[{bit}];']
    if axis=='Z':meas=[f'h q[{h}];']+meas+[f'h q[{h}];']
    for lines,t in [(init,a),([edge],a+1),([edge],b-1),(meas,b)]:d['u'].append(C.Unit(lines));d['t'].append(t)
    d['tail'].append(f'// DETECTOR c[{bit}]')
    return normalize(d),dict(family='wait_split',qubit=q,helper=h,axis=axis,window=[a,b])

def known_watch(c,rng):
    us=c['u'];ts=c['t'];options=[]
    for q in range(36):
        seq=[i for i,u in enumerate(us) if q in u.qs]
        for i,j in zip(seq,seq[1:]):
            if us[i].name not in ('MEASURE','MX','RX','RESET') or ts[j]<=ts[i]+1 or ts[j]>=c['meta']['R']:continue
            if ts[i]<20:continue
            options.append((q,i,j))
    if not options:return None,{}
    q,i,j=rng.choice(options);d=C.clone(c);b=C.bit(d);basis='X' if us[i].name in ('RX','MX') else 'Z';t=rng.choice([ts[i]+1,ts[j]-1])
    lines=[f'measure q[{q}] -> c[{b}];']
    if basis=='X':lines=[f'h q[{q}];']+lines+[f'h q[{q}];']
    d['u'].append(C.Unit(lines));d['t'].append(t)
    oldbit=re.findall(r'c\[(\d+)\]',' '.join(us[i].lines))
    d['tail'].append(f'// DETECTOR c[{b}]'+(f' c[{oldbit[0]}]' if oldbit else ''))
    return normalize(d),dict(family='known_watch',qubit=q,basis=basis,time=t)

def readout_window(c,rng):
    # Simultaneous disjoint readout edges, with full detector parity transport.
    d=C.clone(c);applied=[]
    for _ in range(rng.choice([1,2,3])):
        last={u.qs[0]:i for i,u in enumerate(d['u']) if u.name=='MEASURE' and d['t'][i]>=d['meta']['R']+1}
        edges=[(a,b) for a,i in last.items() for b,j in last.items() if a!=b and abs(a//6-b//6)+abs(a%6-b%6)==1 and d['t'][i]==d['t'][j] and not {a,b}&set(sum(applied,[]))]
        if not edges:break
        a,b=rng.choice(edges);i,j=last[a],last[b];ba=int(re.findall(r'c\[(\d+)\]',d['u'][i].lines[0])[0]);bb=int(re.findall(r'c\[(\d+)\]',d['u'][j].lines[0])[0]);t=d['t'][i]
        d['t'][i]=d['t'][j]=t+1;d['u'].append(C.Unit([f'cx q[{a}],q[{b}];']));d['t'].append(t)
        for k,l in enumerate(d['tail']):
            if not l.startswith('// DETECTOR'):continue
            bits=set(map(int,re.findall(r'c\[(\d+)\]',l)))
            if bb in bits:bits^={ba}
            d['tail'][k]='// DETECTOR '+' '.join(f'c[{z}]' for z in sorted(bits))
        applied.append([a,b])
    return (normalize(d),dict(family='readout_window',edges=applied)) if applied else (None,{})

FAMILIES=['prefix_mix','release','A_wait','idle_mix','commute_window','wait_split','known_watch','readout_window']
def mutate(c,rng,index):
    fam=FAMILIES[index%len(FAMILIES)]
    try:
        if fam in FAMILIES[:4]:return weighted_window(c,rng,fam)
        return {'commute_window':commute_window,'wait_split':idle_protect,'known_watch':known_watch,'readout_window':readout_window}[fam](c,rng)
    except Exception as e:return None,dict(family=fam,error=repr(e))

def score_job(job):
    path,source,moves=job;t=time.monotonic();p=Path(path)
    try:
        text=p.with_suffix('.qasm').read_text();data=json.loads(p.with_suffix('.json').read_text())['data_qubits']
        ev=C.exact2.Eval(text,data);c1=float(ev.fp@ev.n_single);a=math.exp(-float(ev.fp@(1-ev.a_single)))
        if abs(c1)>=1e-12:return dict(stem=p.name,ok=False,c1=c1,error='first-order loss',source=source,moves=moves)
        r=dict(stem=p.name,source=source,moves=moves,c1=c1,exp_minus_A1=a)
        try:r.update(mom.evaluate(ev))
        except Exception as e:r['cubic_error']=repr(e)
        if a<.5002:return dict(r,ok=False,error='acceptance proxy')
        outdir=p.parent/'sparse_results'/p.name;outdir.mkdir(parents=True,exist_ok=True);sw.__file__=str(outdir/'sparse_walsh.py')
        with contextlib.redirect_stdout(io.StringIO()):ao=sw.run(p,72,True,procs=1)
        r.update(ok=True,allorders=ao['loss'],acceptance=ao['acceptance'],omission_bound=ao['conditional_loss_kernel_omission_bound'],seconds=time.monotonic()-t)
        (outdir/(p.name+'_canonical_sparse_result.json')).unlink()
        outdir.rmdir()
        return r
    except Exception as e:return dict(stem=p.name,ok=False,error=repr(e),source=source,moves=moves,seconds=time.monotonic()-t)

def save(c,p):
    c=normalize(c);p.with_suffix('.qasm').write_text(C.textof(c));p.with_suffix('.json').write_text(json.dumps(c['meta'],indent=2));return c

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--workers',type=int,default=8);ap.add_argument('--generations',type=int,default=6);ap.add_argument('--population',type=int,default=8);ap.add_argument('--children',type=int,default=3);ap.add_argument('--seed',type=int,default=3001);ap.add_argument('--label',default='directed_run');args=ap.parse_args()
    out=H/args.label;out.mkdir(exist_ok=True);rng=random.Random(args.seed);seen=set();circuits={};prov={};cache={};trace=[];rejections=[]
    for rec in json.loads((H/'directed_seeds.json').read_text()):
        try:
            src=H/rec['local'];c=normalize(C.read(src));fp=digest(c)
            if fp in seen:continue
            seen.add(fp);name='seed_'+fp;circuits[name]=save(c,out/name);prov[name]=dict(source=rec['source'],moves=[])
        except Exception as e:rejections.append(dict(seed=rec,error=repr(e)))
    population=list(circuits);accepted_moves=0;counter=0
    for gen in range(args.generations):
        jobs=list(population)
        for parent in population:
            for k in range(args.children):
                child,desc=mutate(circuits[parent],rng,counter);counter+=1
                if child is None:rejections.append(dict(parent=parent,**desc));continue
                fp=digest(child)
                if fp in seen:continue
                seen.add(fp);name=f'g{gen}_{fp}';circuits[name]=save(child,out/name)
                prov[name]=dict(source=prov[parent]['source'],moves=prov[parent]['moves']+[desc],parent=parent)
                jobs.append(name)
        pending=[n for n in jobs if n not in cache];print('generation',gen,'new',len(pending),'pool',len(jobs),flush=True)
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            fs={pool.submit(score_job,(str(out/n),prov[n]['source'],prov[n]['moves'])):n for n in pending}
            for f in as_completed(fs):
                n=fs[f];r=f.result();r.update(generation=gen,parent=prov[n].get('parent'));cache[n]=r;trace.append(r)
                (out/(n+'.score.json')).write_text(json.dumps(r,indent=2))
                if r.get('ok') and r['acceptance']>=.5:
                    if r.get('parent') and r['allorders']<cache.get(r['parent'],{}).get('allorders',float('inf'))-1e-13:accepted_moves+=1
                    print(n,r['allorders'],r['acceptance'],flush=True)
                else:print('rejected',n,r.get('error'),flush=True)
        good=[cache[n] for n in jobs if cache[n].get('ok') and cache[n]['acceptance']>=.5]
        good.sort(key=lambda r:(round(r['allorders'],13),len(prov[r['stem']]['moves'])))
        if not good:raise RuntimeError('no accepted population')
        # Half fitness elites, half distinct/worse intermediates. No rewards
        # for excess acceptance; it is a hard filter only.
        chosen=good[:max(1,args.population//2)]
        rest=[r for r in good if r not in chosen];rng.shuffle(rest)
        chosen+=rest[:args.population-len(chosen)];population=[r['stem'] for r in chosen]
        summary=dict(generation=gen,new_evaluations=len(pending),total_evaluations=len(trace),accepted_moves=accepted_moves,best=good[0],selected=chosen,rejections=len(rejections))
        (out/f'generation_{gen}.json').write_text(json.dumps(summary,indent=2))
        with lzma.open(out/'trace.jsonl.xz','wt') as f:
            for r in trace:f.write(json.dumps(r)+'\n')
        print('BEST',gen,good[0]['stem'],good[0]['allorders'],flush=True)
    ranked=sorted([r for r in cache.values() if r.get('ok') and r['acceptance']>=.5],key=lambda r:r['allorders'])
    (out/'summary.json').write_text(json.dumps(dict(evaluations=len(trace),valid=sum(r.get('ok',False) for r in trace),accepted_moves=accepted_moves,ranked=ranked,rejections=rejections),indent=2))
    keep={r['stem'] for r in ranked[:12]}|set(population)
    for n in circuits:
        if n not in keep:
            for ext in ['.qasm','.json','.score.json']:(out/(n+ext)).unlink(missing_ok=True)
    print('DONE',len(trace),'best',ranked[0]['stem'],ranked[0]['allorders'],flush=True)

if __name__=='__main__':main()
