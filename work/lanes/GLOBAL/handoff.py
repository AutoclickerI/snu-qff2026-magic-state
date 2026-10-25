"""Retiming for a two-CX coherent output handoff into the B partner.

DB;BD = BD;SWAP, so relabel the measured partner and output after the pair.
The added DB gate occupies the flag data gap. B's C check must precede it.
"""
import argparse, copy, json, re
from pathlib import Path
from ortools.sat.python import cp_model
from qedit import load,QRE
from borrow import save,D,A,B,C,HERE

def info(g):
    qs=tuple(map(int,QRE.findall(g[0])))
    if g[0].startswith('cx'):kind='CX'
    elif g[0].startswith('h') and 'measure' in ' '.join(g):kind='MX'
    elif g[0].startswith('reset'):kind='RX' if len(g)>1 else 'R'
    else:kind=g[0].split()[0]
    return kind,qs

def commute(u,v):
    k,a=info(u);l,b=info(v)
    if not set(a)&set(b):return True
    if k==l=='CX':return a[0]!=b[1] and a[1]!=b[0]
    if k in ('t','tdg') and l=='CX':return a[0]==b[0]
    if l in ('t','tdg') and k=='CX':return b[0]==a[0]
    return False

def make(label,targets,drops=(),span=4,limit=45):
    c=load(str(HERE/'builds/v36h'))
    removed=[]
    for typ in drops:
        if typ.startswith('cx_'):
            _,a,b,t=typ.split('_');a,b,t=map(int,(a,b,t))
            g=next(g for g in c.segs[t] if g==[f'cx q[{a}],q[{b}];'])
            c.segs[t].remove(g);removed.append((t,g))
        elif typ.startswith('pair'):
            _,a,b,t=typ.split('_');a,b,t=map(int,(a,b,t))
            for tt in [t,t+1]:
                g=next(g for g in c.segs[tt] if g==[f'cx q[{a}],q[{b}];'])
                c.segs[tt].remove(g);removed.append((tt,g))
        elif typ=='late_guards':
            for h in [18,24,32,33]:
                for t in range(39,44):
                    for g in list(c.segs[t]):
                        if h in map(int,QRE.findall(' '.join(g))):
                            c.segs[t].remove(g);removed.append((t,g))
                            if 'measure' in ' '.join(g):
                                bit=int(re.findall(r'c\[(\d+)\]',' '.join(g))[0])
                                c.dets.remove(f'// DETECTOR c[{bit}]')
        else:raise ValueError(typ)
    us=[(t,g) for t,ss in enumerate(c.segs) for g in ss]
    m=cp_model.CpModel();ts=[];cost=[];bounds=[];edges=set()
    target_checks={tuple((B[i],C[i])) for i in targets}
    for i,(t,g) in enumerate(us):
        k,qs=info(g)
        lo=hi=t
        if 32<=t<=44 and not (k=='CX' and (set(qs)&set(D))):
            lo=max(0,t-span);hi=min(44,t+span)
        if (k,qs)==('CX',(14,15)) and t==45:lo=hi=t
        if k=='CX' and qs in target_checks and t==44:hi=43
        if k=='CX' and set(qs)<=set(A):lo=max(lo,t);hi=min(hi,t) # preserve the A encoder
        x=m.NewIntVar(lo,hi,f't{i}');ts.append(x)
        bounds.append((lo,hi))
        diff=m.NewIntVar(0,span+1,f'd{i}');m.AddAbsEquality(diff,x-t)
        ch=m.NewBoolVar(f'm{i}');m.Add(x==t).OnlyEnforceIf(ch.Not());m.Add(x!=t).OnlyEnforceIf(ch)
        cost.append(diff+3*ch)
    for q in range(36):
        idx=[i for i,(t,g) in enumerate(us) if q in info(g)[1]]
        m.AddAllDifferent([ts[i] for i in idx])
        for ii,i in enumerate(idx):
            for j in idx[ii+1:]:
                if not commute(us[i][1],us[j][1]):
                    m.Add(ts[i]<ts[j]);edges.add((i,j))
        if q in [D[i] for i in targets]+[B[i] for i in targets]:
            for i in idx:m.Add(ts[i]!=44)
    m.Minimize(sum(cost))
    s=cp_model.CpSolver();s.parameters.num_workers=6;s.parameters.max_time_in_seconds=limit
    status=s.Solve(m)
    out=dict(label=label,targets=targets,drops=drops,status=s.StatusName(status))
    early=[b[0] for b in bounds];parent={}
    for i in range(len(us)):
        for j in [b for a,b in edges if a==i]:
            if early[i]+1>early[j]:early[j]=early[i]+1;parent[j]=i
    violations=[i for i in range(len(us)) if early[i]>bounds[i][1]]
    if violations:
        z=violations[0];chain=[]
        while True:
            chain.append([us[z][0],early[z],us[z][1]])
            if z not in parent:break
            z=parent[z]
        out['critical_chain']=chain[::-1]
    if status in [cp_model.OPTIMAL,cp_model.FEASIBLE]:
        cc=copy.deepcopy(c);cc.segs=[[] for _ in c.segs]
        moved=[]
        for i,(t,g) in enumerate(us):
            tt=s.Value(ts[i]);cc.segs[tt].append(g)
            if tt!=t:moved.append([t,tt,g])
        desc=dict(family='coherent output handoff',removed=removed,moved=moved,targets=targets)
        save(cc,label+'_retime',desc)
        for i in targets:
            d,b=D[i],B[i]
            cc.segs[44].append([f'cx q[{d}],q[{b}];'])
            for t in range(46,len(cc.segs)):
                cc.segs[t]=[[QRE.sub(lambda mt:f'q[{d if int(mt[1])==b else b if int(mt[1])==d else int(mt[1])}]',ln) for ln in g] for g in cc.segs[t]]
        stem=save(cc,label,desc)
        meta=json.loads(stem.with_suffix('.json').read_text())
        meta['data_qubits']=[B[i] if i in targets else d for i,d in enumerate(D)]
        stem.with_suffix('.json').write_text(json.dumps(meta,indent=2)+'\n')
        out.update(moved=moved,removed=removed,objective=s.ObjectiveValue())
    (HERE/'logs'/f'{label}.solve.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out),flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('label');ap.add_argument('targets');ap.add_argument('--drops',default='');ap.add_argument('--span',type=int,default=4);ap.add_argument('--limit',type=float,default=45)
    args=ap.parse_args();make(args.label,list(map(int,args.targets.split(','))),args.drops.split(',') if args.drops else [],args.span,args.limit)
