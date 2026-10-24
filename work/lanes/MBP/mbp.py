"""MBP generators and grid-free prices. Run with the repository .venv/bin/python.

Grid-free circuits use dedicated virtual helper cells (36..63); this deliberately
relaxes helper occupancy, in addition to adjacency. Physical builds do neither.
"""
import os, sys, json, re, itertools, math, time, argparse
from pathlib import Path
sys.dont_write_bytecode = True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'): os.environ[k]='1'
ROOT=Path('/home/jihoon/competitions/quantumn'); OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(OUT/'inputs'),str(ROOT/'work/lanes/EVAL')]
import model, exact2, gf33, schedule as S
gf33.early_merge.PREFIX=str(OUT/'inputs/v11_A1i_alap45.qasm')
from util import native_times
import stim, xtim, tprep, tprep.qasm as tq
import importlib
tp=importlib.import_module('tprep.parse')
xtim.cache_dir=str(OUT/'.xtim_cache')
from ortools.sat.python import cp_model
GENS=gf33.GENS
SUPPORTS=GENS+[[0,1,3,6]]
ORIG_VERIFY=model.verify
ORIG_ADJ=tq.adjacent
ORIG_PARSE_ADJ=tp.adjacent

def relax(n=64):
    tq.adjacent=lambda a,b: True
    tp.adjacent=lambda a,b: True
    model.N_QUBITS=n
    model.verify=lambda *a,**kw: ORIG_VERIFY(*a,**dict(kw,n_qubits=n))

def physical():
    tq.adjacent=ORIG_ADJ;tp.adjacent=ORIG_PARSE_ADJ;model.N_QUBITS=36;model.verify=ORIG_VERIFY

def emit(ops,dets,n=64):
    """ops: (native step, list of statements, provenance)."""
    by={}
    for t,ls,tag in ops: by.setdefault(t,[]).append((ls,tag))
    used=sorted({int(q) for _,ls,_ in ops for s in ls for q in re.findall(r'q\[(\d+)\]',s)})
    bar='barrier '+','.join(f'q[{q}]' for q in used)+';'
    out=['OPENQASM 2.0;','include "qelib1.inc";',f'qreg q[{n}];','creg c[256];']
    tags={}
    for t in range(max(by)+1):
        if not by.get(t):
            # Preserve an empty physical step on an already initialized data wire.
            by[t]=[(['id q[0];'],'clock')]
        for ls,tag in by[t]:
            for s in ls: tags[len(out)+1]=tag;out.append(s)
        if t<max(by): out.append(bar)
    out += ['// DETECTOR '+' '.join(f'c[{b}]' for b in sorted(set(d))) for d in dets]
    return '\n'.join(out)+'\n',tags

def unitary(cells,plus,R,selected=(0,1,2),tag='prep'):
    out=[]
    for i,q in enumerate(cells):
        p=(i in [gf33.PIV[k] for k in selected]) != plus
        out.append((R-4,[f'reset q[{q}];']+([f'h q[{q}];'] if p else []),tag))
    for t,layer in enumerate(gf33.LAYERS0):
        for k,(c,d) in enumerate(layer):
            if k not in selected:continue
            a,b=(cells[d],cells[c]) if plus else (cells[c],cells[d])
            out.append((R-3+t,[f'cx q[{a}],q[{b}];'],tag))
    return out

