"""Joint native preparation of B=|0_L>, C=|0>^7 through the old final CX layer.

The C cells are temporary workspace and literal verification outputs. This
replaces the complete old B/C encoder and its final B->C layer. It preserves
the data/guard operations at the identified independent-state boundary.
"""
import argparse,copy,json,os,sys,time
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'work/tools'))
from qtools import price,write_stem
from qtools.validity import raw_check
from qtools.evaluator import frontend as f
from ortools.sat.python import cp_model

HERE=Path(__file__).resolve().parent
D=[6,20,19,10,2,22,16]
B=[12,26,25,11,3,28,17]
C=[18,27,24,5,4,29,23]
CELLS=B+C
EDGES=[(a,b) for a in CELLS for b in CELLS if abs(a//6-b//6)+abs(a%6-b%6)==1]
OLD_START={29:30,23:29,17:30,27:30,26:31,28:31,25:31,24:32,18:32,12:33,11:35,5:35,4:36,3:39}
INIT_MIN={29:30,23:29,17:30,27:30,26:31,28:31,25:31,24:32,18:32,12:37,11:35,5:34,4:36,3:39}
COL={q:i+1 for i,q in enumerate(B)}
BASE=ROOT/'work/lanes/MAIN/v37j'

def split_base():
    ops,dets=f.parse_current(BASE.with_suffix('.qasm').read_text())
    old=[];keep=[]
    for o in ops:
        take=(set(o.qs)<=set(CELLS) and all(OLD_START[q]<=o.time for q in o.qs) and o.time<=46)
        if o.qs==(12,) and o.time in (33,35):take=False
        (old if take else keep).append(o)
    removed={o.bit for o in old if o.bit is not None}
    dd=[]
    for row in dets:
        if row&set(range(330,344)):continue
        rr=row-removed
        if rr:dd.append(rr)
    dd += [{337+i} for i in range(7)]
    dd += [{330+i for i in row} for row in f.SUPPORTS]
    return keep,dd,old

def emit(ops,dets):
    used=sorted({q for o in ops for q in o.qs})
    lines=['OPENQASM 2.0;','include "qelib1.inc";','qreg q[36];',f'creg c[{max(o.bit or 0 for o in ops)+1}];']
    by={}
    for o in ops:by.setdefault(o.time,[]).append(o)
    for t in range(max(by)+1):
        if t:lines.append('barrier '+','.join(f'q[{q}]' for q in used)+';')
        for o in by.get(t,[]):
            q=o.qs[0]
            if o.kind in ('R','RX'):
                lines.append(f'reset q[{q}];')
                if o.kind=='RX':lines.append(f'h q[{q}];')
            elif o.kind in ('M','MX'):
                if o.kind=='MX':lines.append(f'h q[{q}];')
                lines.append(f'measure q[{q}] -> c[{o.bit}];')
                if o.kind=='MX':lines.append(f'h q[{q}];')
            elif o.kind=='CX':lines.append(f'cx q[{q}],q[{o.qs[1]}];')
            else:lines.append({'TDG':'tdg','T_DAG':'tdg','ID':'id'}.get(o.kind,o.kind.lower())+f' q[{q}];')
    lines+=['// DETECTOR '+' '.join(f'c[{b}]' for b in sorted(r)) for r in dets]
    return '\n'.join(lines)+'\n'

def make(sol,name):
    keep,dets,old=split_base();ops=copy.deepcopy(keep)
    dets=[r for r in dets if not(r&set(range(337,344)))]
    dets += [{337+i}|({366} if sol.get('c_carry',[0]*7)[i] else set()) for i in range(7)]
    if sol.get('source_zero'):
        source=next(o for o in ops if o.bit==366)
        assert (source.kind,source.qs,source.time)==('M',(1,),29)
        source.kind='R';source.bit=None
        dets=[r-{366} for r in dets if r-{366}]
    gates=[f.Op('CX',tuple(e),sol['T0']+t) for t,layer in enumerate(sol['ops']) for e in layer]
    for q in CELLS:
        touch=[o.time for o in gates if q in o.qs]
        if not touch:raise ValueError(('unused resource cell',q))
        if q==3 and (not sol.get('source_zero') or not int(sol['pivots'].get('3',sol['pivots'].get(3,0)))):
            continue  # Preserved prefix source (fixed zero or correlated with c366).
        t=min(touch)-1
        occupied={o.time for o in keep if q in o.qs}
        while t in occupied:t-=1
        assert t>=INIT_MIN[q],(q,t,INIT_MIN[q])
        kind='RX' if int(sol['pivots'].get(str(q),sol['pivots'].get(q,0))) else 'R'
        ops.append(f.Op(kind,(q,),t))
    ops+=gates
    seen={}
    for o in ops:
        for q in o.qs:
            key=(o.time,q)
            assert key not in seen,('collision',key,o,seen.get(key))
            seen[key]=o
    text=emit(ops,dets)
    stem=write_stem(text,D,HERE/'cand',name,source={'joint_resource':sol,'removed_cx':sum(o.kind=='CX' for o in old)})
    return stem,text

def build(T0=30,depth=17,cap=None,wx=10,wz=1,wbad=20,f1=True,source_zero=False,hint=None,wunflag=0,verified_init=False,gauge=()):
    keep,_,_=split_base();blocked={(o.time,q) for o in keep for q in o.qs}
    m=cp_model.CpModel()
    sel=[{e:m.NewBoolVar(f'cx{t}_{e[0]}_{e[1]}') for e in EDGES} for t in range(depth)]
    use=[]
    for t in range(depth):
        row={}
        for q in CELLS:
            vv=[v for e,v in sel[t].items() if q in e]
            m.AddAtMostOne(vv);row[q]=m.NewBoolVar(f'use{t}_{q}');m.AddMaxEquality(row[q],vv)
        use.append(row)
        for (a,b),v in sel[t].items():
            earliest=lambda q:INIT_MIN[q]+int(q!=3)
            if T0+t<max(earliest(a),earliest(b)) or (T0+t,a) in blocked or (T0+t,b) in blocked:
                m.Add(v==0)
    assert not gauge or source_zero
    nx=3+len(gauge) if source_zero else 4
    x=[{q:[m.NewBoolVar(f'x{t}_{q}_{k}') for k in range(nx)] for q in CELLS} for t in range(depth+1)]
    h=[{q:[m.NewBoolVar(f'h{t}_{q}_{k}') for k in range(11)] for q in CELLS} for t in range(depth+1)]
    for q in CELLS:
        col=COL.get(q,0)
        for k in range(3):m.Add(x[depth][q][k]==((col>>k)&1))
        for k,g in enumerate(gauge):m.Add(x[depth][q][3+k]==int(q in C and bool(g>>C.index(q)&1)))
        sig=[(col>>k)&1 for k in range(3)]+[int(q in B)]+[int(q==c) for c in C]
        for k,b in enumerate(sig):m.Add(h[depth][q][k]==b)
        if not source_zero:m.Add(x[0][q][3]==int(q==3))
    if not source_zero:
        for k in range(3):m.Add(x[0][3][k]==0)
    # Preserve the exact byproduct coset X_6*C2 on B. C's affine reference
    # bits are free outputs, permitting a jointly synthesized readout contract.
    if not source_zero:
        for support in list(f.SUPPORTS)+[set(range(7))]:
            m.AddBoolXOr([x[depth][B[i]][3] for i in support])
    def xor(z,a,b,lit):
        aux=m.NewIntVar(0,1,'')
        m.Add(z+a+b==2*aux).OnlyEnforceIf(lit)
    for t in range(depth):
        for q in CELLS:
            ins=[e for e in EDGES if e[1]==q];outs=[e for e in EDGES if e[0]==q]
            tin=m.NewBoolVar('');tout=m.NewBoolVar('')
            m.AddMaxEquality(tin,[sel[t][e] for e in ins]);m.AddMaxEquality(tout,[sel[t][e] for e in outs])
            for k in range(nx):
                m.Add(x[t][q][k]==x[t+1][q][k]).OnlyEnforceIf(tin.Not())
                for a,b in ins:xor(x[t][q][k],x[t+1][q][k],x[t+1][a][k],sel[t][a,b])
            for k in range(11):
                m.Add(h[t][q][k]==h[t+1][q][k]).OnlyEnforceIf(tout.Not())
                for a,b in outs:xor(h[t][q][k],h[t+1][q][k],h[t+1][b][k],sel[t][a,b])
    nz=[]
    for t in range(depth+1):
        row={q:m.NewBoolVar(f'nz{t}_{q}') for q in CELLS}
        for q in CELLS:m.AddMaxEquality(row[q],x[t][q])
        nz.append(row)
    m.Add(sum(nz[0].values())==nx)
    m.Add(nz[0][17]==1)
    if source_zero and 3 in CELLS and 0<=39-T0<depth:
        m.Add(use[39-T0][3]==0).OnlyEnforceIf(nz[0][3])
    for q in CELLS:m.Add(sum(use[t][q] for t in range(depth))>=1)
    alive=[]
    for t in range(depth+1):
        row={q:m.NewBoolVar(f'alive{t}_{q}') for q in CELLS}
        for q in CELLS:
            if t:m.AddMaxEquality(row[q],[use[s][q] for s in range(t)])
            else:m.Add(row[q]==0)
        alive.append(row)
    bads=[];unflagged=[]
    bad_s=[8]+list(range(1,8))  # nonzero syndrome with even parity, or logical X.
    gauge_span=[0]
    for g in gauge:gauge_span += [v^g for v in list(gauge_span)]
    def fault(sig,lit,weight=1):
        # s bits are syndrome[0:3], parity[3]; d is the literal C record.
        if f1:
            for offset in gauge_span:
                for bad in bad_s:
                    mismatch=[sig[4+j].Not() if offset>>j&1 else sig[4+j] for j in range(7)]
                    m.AddBoolOr([lit.Not()]+mismatch+[sig[k].Not() if bad>>k&1 else sig[k] for k in range(4)])
        if wbad:
            dangerous=m.NewBoolVar('danger')
            for offset in {v^(1<<c) for v in gauge_span for c in range(7)}:
                for bad in bad_s:
                    mismatch=[sig[k].Not() if bad>>k&1 else sig[k] for k in range(4)]
                    mismatch += [sig[4+j].Not() if offset>>j&1 else sig[4+j] for j in range(7)]
                    m.AddBoolOr([lit.Not(),dangerous]+mismatch)
            bads.append(weight*dangerous)
        if wunflag:
            risky=m.NewBoolVar('unflagged')
            for offset in gauge_span:
                mismatch=[sig[4+j].Not() if offset>>j&1 else sig[4+j] for j in range(7)]
                for k in range(4):m.AddBoolOr([lit.Not(),risky,sig[k].Not()]+mismatch)
            unflagged.append(weight*risky)
    for t in range(1,depth+1):
        for q in CELLS:fault(h[t][q],alive[t][q],2)
    for t in range(depth):
        for a,b in EDGES:
            if a>b:continue
            on=m.NewBoolVar('pair');m.AddMaxEquality(on,[sel[t][a,b],sel[t][b,a]])
            sig=[m.NewBoolVar('xx') for k in range(11)]
            for k in range(11):xor(sig[k],h[t+1][a][k],h[t+1][b][k],on)
            fault(sig,on,1)
    # Initial reset faults occur immediately before first use.
    for t in range(depth):
        for q in CELLS:
            first=m.NewBoolVar('first')
            m.AddBoolAnd([use[t][q],alive[t][q].Not()]).OnlyEnforceIf(first)
            m.AddBoolOr([use[t][q].Not(),alive[t][q],first])
            if not verified_init:fault(h[t][q],first,3)
    ncx=sum(v for row in sel for v in row.values())
    if cap is not None:m.Add(ncx<=cap)
    exposure=[]
    for t in range(depth+1):
        for q in CELLS:
            v=m.NewBoolVar('load');m.AddBoolAnd([nz[t][q],alive[t][q]]).OnlyEnforceIf(v)
            m.AddBoolOr([nz[t][q].Not(),alive[t][q].Not(),v]);exposure.append(v)
    badcount=sum(bads)
    riskcount=sum(unflagged)
    m.Minimize(wx*ncx+wz*sum(exposure)+wbad*badcount+wunflag*riskcount)
    if hint:
        for t,row in enumerate(sel):
            used={tuple(e) for e in hint['ops'][t]} if t<len(hint['ops']) else set()
            for e,v in row.items():m.AddHint(v,int(e in used))
        for q in CELLS:
            value=int(hint['pivots'].get(str(q),hint['pivots'].get(q,0)))
            for k,b in enumerate(x[0][q]):m.AddHint(b,(value>>k)&1)
        xr={q:int(hint['pivots'].get(str(q),hint['pivots'].get(q,0)))&((1<<nx)-1) for q in CELLS}
        for t in range(depth):
            for a,b in hint['ops'][t] if t<len(hint['ops']) else []:
                if (a,b) in EDGES:xr[b]^=xr[a]
            for q in CELLS:
                for k,v in enumerate(x[t+1][q]):m.AddHint(v,(xr[q]>>k)&1)
        hr={q:COL[q]|8 if q in B else 1<<(4+C.index(q)) for q in CELLS}
        for t in range(depth,-1,-1):
            for q in CELLS:
                for k,v in enumerate(h[t][q]):m.AddHint(v,(hr[q]>>k)&1)
            if t:
                for a,b in hint['ops'][t-1] if t-1<len(hint['ops']) else []:
                    if (a,b) in EDGES:hr[a]^=hr[b]
    return m,sel,x,ncx,badcount,riskcount

def solve(args):
    hint=json.loads(Path(args.hint).read_text()) if args.hint else None
    m,sel,x,ncx,badcount,riskcount=build(args.t0,args.depth,args.cap,args.wcx,args.wz,args.wbad,not args.no_f1,args.source_zero,hint,args.wunflag)
    s=cp_model.CpSolver();s.parameters.max_time_in_seconds=args.seconds;s.parameters.num_search_workers=args.workers;s.parameters.random_seed=args.seed
    s.parameters.log_search_progress=args.verbose
    status=s.Solve(m)
    out={'status':s.StatusName(status),'seconds':s.WallTime(),'T0':args.t0,'depth':args.depth,'seed':args.seed,'cap':args.cap,'wcx':args.wcx,'wz':args.wz,'wbad':args.wbad,'wunflag':args.wunflag,'f1':not args.no_f1,'source_zero':args.source_zero}
    if status in (cp_model.FEASIBLE,cp_model.OPTIMAL):
        out.update(ops=[[list(e) for e,v in row.items() if s.Value(v)] for row in sel],pivots={str(q):sum(s.Value(b)<<k for k,b in enumerate(x[0][q])) for q in CELLS},b_carry=[0 if args.source_zero else s.Value(x[args.depth][q][3]) for q in B],c_carry=[0 if args.source_zero else s.Value(x[args.depth][q][3]) for q in C],cx=s.Value(ncx),bad=s.Value(badcount),unflagged=s.Value(riskcount),objective=s.ObjectiveValue(),bound=s.BestObjectiveBound())
        stem,text=make(out,args.name);out['stem']=str(stem.relative_to(ROOT));out['raw']=raw_check(text,D)
        print('RAW',json.dumps(out['raw']),flush=True)
        if args.price and out['raw']['ok']:out['price']=price(stem,1,use_cache=False)
    (HERE/'sol').mkdir(exist_ok=True);(HERE/'sol'/f'{args.name}.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out),flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('name');ap.add_argument('--t0',type=int,default=30);ap.add_argument('--depth',type=int,default=17);ap.add_argument('--cap',type=int);ap.add_argument('--wcx',type=int,default=10);ap.add_argument('--wz',type=int,default=1);ap.add_argument('--wbad',type=int,default=20);ap.add_argument('--wunflag',type=int,default=0);ap.add_argument('--no-f1',action='store_true');ap.add_argument('--source-zero',action='store_true');ap.add_argument('--hint');ap.add_argument('--seconds',type=float,default=120);ap.add_argument('--workers',type=int,default=1);ap.add_argument('--seed',type=int,default=1);ap.add_argument('--price',action='store_true');ap.add_argument('--verbose',action='store_true');solve(ap.parse_args())
