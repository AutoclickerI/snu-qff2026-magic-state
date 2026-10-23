"""PRE-only construction; existing judge and exact evaluator are unchanged."""
import os
os.environ.update(OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1')
import sys
sys.dont_write_bytecode = True
from pathlib import Path
ROOT=Path('/home/jihoon/competitions/quantumn')
HERE=ROOT/'work/lanes/PRE'
sys.path[:0]=[str(ROOT/'work'),str(ROOT/'work/lanes/EVAL'),str(ROOT/'work/lanes/L5_precycle')]
import json, re, copy, random, math
import numpy as np
import cultiv_port as cp
from qcirc import Circ
from schedules import dag, commute, greedy
from exact2 import Eval, run
import tprep
import xtim
xtim.cache_dir=str(HERE/'.xtim_cache')
os.environ['XTIM_TWIRL_CACHE_DIR']=str(HERE/'.twirl_cache')
BASE=json.loads((ROOT/'work/lanes/L5_precycle/combined_lns_0012.json').read_text())
OPS=[(k,tuple(qs),b) for k,qs,b in BASE['schedule']['ops']]
TIMES=BASE['schedule']['times']
NPRE=137
DETS=[[int(x) for x in re.findall(r'c\[(\d+)\]',s)] for s in (ROOT/'work/submissions/v12_L5lns12.qasm').read_text().splitlines() if s.startswith('// DETECTOR')]

def emit(ops,times,detectors,nbits):
    """Same lazy-reset emission as v12's generating lane."""
    c=Circ();c.nbits=nbits;c.detectors=copy.deepcopy(detectors)
    used=tuple(sorted({q for _,qs,_ in ops for q in qs}));shift=min(times)
    for t in range(max(times)-shift+1):
        for (k,qs,b),tm in zip(ops,times):
            if tm-shift!=t:continue
            if k=='cx':c.cx(*qs)
            elif k=='RX':c.rx(*qs)
            elif k=='R':c.reset(*qs)
            elif k in ('M','MX','MX_KEEP'):
                c.sops.append(('MX' if k=='MX_KEEP' else k,qs,b))
            else:c.g(k[2:],*qs)
        if t<max(times)-shift:c.barrier(*used)
    text=c.rescheduled(lazy_init=True).text()
    for k,qs,b in ops:
        if k=='MX_KEEP':
            old=f'measure q[{qs[0]}] -> c[{b}];'
            text=text.replace(old,old+f'\nh q[{qs[0]}];')
    return text

def pack(ops,ct,npre,seed=0,can_commute=True):
    pre=ops[:npre];cyc=ops[npre:];pred,succ=dag(pre,can_commute)
    limits=[min((t-1 for op2,t in zip(cyc,ct) if set(op[1])&set(op2[1])),default=min(ct)-1) for op in pre]
    occupied={(q,t) for op,t in zip(cyc,ct) for q in op[1]}
    distance=[0]*npre
    for i in range(npre):distance[i]=1+max((distance[j] for j in pred[i]),default=0)
    rng=random.Random(seed);pri=[d+(rng.random()*3 if seed else 0) for d in distance]
    out=[None]*npre;remaining=set(range(npre));done=set();t=max(limits)
    while remaining:
        ready=sorted((i for i in remaining if succ[i]<=done and t<=limits[i]),key=lambda i:(-pri[i],i))
        selected=[]
        for i in ready:
            if any((q,t) in occupied for q in pre[i][1]):continue
            if any(out[j]<=t for j in succ[i]):continue
            selected.append(i);out[i]=t;occupied.update((q,t) for q in pre[i][1])
        remaining.difference_update(selected);done.update(selected);t-=1
        assert t>-2000
    return out+ct

def save(name,ops,times,detectors,nbits,npre,source):
    text=emit(ops,times,detectors,nbits)
    meta=dict(data_qubits=BASE['data_qubits'],source=source,schedule=dict(ops=ops,times=times,npre=npre),
              pre_end_step=max(times[:npre])-min(times),depth=max(times)-min(times)+1,n_2q=sum(k=='cx' for k,_,_ in ops))
    (HERE/f'{name}.qasm').write_text(text)
    (HERE/f'{name}.json').write_text(json.dumps(meta,indent=2)+'\n')
    return meta

def validate(name,shots=1000000):
    meta=json.loads((HERE/f'{name}.json').read_text())
    rep=tprep.check((HERE/f'{name}.qasm').read_text(),meta['data_qubits'],shots=shots,seed=0)
    d=dict(passed=rep.passed,format=rep.format_ok,class_ok=rep.class_ok,correctness=rep.correct_ok,acceptance_ok=rep.acceptance_ok,
           acceptance=rep.acceptance,score=rep.score,sem=rep.sem,shots=shots,seed=0,report=str(rep))
    (HERE/f'{name}.check.json').write_text(json.dumps(d,indent=2)+'\n')
    print(name,str(rep),flush=True)
    return d

def native_mapping(meta, ev):
    """Associate saved construction nodes with actual judge instructions/times."""
    sch=meta['schedule'];ops=sch['ops'];times=sch['times'];npref=sch['npre']
    chronological=sorted(range(len(ops)),key=lambda i:(times[i],i))
    free={};native_times={}
    for t in sorted(set(times)):
        for i in chronological:
            if times[i]!=t:continue
            qs=ops[i][1];nt=max(free.get(q,0) for q in qs)
            native_times[i]=nt
            for q in qs:free[q]=nt+1
        sync=max(free.values());free={q:sync for q in free}
    for i in chronological:
        if ops[i][0] in ('R','RX'):
            q=ops[i][1][0];following=[j for j in chronological if times[j]>times[i] and q in ops[j][1]]
            if following:native_times[i]=native_times[following[0]]-1
    emitted=iter(sorted(chronological,key=lambda i:(native_times[i],chronological.index(i))))
    ownership={};actual={}
    for ii,ins in enumerate(ev.m.prog):
        if not ev.m.steps[ii]:continue
        i=next(emitted);kind,qs,b=ops[i]
        native={'cx':'CX','MX_KEEP':'MX','g:t':'T','g:tdg':'T_DAG'}.get(kind,kind)
        assert (native,tuple(qs))==(ins.name,tuple(ins.qubits)),(i,native,qs,ins)
        actual[i]=ev.m.steps[ii][0][1];ownership[ii]=i<npref
    assert next(emitted,None) is None
    return actual,ownership