def mbprep(cells,plus,R,anc,bit,kind='direct',order=(0,1,2),permutation=(0,1,2,3),hybrid=0,legacy=False,red_mask=7):
    """Prepare by stabilizer projection; returns ops, the 3 frame parities, extra detectors.

    direct: independent bare ancillas, parallel edge coloring; seq: one recycled
    ancilla; cat: Bell pair per stabilizer; flag: bare ancilla bracketed by flag;
    redundant: 4 checks including their product; hybrid1/2: partial encoder.
    """
    hybrid_tree=kind=='hybrid2t'
    if kind.startswith('hybrid'):hybrid=int(kind[6]);kind='direct'
    spine_cat='spine' in kind
    reuse_cat='reuse' in kind or spine_cat
    kind=kind.replace('reuse','').replace('spine','')
    selected=tuple(range(hybrid));rows=[k for k in order if k not in selected]
    redundant=kind=='redundant' or kind.endswith('red')
    if kind.endswith('red'):kind=kind[:-3]
    if redundant:rows=list(order) if 3 in order else list(order)+[3]
    fourth=set()
    for j,s in enumerate(GENS):
        if red_mask>>j&1:fourth^=set(s)
    supports=GENS+[sorted(fourth)]
    frame=[[] for _ in range(3)];extra=[];jobs=[]; pred=[];last={};init=[]
    def add(ls,qs,deps=()):
        i=len(jobs);jobs.append((ls,tuple(qs)));pred.append(set(deps))
        for q in qs:
            if q in last:pred[i].add(last[q])
            last[q]=i
        return i
    # Partial row encoder. The unselected pivots have no outgoing CXs.
    for i,q in enumerate(cells):
        p=(i in [gf33.PIV[k] for k in selected]) != plus
        init.append(add([f'reset q[{q}];']+([f'h q[{q}];'] if p else []),[q]))
    edges=[(0,4),(1,5),(0,6),(1,6),(6,2)] if hybrid_tree else [(c,d) for layer in gf33.LAYERS0 for k,(c,d) in enumerate(layer) if k in selected]
    for c,d in edges:
        a,b=(cells[d],cells[c]) if plus else (cells[c],cells[d])
        add([f'cx q[{a}],q[{b}];'],[a,b])
    partial=list(last.values())
    results={};endrow=None
    for j,k in enumerate(rows):
        pp=([3,1,2,0],[3,1,0,2],[3,0,1,2],[3,2,1,0])[k] if spine_cat else permutation
        supp=[supports[k][x] for x in pp]
        deps=([endrow] if kind=='seq' and endrow is not None else [])
        if kind.startswith('cat'):
            count=int(kind[-1]) if kind in ('cat3','cat4') else 2
            av=anc[:count] if reuse_cat else anc[count*j:count*(j+1)];assert len(av)==count
            ii=[]
            for z,f in enumerate(av):
                plusinit=(z==0) if legacy else (z==0)!=plus
                ii.append(add([f'reset q[{f}];']+([f'h q[{f}];'] if plusinit else []),[f],deps))
            ready=ii[0]
            for z in range(1,count):
                a,b=av[z-1],av[z]
                if plus and not legacy:a,b=b,a
                ready=add([f'cx q[{a}],q[{b}];'],[a,b],ii)
            for z,i in enumerate(supp):
                ix=([0,0,1,1] if kind=='cat' else [0,1,1,1] if kind=='cat13' else [0,0,1,2] if count==3 else [0,1,2,3])[z]
                f=av[ix];u,v=(cells[i],f) if plus else (f,cells[i])
                add([f'cx q[{u}],q[{v}];'],[u,v],[ready]+(partial if hybrid else []))
            rec=[]
            for f in av:
                ls=([f'h q[{f}];'] if not plus else [])+[f'measure q[{f}] -> c[{bit}];']
                add(ls,[f]);rec.append(bit);bit+=1
        else:
            a=anc[0 if kind=='seq' else j]
            ready=add([f'reset q[{a}];']+([] if plus else [f'h q[{a}];']),[a],deps)
            if kind=='flag':
                f=anc[len(rows)+j]
                fi=add([f'reset q[{f}];']+([f'h q[{f}];'] if plus else []),[f],deps)
                u,v=(f,a) if plus else (a,f)
                ready=add([f'cx q[{u}],q[{v}];'],[a,f],[ready,fi])
            for i in supp:
                u,v=(cells[i],a) if plus else (a,cells[i])
                add([f'cx q[{u}],q[{v}];'],[u,v],[ready]+(partial if hybrid else []))
            if kind=='flag':
                add([f'cx q[{u}],q[{v}];'] if False else [f'cx q[{f if plus else a}],q[{a if plus else f}];'],[a,f])
                add(([f'h q[{f}];'] if plus else [])+[f'measure q[{f}] -> c[{bit}];'],[f])
                extra.append([bit]);bit+=1
            rec=[bit];bit+=1
            endrow=add(([f'h q[{a}];'] if not plus else [])+[f'measure q[{a}] -> c[{rec[0]}];'],[a])
        results[k]=rec
        if k<3:frame[k]=rec
    if redundant:extra.append(results[3]+sum((results[k] for k in range(3) if red_mask>>k&1),[]))
    # Fixed per-wire order, as-late-as-possible scheduling under the desired end.
    succ=[[] for _ in jobs]
    for i,ps in enumerate(pred):
        for p in ps:succ[p].append(i)
    ts=[0]*len(jobs)
    for i in reversed(range(len(jobs))):ts[i]=min((ts[j]-1 for j in succ[i]),default=R-1)
    assert min(ts)>=0,(kind,R,min(ts))
    return [(t,ls,'mb') for t,(ls,qs) in zip(ts,jobs)],frame,extra,bit

