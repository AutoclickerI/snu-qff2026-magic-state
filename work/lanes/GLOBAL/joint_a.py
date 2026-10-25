"""Joint A-encoder / late controlled-X-check synthesis, borrowing live role cells.

Track four independent A preparation bits and their induced X actions on D.
Each induced data action must be a Steane X stabilizer. The A flag must read
a nonzero specified X stabilizer in addition to its original preparation flag.
"""
import argparse,copy,json,sys
from pathlib import Path
from ortools.sat.python import cp_model
from qedit import load,QRE,CRE
from borrow import HERE,save,D,A

HS=[85,102,120];ROWS=HS+[7]
REL={1:(35,'Z'),14:(33,'X'),8:(35,'Z'),9:(37,'Z'),2:(35,'X'),16:(37,'Z'),15:(39,'Z')}
DA={q:(43 if q in [9,15] else 44) for q in A}
ORIG=[(37,8,2),(38,2,1),(38,14,8),(39,1,2),(39,9,8),(40,8,2),(40,9,15),(41,8,9),(41,16,15),(42,9,8),(42,15,14),(43,14,8)]

def exterior():
    c=load(str(HERE/'builds/v36h'));removed=[]
    for t,ss in enumerate(c.segs):
        for g in list(ss):
            qs=tuple(map(int,QRE.findall(g[0])));k=g[0].split()[0]
            drop=(k=='cx' and (t,*qs) in ORIG) or (k=='reset' and (t,qs[0]) in [(36,8),(36,2),(38,9),(38,16)])
            drop |= (k=='cx' and qs==(6,7) and 37<=t<=41)
            drop |= (k=='cx' and ((t,qs) in [(32,(13,14)),(39,(10,16))] or (qs==(20,14) and t in [40,41])))
            drop |= any('-> c[278];' in l for l in g)
            if drop:ss.remove(g);removed.append([t,g])
    c.dets.remove('// DETECTOR c[278]')
    for old,new,g in [(36,32,['cx q[14],q[20];'])]:c.segs[old].remove(g);c.segs[new].append(g)
    for bit,tt in [(12,33),(64,35)]:
        (t,j),=c.find(lambda g:any(f'-> c[{bit}];' in l for l in g));c.move(t,j,tt)
    for q,tt in [(10,35),(20,36)]:
        (t,j),=c.find(lambda g:g[0]==f'tdg q[{q}];');c.move(t,j,tt)
    return c,removed

