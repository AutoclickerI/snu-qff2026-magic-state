"""Full non-Clifford noiseless/single-fault audit, no stim/xtim dependency.

Independent integer-Pauli walker + actual repository Engine AST.
Uses official judge noise_blocks/schedule with a native-op frontend.
No second/third-order or official Monte Carlo claims.
"""
import ast, sys, math, json, os
from pathlib import Path
from types import SimpleNamespace
from collections import Counter
from functools import lru_cache
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'audit'))
REPO=Path(os.environ['QUANTUMN_REPO']).resolve()
JUDGE=Path(os.environ.get('QUANTUMN_JUDGE',str(REPO/'upstream/snu-qff2026-problem'))).resolve()
sys.path.insert(0,str(JUDGE))
from tprep.noise import noise_blocks,schedule
DATA=[]

ns={'np':np,'math':math,'SQ2':math.sqrt(2),'Model':object}
for fname,names in [('model.py',{'Basis'}),('engine.py',{'Engine'})]:
    path=REPO/'work/lanes/EVAL'/fname
    body=[node for node in ast.parse(path.read_text()).body if isinstance(node,ast.ClassDef) and node.name in names]
    exec(compile(ast.Module(body=body,type_ignores=[]),str(path),'exec'),ns)
Engine=ns['Engine']
SUPPORTS=({0,2,4,6},{1,2,5,6},{3,4,5,6})

def mul(a,b):
    return (a[0]^b[0],a[1]^b[1],a[2]*b[2]*(-1)**((a[1]&b[0]).bit_count()))
def comm(a,b):return ((a[0]&b[1]).bit_count()+(a[1]&b[0]).bit_count())&1

def native_text(ops):
    lines=[];labels=[];lasttime=None
    for op in ops:
        name={'TDG':'T_DAG','ID':'I'}.get(op.kind,op.kind)
        line=name+' '+' '.join(map(str,op.qs))
        if op.time!=lasttime:
            line+=' # barrier '+' '.join(map(str,range(36)))
            lasttime=op.time
        lines.append(line);labels.append(op)
    return '\n'.join(lines),labels

def make_model(ops,dets):
    text,labels=native_text(ops)
    prog,blocks=noise_blocks(text,.001,first_order=True)
    _,steps,gaps=schedule(text)
    n=36+sum(len(ins.qubits) for ins in prog if ins.name in ('R','RX','M','MX'))
    xs=[(1<<i,0,1) for i in range(n)];zs=[(0,1<<i,1) for i in range(n)]
    wire=list(range(36));nxt=36;records={};rots=[];faults=[];chans=[]
    def cx(c,t):
        xs[c]=mul(xs[c],xs[t]);zs[t]=mul(zs[c],zs[t])
    def pull(P):
        x,z,coef=P;out=(0,0,coef)
        while x:
            bit=x&-x;x^=bit;out=mul(out,xs[bit.bit_length()-1])
        while z:
            bit=z&-z;z^=bit;out=mul(out,zs[bit.bit_length()-1])
        return out
    def physical(qs,pauli):
        x=z=0;co=1
        for q,P in zip(qs,pauli):
            if P in 'XY':x|=1<<wire[q]
            if P in 'YZ':z|=1<<wire[q]
            if P=='Y':co*=1j
        return x,z,co
    def channel(line,ii,jl):
        if '(' not in line:return
        head,rest=line.split(')',1);name,pr=head.split('(');pr=float(pr)
        qs=list(map(int,rest.split()));arity=2 if name=='DEPOLARIZE2' else 1
        comps={'X_ERROR':['X'],'Z_ERROR':['Z'],'DEPOLARIZE1':list('XYZ'),'DEPOLARIZE2':[a+b for a in 'IXYZ' for b in 'IXYZ' if a+b!='II']}[name]
        for k in range(0,len(qs),arity):
            grp=qs[k:k+arity];cid=len(chans)
            chans.append(dict(name=name,p=pr,qs=grp,ins=ii,jl=jl))
            for pauli in comps:
                x,z,co=pull(physical(grp,pauli))
                faults.append(dict(x=x,z=z,p=pr/len(comps),m=len(rots),chan=cid,pauli=pauli,qs=grp,ins=ii,jl=jl,label=f'{name} {pauli}@{grp} after/before native#{ii} srcL{labels[ii].line}'))
    for ii,(ins,block) in enumerate(zip(prog,blocks)):
        k=block.index(ins.text)
        for jl,line in enumerate(block[:k]):channel(line,ii,jl)
        name=ins.name;qs=ins.qubits
        if name in ('R','RX'):
            for q in qs:
                wire[q]=nxt;nxt+=1
                if name=='RX':xs[wire[q]],zs[wire[q]]=zs[wire[q]],xs[wire[q]]
        elif name in ('M','MX'):
            assert len(qs)==1
            q=qs[0];w=nxt;nxt+=1
            if name=='MX':xs[wire[q]],zs[wire[q]]=zs[wire[q]],xs[wire[q]]
            cx(wire[q],w)
            if name=='MX':xs[wire[q]],zs[wire[q]]=zs[wire[q]],xs[wire[q]]
            records[labels[ii].bit]=w
        elif name=='CX':cx(*[wire[q] for q in qs])
        elif name=='H':
            for q in qs:xs[wire[q]],zs[wire[q]]=zs[wire[q]],xs[wire[q]]
        elif name in ('T','T_DAG'):
            for q in qs:
                x,z,co=zs[wire[q]]
                rots.append((x,z,co,(-1 if name=='T' else 1)*math.pi/8,ii))
        elif name!='I':raise ValueError(name)
        for jl in range(k+1,len(block)):channel(block[jl],ii,jl)
    assert nxt==n
    def par(bits):
        z=0
        for bit in bits:z^=1<<records[bit]
        return 0,z,1
    proj=[pull(par(row)) for row in dets]
    gens=[physical([DATA[i] for i in sorted(S)],P*len(S)) for P in 'XZ' for S in SUPPORTS]
    X7=physical(DATA,'X'*7);Z7=physical(DATA,'Z'*7);Y7=physical(DATA,'Y'*7)
    sig=[pull(g) for g in gens]+[pull(X7),pull(Z7),(0,0,1),(0,0,1)]
    Q={}
    for T,L in [('X',X7),('Y',Y7)]:
        for a in range(8):
            for b in range(8):
                if T=='X' and b:continue
                ps=(0,0,1)
                for i,g in enumerate(gens):
                    if (a|(b<<3))>>i&1:ps=mul(ps,g)
                Q[T,a,b]=pull(mul(ps,L))
    for f in faults:
        F=(f['x'],f['z'])
        f['s']=sum(comm(F,r)<<j for j,r in enumerate(rots) if j>=f['m'])
        f['d']=sum(comm(F,v)<<j for j,v in enumerate(proj))
        f['e']=sum(comm(F,v)<<j for j,v in enumerate(sig))
    model=SimpleNamespace(rots=rots,proj_m=proj,Q=Q,cz=0,cxz=0,proj_v=[None]*len(proj),n_post=0,faults=faults,chans=chans)
    model.gen_m=[pull(g) for g in gens];model.native=text;model.steps=steps;model.labels=labels;model.dets=dets
    model.record_ps={bit:pull((0,1<<w,1)) for bit,w in records.items()}
    for f in faults:
        F=(f['x'],f['z'])
        f['record_flips']=[bit for bit,P in model.record_ps.items() if comm(F,P)]
    return model