def prefix(which):
    if which=='sep':
        h,stm=gf33.early_merge.prefix_steps()
        # Fold native pairs before emission, preserving the supplied scheduled prefix.
        raw=[s for s,t in stm];units=S.fold_units(raw)
        ops=[(min(stm[i][1] for i in u.raw_indices),u.lines,'pre') for u in units]
        return ops,gf33.PRE_DATA
    src=OUT/'inputs/reuse19_tuned'
    text=src.with_suffix('.qasm').read_text();meta=json.loads(src.with_suffix('.json').read_text())
    h,raw,tail=S.qasm_ops(text);us=S.fold_units(raw);ts=native_times(text,us)
    pre=set(meta['prefix_unit_indices'])
    if which=='v22h':
        import collections
        actual=(OUT/'inputs/v22h_c2c9.qasm').read_text();hh,rr,tail=S.qasm_ops(actual);au=S.fold_units(rr);at=native_times(actual,au)
        lookup=collections.defaultdict(list)
        for i,u in enumerate(au):lookup[tuple(u.lines)].append(i)
        counts=collections.Counter();chosen=[]
        for i,u in enumerate(us):
            key=tuple(u.lines);ordinal=counts[key];counts[key]+=1
            if i in pre:chosen.append(lookup[key][ordinal])
        assert len(chosen)==129
        return [(at[i],au[i].lines,'pre') for i in sorted(chosen)],gf33.PRE_DATA
    return [(ts[i],u.lines,'pre') for i,u in enumerate(us) if i in pre],gf33.PRE_DATA

def prefix_detectors(which):
    if which!='v22h':return [list(map(int,re.findall(r'c\[(\d+)\]',d))) for d in gf33.PRE_DETECTORS]
    ops,_=prefix(which);bits={int(b) for _,ls,_ in ops for s in ls for b in re.findall(r'c\[(\d+)\]',s)}
    out=[]
    for line in (OUT/'inputs/v22h_c2c9.qasm').read_text().splitlines():
        if line.startswith('// DETECTOR'):
            bb=list(map(int,re.findall(r'c\[(\d+)\]',line)))
            if set(bb)<=bits:out.append(bb)
    assert len(out)==18
    return out

def build(blocks='',kind='direct',R=33,order=(0,1,2),perm=(0,1,2,3),pre='sep',legacy=False,red_mask=7):
    ops,data=prefix(pre)
    cells={k:gf33.FREE[j*7:j*7+7] for j,k in enumerate('ABC')}
    bit=60 if pre=='v22h' else 35;frames={};dets=[]
    for j,k in enumerate('ABC'):
        if k in blocks:
            recipe=kind.split(',')[j] if ',' in kind else kind
            stride=8 if legacy else 16
            oo,ff,dd,bit=mbprep(cells[k],k=='A',R,list(range(36+stride*j,36+stride*(j+1))),bit,recipe,order,perm,legacy=legacy,red_mask=red_mask)
            ops += [(t,ls,k) for t,ls,_ in oo];frames[k]=ff;dets+=dd
        else:ops+=unitary(cells[k],k=='A',R,tag=k);frames[k]=[[],[],[]]
    for i in range(7):
        d,a,b,c=[data[i]]+[cells[k][i] for k in 'ABC']
        ops += [(R,[f'cx q[{d}],q[{a}];'],'round'),(R,[f'cx q[{b}],q[{c}];'],'round'),
                (R+1,[f'cx q[{b}],q[{d}];'],'round'),(R+1,[f'measure q[{a}] -> c[{14+i}];'],'round'),
                (R+1,[f'measure q[{c}] -> c[{21+i}];'],'round'),
                (R+2,[f'h q[{b}];',f'measure q[{b}] -> c[{28+i}];'],'round')]
    dets=prefix_detectors(pre)+dets
    for j,s in enumerate(GENS):
        dets += [[14+i for i in s]+frames['A'][j], [28+i for i in s]+frames['B'][j]+frames['C'][j], [21+i for i in s]]
    dets.append(list(range(21,28)))
    nq=64 if legacy else 84
    text,tags=emit(ops,dets,nq)
    return text,dict(data_qubits=data,grid_free=True,virtual_helpers=True,n_qubits=nq,legacy_single=legacy,red_mask=red_mask,blocks=blocks,kind=kind,R=R,order=order,perm=perm,pre=pre,cx=text.count('cx '),line_regions=tags)

