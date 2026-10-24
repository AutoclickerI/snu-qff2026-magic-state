"""Grid parity-network realizations of all 16 protected phase supports.

The resynthesized injection encoder and its verification prepare |+_L>.
A fifth |+> variable is added on q6. Nearest-neighbour parity networks apply
the selected 15 signed rotations and uncompute; measuring the fifth variable
and zero helpers detects phase/data errors before the retained Steane suffix.
The coordinate labels are fixed across forms, not renamed per candidate.
"""
import os,sys,json,re,random,argparse,heapq
from pathlib import Path
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(OUT),str(OUT/'inputs'),str(ROOT/'work/lanes/EVAL')]
import schedule as S
from schedules import placement,write
from util import native_times
from exact2 import Eval
from model import Basis,comm

CELLS=[0,1,2,3,4,6,7,8,9,10,13,14,15,19,20]
DATA=[0,20,7,4,3,15,8]
EDGES=[(i,j)for i,q in enumerate(CELLS)for j,v in enumerate(CELLS)if abs(q//6-v//6)+abs(q%6-v%6)==1]
ROWS=dict(zip(DATA,[2,31,4,21,14,19,8]));ROWS[6]=16

def route(rows,left,rng):
    # Beam search through reversible physical CNOTs to the nearest missing axis.
    start=tuple(rows);beam=[(start,[])];seen={start}
    for depth in range(1,10):
        nxt=[]
        for state,path in beam:
            es=EDGES[:];rng.shuffle(es)
            for c,t in es:
                if not state[c] or state[c]==state[t]:continue
                v=state[c]^state[t]
                if v==25:continue  # avoid a bare logical-Z phase fault
                ns=list(state);ns[t]=v;ns=tuple(ns)
                if ns in seen:continue
                seen.add(ns);np=path+[(c,t)]
                if v in left:return ns,np
                # Number of bit differences is a search heuristic only.
                dist=min((v^x).bit_count()for x in left)
                potential=sum(any((ns[c]^ns[t])==x for c,t in EDGES)for x in left)
                nxt.append((dist-.05*potential+rng.random()*.1,ns,np))
        if not nxt:break
        nxt.sort(key=lambda a:a[0]);beam=[(s,p)for _,s,p in nxt[:128]]
    raise RuntimeError(('route exhausted',left))

def network(form,seed):
    rng=random.Random(seed);rows=[ROWS.get(q,0)for q in CELLS];left=set(form['support']);ops=[];gates=[]
    coeff=dict(zip(form['support'],form['signed_representations'][0]['coefficients']))
    def consume():
        order=list(range(len(rows)));rng.shuffle(order)
        for q in order:
            if rows[q]in left:
                ops.append((('t'if coeff[rows[q]]==1 else 'tdg'),CELLS[q],rows[q]));left.remove(rows[q])
    consume()
    while left:
        ns,path=route(rows,left,rng)
        for c,t in path:
            rows[t]^=rows[c];gates.append((c,t));ops.append(('cx',CELLS[c],CELLS[t]));consume()
        assert tuple(rows)==ns
    for c,t in reversed(gates):ops.append(('cx',CELLS[c],CELLS[t]))
    return ops,len(gates)*2

def build(form,trials=12,criterion='cx'):
    best=None;failed=[]
    for seed in range(trials):
        try:ops,cx=network(form,seed)
        except RuntimeError as ex:
            failed.append(dict(seed=seed,error=str(ex)));continue
        us=[S.Unit([f'cx q[{a}],q[{b}];'if op=='cx'else f'{op} q[{a}];'],[])for op,a,b in ops]
        dep=max(placement(us,'asap'))+1
        key=(cx,dep)if criterion=='cx'else(dep,cx)
        if best is None or key<best[0]:best=(key,ops,seed,cx,dep)
    if best is None:raise RuntimeError((form['id'],failed))
    _,ops,seed,ncx,dep=best
    src=OUT/'encoder19';text=src.with_suffix('.qasm').read_text();meta=json.loads(src.with_suffix('.json').read_text());h,r,t=S.qasm_ops(text);us=S.fold_units(r);ts=native_times(text,us)
    # Original step20 verification is shifted to17 by encoder19.
    prefix=[u for u,v in zip(us,ts)if v<=29 and u.name not in ('T','TDG')]
    suffix=[u for u,v in zip(us,ts)if v>29]
    # Drop the double-cat checks (records 7..13), retaining injection checks.
    tail=[]
    for line in t:
        bits=[int(x)for x in re.findall(r'c\[(\d+)\]',line)]
        tail.append(line)
    tail.append('// DETECTOR c[54]')
    extra=[]
    for q in CELLS:
        if q in DATA:continue
        extra.append(S.Unit([f'reset q[{q}];']+([f'h q[{q}];']if q==6 else[]),[]))
    phase=[S.Unit([f'cx q[{a}],q[{b}];'if op=='cx'else f'{op} q[{a}];'],[])for op,a,b in ops]
    end=[];idx=47
    for q in CELLS:
        if q in DATA:continue
        if q==6:end.append(S.Unit([f'h q[{q}];','measure q[6] -> c[54];'],[]))
        else:
            end.append(S.Unit([f'measure q[{q}] -> c[{idx}];'],[]));tail.append(f'// DETECTOR c[{idx}]');idx+=1
    h=[re.sub(r'creg c\[\d+\]',f'creg c[{max(idx,55)}]',l)for l in h]
    units=prefix+extra+phase+end+suffix
    times=placement(units,'alap');name=form['id']+('_parity'if criterion=='cx'else'_depth')
    meta=dict(data_qubits=meta['data_qubits'],form=form['id'],form_support=form['support'],phase_coordinates=ROWS,parity_CX=ncx,parity_depth=dep,search_seed=seed,search_trials=trials,failed_search_trials=failed,injection_cx=19,synthesis='grid parity beam synthesis over fixed coordinates, using TREP encoder19')
    stem=write('encoder19',name,times,units,h,tail,meta)
    try:
        ev=Eval(stem.with_suffix('.qasm').read_text(),meta['data_qubits']);res={'correct':True,'c1':float(ev.fp@ev.n_single),'form':form['id'],'phase_CX':ncx}
        byq={}
        for op,q,ax in ops:
            if op!='cx':byq.setdefault(q,[]).append(ax)
        b=Basis();images=[];observed=[]
        for x,z,c,theta,ii in ev.m.rots:
            q=ev.m.prog[ii].qubits[0];expected=byq[q].pop(0);coord=b.express(x)
            if coord is None:b.add(x);images.append(expected);coord=b.express(x)
            mapped=0
            for j,img in enumerate(images):
                if coord>>j&1:mapped^=img
            assert mapped==expected,(form['id'],mapped,expected)
            observed.append(mapped)
        assert sorted(observed)==form['support'] and len(images)==5
        assert all(comm(x,z,v,w)==0 for x,z,*_ in ev.m.rots for v,w,*_ in ev.m.rots)
        res['phase_certificate']=dict(reference_support=sorted(observed),native_basis_to_reference=images,commuting=True)
    except Exception as ex:res={'correct':False,'error':str(ex),'form':form['id'],'phase_CX':ncx}
    stem.with_suffix('.build.json').write_text(json.dumps(res,indent=2)+'\n');print(res,flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--trials',type=int,default=12);p.add_argument('--ids',nargs='*');p.add_argument('--criterion',choices=['cx','depth'],default='cx');a=p.parse_args()
    e=json.loads((OUT/'inputs/enumeration.json').read_text())
    for f in e['forms']:
        if f['T']==15 and (not a.ids or f['id']in a.ids):build(f,a.trials,a.criterion)