def solve(name,smask,seconds,workers,seed,allowdrop=False,near=3):
    c,removed=exterior();T0,T1=33,44;depth=T1-T0
    m=cp_model.CpModel();one=m.NewConstant(1)
    def xor_eq(z,terms):m.AddBoolXOr([z,*terms,one])
    def product(a,b):
        z=m.NewBoolVar('');m.AddMultiplicationEquality(z,[a,b]);return z
    piv={(q,j):m.NewBoolVar(f'p{q}_{j}') for q in A for j in range(4)}
    nz={q:m.NewBoolVar(f'pivot{q}') for q in A}
    for j in range(4):m.AddExactlyOne(piv[q,j] for q in A)
    for q in A:m.Add(sum(piv[q,j] for j in range(4))==nz[q])
    x=[{(q,j):piv[q,j] for q in A for j in range(4)}]
    y=[{(i,j):m.NewConstant(0) for i in range(7) for j in range(4)}]
    E=[(a,b) for a in A for b in A if abs(a//6-b//6)+abs(a%6-b%6)==1]
    X=[(a,d) for a in A for d in D if abs(a//6-d//6)+abs(a%6-d%6)==1]
    ins=[];adds=[];allused={q:[] for q in A};drops={q:m.NewBoolVar(f'drop{q}') for q in A}
    for q in A:
        if not allowdrop:m.Add(drops[q]==0)
    for t in range(T0,T1):
        si={e:m.NewBoolVar(f'e{t}_{e}') for e in E};ad={e:m.NewBoolVar(f'c{t}_{e}') for e in X};ins.append(si);adds.append(ad)
        for q in A:
            inc=[si[e] for e in E if q in e]+[ad[e] for e in X if e[0]==q]
            m.AddAtMostOne(inc)
            u=m.NewBoolVar('');m.AddMaxEquality(u,inc);allused[q].append(u)
            rel,basis=REL[q]
            if t<rel:m.Add(u==0)
            elif t==rel:
                m.AddImplication(u,drops[q]);m.Add(nz[q]==int(basis=='X')).OnlyEnforceIf(u)
            elif t==rel+1:
                # Reuse the release measurement, or replace it by a reset if its check is dropped.
                m.Add(nz[q]==int(basis=='X')).OnlyEnforceIf([u,drops[q].Not()])
            if t>=DA[q]:m.Add(u==0)
        for d in D:
            possible=[ad[e] for e in X if e[1]==d];m.AddAtMostOne(possible)
            busy=d in c.qubits_at(t)
            after={0:30,20:36,7:29,10:35,3:33,22:37,21:38}[d]
            if busy or t<=after:
                for v in possible:m.Add(v==0)
        xn={};yn={}
        for q in A:
            for j in range(4):
                xn[q,j]=m.NewBoolVar('');xor_eq(xn[q,j],[x[-1][q,j]]+[product(si[a,b],x[-1][a,j]) for a,b in E if b==q])
        for i,d in enumerate(D):
            for j in range(4):
                yn[i,j]=m.NewBoolVar('');xor_eq(yn[i,j],[y[-1][i,j]]+[product(ad[a,dd],x[-1][a,j]) for a,dd in X if dd==d])
        x.append(xn);y.append(yn)
    change={};coeff={}
    for j in range(4):
        for k in range(4):change[j,k]=m.NewBoolVar('')
        for k in range(3):coeff[j,k]=m.NewBoolVar('')
        for i,q in enumerate(A):
            xor_eq(x[-1][q,j],[change[j,k] for k,row in enumerate(ROWS) if row>>i&1])
            xor_eq(y[-1][i,j],[coeff[j,k] for k,row in enumerate(HS) if row>>i&1])
    u=[m.NewBoolVar(f'flagbit{j}') for j in range(4)]
    flag=(1<<2)|(1<<3)|(1<<6)
    for i,q in enumerate(A):
        xor_eq(m.NewConstant((flag>>i)&1),[product(u[j],x[-1][q,j]) for j in range(4)])
        xor_eq(m.NewConstant((smask>>i)&1),[product(u[j],y[-1][i,j]) for j in range(4)])
    nadd=sum(v for row in adds for v in row.values());ncx=sum(v for row in ins for v in row.values())
    m.Add(nadd>=4);m.Add(nadd<=10);m.Add(ncx<=16)
    original=set(ORIG);dist=sum(1-v if (t+T0,*e) in original else v for t,row in enumerate(ins) for e,v in row.items())
    m.Minimize(near*dist+3*ncx+2*nadd+8*sum(drops.values()))
    s=cp_model.CpSolver();s.parameters.max_time_in_seconds=seconds;s.parameters.num_workers=workers;s.parameters.random_seed=seed
    st=s.Solve(m);out=dict(name=name,status=s.StatusName(st),seconds=s.WallTime(),support=smask,seed=seed,allowdrop=allowdrop)
    if st in [cp_model.FEASIBLE,cp_model.OPTIMAL]:
        ops=[(t+T0,a,b) for t,row in enumerate(ins) for (a,b),v in row.items() if s.Value(v)]
        extra=[(t+T0,a,b) for t,row in enumerate(adds) for (a,b),v in row.items() if s.Value(v)]
        first={q:min(t for t,a,b in ops+extra if q==a or (q==b and b in A)) for q in A}
        inits={};dropped=[]
        for q,t in first.items():
            rel,basis=REL[q];plus=bool(s.Value(nz[q]));need='X' if plus else 'Z'
            if t<=rel+1 and need==basis:
                if t==rel:
                    g=next(g for g in c.segs[rel] if any('measure' in ln for ln in g) and q in map(int,QRE.findall(g[0])))
                    bit=int(CRE.findall(' '.join(g))[0]);c.segs[rel].remove(g);c.dets.remove(f'// DETECTOR c[{bit}]');dropped.append(bit)
                inits[q]=dict(kind='reuse',time=rel)
            else:
                tt=t-1
                if tt==rel:
                    g=next(g for g in c.segs[rel] if any('measure' in ln for ln in g) and q in map(int,QRE.findall(g[0])))
                    bit=int(CRE.findall(' '.join(g))[0]);c.segs[rel].remove(g);c.dets.remove(f'// DETECTOR c[{bit}]');dropped.append(bit)
                c.segs[tt].append([f'reset q[{q}];']+([f'h q[{q}];'] if plus else []));inits[q]=dict(kind='RX' if plus else 'R',time=tt)
        for t,a,b in ops+extra:c.segs[t].append([f'cx q[{a}],q[{b}];'])
        out.update(A_ops=ops,extra=extra,inits=inits,dropped=dropped,objective=s.ObjectiveValue(),bound=s.BestObjectiveBound(),flag_initial_bits=[s.Value(z) for z in u])
        stem=save(c,name,dict(family='joint A encoder and X check',**out))
        # Verify every selected real-grid edge and collision before any evaluator call.
        for ss in c.segs:
            for g in ss:
                if g[0].startswith('cx'):
                    a,b=map(int,QRE.findall(g[0]));assert abs(a//6-b//6)+abs(a%6-b%6)==1
        out['stem']=str(stem)
    (HERE/'layouts'/f'{name}.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out),flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('name');ap.add_argument('mask',type=int);ap.add_argument('--seconds',type=float,default=180);ap.add_argument('--workers',type=int,default=8);ap.add_argument('--seed',type=int,default=1);ap.add_argument('--drop',action='store_true');ap.add_argument('--near',type=int,default=3);a=ap.parse_args();solve(a.name,a.mask,a.seconds,a.workers,a.seed,a.drop,a.near)