def stim_verify(text,n=64):
    ss,labels,err=tq.convert(text,n,model.STANDARD);assert not err,err
    # T->I is the valid X_L Clifford surrogate for this prefix; the real circuit
    # is independently verified over all measurement outcomes by tprep.check.
    ss='\n'.join(l for l in ss.splitlines() if not l.startswith(('T ','T_DAG ')))
    c=stim.Circuit(ss);c.detector_error_model()
    return c.num_detectors

def check(text,data,n=64):
    r=tprep.check(text,data,shots=10**6,seed=0,n_qubits=n)
    return dict(passed=r.passed,format=r.format_ok,correct=r.correct_ok,acceptance=r.acceptance,score=r.score,errors=r.format_errors+r.correctness_errors+([r.class_error] if r.class_error else []))

def price(text,meta,procs=1,third=True):
    import fast_third
    import fast_pairs
    import cache_tables
    t0=time.time();stimdet=stim_verify(text,meta.get('n_qubits',36));ch=check(text,meta['data_qubits'],meta.get('n_qubits',36))
    assert ch['correct'],ch
    ev=exact2.Eval(text,meta['data_qubits']);c1=float((ev.fp*ev.n_single).sum())
    r=fast_pairs.run(ev,procs,third=third,keep_thr=1e-10)
    cache_stats=cache_tables.install(ev)
    t3=fast_third.third_order(ev,procs)[0]+r['t3bc'] if third and abs(c1)<1e-12 else None
    return dict(c1=c1,second=r['loss2'],third=t3,total=r['loss']+t3 if t3 is not None else None,expA1=math.exp(-r['A1']),check=ch,stim_detectors=stimdet,seconds=time.time()-t0,table_cache=cache_stats,
        top_pairs=[dict(loss=c,first=ev.fault_label(i),second=ev.fault_label(j)) for c,i,j,*_ in sorted(r['big'],reverse=True)[:12]])

def main():
    p=argparse.ArgumentParser();p.add_argument('name');p.add_argument('--blocks',default='');p.add_argument('--kind',default='direct');p.add_argument('--R',type=int,default=33);p.add_argument('--pre',default='sep');p.add_argument('--order',default='012');p.add_argument('--perm',default='0123');p.add_argument('--procs',type=int,default=1);p.add_argument('--second',action='store_true');p.add_argument('--legacy-single',action='store_true');p.add_argument('--red-mask',type=int,default=7);a=p.parse_args()
    relax(64 if a.legacy_single else 84);text,meta=build(a.blocks,a.kind,a.R,tuple(map(int,a.order)),tuple(map(int,a.perm)),a.pre,a.legacy_single,a.red_mask)
    stem=OUT/a.name;stem.with_suffix('.qasm').write_text(text);stem.with_suffix('.json').write_text(json.dumps(meta,indent=2)+'\n')
    row=price(text,meta,a.procs,not a.second);stem.with_suffix('.result.json').write_text(json.dumps(dict(meta,**row),indent=2)+'\n');print(json.dumps(dict(name=a.name,**row)),flush=True)

if __name__=='__main__':main()
