"""Unrestricted CP-SAT schedules driven by a data-only tail objective, then exact oracle.

This objective includes pure-data CNOT fault components and late idle components;
it excludes ancilla faults and partial windows. It is a search objective, not a
certificate for the complete proxy. ordered_objective.py supplies the complete
objective and certificates within each sampled gate-order class.
"""
import argparse
import time
from collections import defaultdict
from itertools import combinations
from common import *
from cpsat import Schedule, compact
from ordered_objective import A1,A2,AR,SCALE
import bounds

def install_tail(sc, extras=False):
    c=sc.model; v=sc.v; lmax=sc.lmax
    masses={}; pub={}
    for d in sorted({k[1] for k in sc.keys if isinstance(k[1],tuple)}):
        ks=[k for k in sc.keys if k[1]==d]
        for P in 'XYZ':
            catching=[v[k] for k in ks if (P in 'ZY' and k[2]=='X') or (P in 'XY' and k[2]=='Z')]
            last=c.new_int_var(2,lmax,f'last{d}{P}'); c.add_max_equality(last,catching)
            after=[]
            for k in ks:
                b=c.new_bool_var(f'after{d}{P}{k}'); c.add(v[k]>last).only_enforce_if(b); c.add(v[k]<=last).only_enforce_if(~b); after.append(b)
            extra_idle=[]; extra_gates=[]; extra_reset=[]
            if extras:
                for t,q,parent,ds in sc.g.extras:
                    if d not in ds:continue
                    assert len(ds)==1
                    served=v[t,d,'X'];attach=v[t,'A',q]
                    survives=c.new_bool_var(f'extra_survives{d}{P}')
                    c.add(served>=last).only_enforce_if(survives);c.add(served<last).only_enforce_if(~survives)
                    # Extra is read in X immediately after this last CNOT. The ancilla-X
                    # component paired with the data Pauli is another invisible component.
                    extra_gates.append(survives)
                    if P=='X':
                        idle=c.new_int_var(0,lmax,f'extra_idle{d}')
                        c.add(idle==served-attach-1).only_enforce_if(survives);c.add(idle==0).only_enforce_if(~survives)
                        extra_idle.append(idle);extra_gates.append(survives);extra_reset.append(survives)
            gmax=len(ks)+len(extra_gates);imax=lmax*(1+len(extra_idle));rmax=len(extra_reset)
            ng=c.new_int_var(1,gmax,f'ng{d}{P}'); c.add(ng==1+sum(after)+sum(extra_gates))
            ni=c.new_int_var(1,imax,f'ni{d}{P}'); c.add(ni==sc.end-last+1-sum(after)+sum(extra_idle))
            nr=c.new_int_var(0,rmax,f'nr{d}{P}');c.add(nr==sum(extra_reset))
            rows=[(i,g,r,round(SCALE*(1-A1**i*A2**g*AR**r)/2)) for i in range(1,imax+1) for g in range(1,gmax+1) for r in range(rmax+1)]
            ub=max(row[3] for row in rows); p=c.new_int_var(0,ub,f'mass{d}{P}')
            c.add_allowed_assignments([ni,ng,nr,p],rows); masses[d,P]=p; pub[d,P]=ub
    terms=[]
    for d,e in combinations(sorted({k[0] for k in masses}),2):
        for P in 'XYZ':
            for Q in 'XYZ':
                w=round(2*bounds.cost(P,Q))
                if w:
                    term=c.new_int_var(0,pub[d,P]*pub[e,Q],f'product{d}{P}{e}{Q}')
                    c.add_multiplication_equality(term,[masses[d,P],masses[e,Q]]); terms.append(w*term)
    c.minimize(sum(terms))

def order_key(a,o):
    m=g2.Model(EXTRAS); per={}
    for k in m.keys:
        for q in m.qubits_of(k,o): per.setdefault(q,[]).append(k)
    return str((tuple(o),tuple((q,tuple(sorted(ks,key=a.__getitem__))) for q,ks in sorted(per.items()))))

def forbid_order(sc,a,o):
    lits=[]; c=sc.model
    for v,oi in zip(sc.o,o): lits.append(v if oi==0 else ~v)
    for q,ks in sc.perq.items():
        seq=sorted(ks,key=a.__getitem__)
        for x,y in zip(seq,seq[1:]):
            b=c.new_bool_var(f'ordercut{len(c.proto.variables)}')
            c.add(sc.v[x]>sc.v[y]).only_enforce_if(b); c.add(sc.v[x]<sc.v[y]).only_enforce_if(~b)
            lits.append(b)
    c.add_bool_or(lits)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--lmax',type=int,default=8); ap.add_argument('--count',type=int,default=40)
    ap.add_argument('--seconds',type=float,default=15); ap.add_argument('--tag',default='global8'); ap.add_argument('--workers',type=int,default=8)
    ap.add_argument('--phase',choices=['none','ZX','XZ'],default='none')
    ap.add_argument('--radius',type=int,default=0)
    ap.add_argument('--extras-tail',action='store_true')
    args=ap.parse_args(); a,o=baseline(); a=compact(a)
    sc=Schedule(args.lmax,(a,o)); install_tail(sc,args.extras_tail)
    import validity
    validity.install(sc)
    if args.phase!='none':
        early=[sc.v[k] for k in sc.keys if k[2]==args.phase[0]]
        late=[sc.v[k] for k in sc.keys if k[2]==args.phase[1]]
        for x in early:
            for y in late: sc.model.add(x<y)
    if args.radius:
        changes=[]
        for k,v in sc.v.items():
            b=sc.model.new_bool_var(f'change{k}'); sc.model.add(v!=a[k]).only_enforce_if(b); sc.model.add(v==a[k]).only_enforce_if(~b); changes.append(b)
        sc.model.add(sum(changes)<=args.radius)
    m=g2.Model(EXTRAS)
    results=[]; runs=[]
    for n in range(args.count):
        start=time.time(); solver,status=sc.solve(args.seconds,args.workers,n)
        run=dict(n=n,status=solver.status_name(status),bound=solver.best_objective_bound/(2*SCALE**2),seconds=time.time()-start)
        if status not in (2,4): runs.append(run); print(run,flush=True); break
        aa,oo=sc.extract(solver); val=m.cost(aa,oo)
        run.update(objective=solver.objective_value/(2*SCALE**2),proxy=val,orientation=oo)
        results.append(encode(val,aa,oo,n)); runs.append(run)
        print(run,flush=True); save(args.tag+'.json',results); save(args.tag+'_runs.json',runs)
        # The fault signatures are invariant under retiming with the same per-qubit order.
        # Exclude the whole invalid/previous order class to search distinct circuits.
        forbid_order(sc,aa,oo)
        sc.model.clear_hints()
        for k,v in sc.v.items(): sc.model.add_hint(v,aa[k])
        for v,b in zip(sc.o,oo): sc.model.add_hint(v,b)

if __name__=='__main__': main()
