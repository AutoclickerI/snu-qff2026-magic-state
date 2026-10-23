"""Scheduling constraints shared by unrestricted and order-fixed models."""
from common import *
from ortools.sat.python import cp_model

class Schedule:
    def __init__(self, lmax, seed=None, fixed_order=False):
        self.lmax=lmax; self.model=cp_model.CpModel(); c=self.model
        self.g=g2.Model(EXTRAS); self.keys=self.g.keys
        self.v={k:c.new_int_var(2,lmax,str(k)) for k in self.keys}
        self.o=[c.new_bool_var('orientation_'+str(t)) for t in range(3)]
        self.end=c.new_int_var(2,lmax,'last_layer'); c.add_max_equality(self.end,list(self.v.values()))
        self.on={}
        for k,v in self.v.items():
            for L in range(2,lmax+1):
                b=c.new_bool_var(f'{k}@{L}'); c.add(v==L).only_enforce_if(b); c.add(v!=L).only_enforce_if(~b)
                self.on[k,L]=b
        for L in range(2,lmax+1):
            active=c.new_bool_var(f'layer_used{L}'); c.add(self.end>=L).only_enforce_if(active); c.add(self.end<L).only_enforce_if(~active)
            c.add(sum(self.on[k,L] for k in self.keys)>=1).only_enforce_if(active)
        self.perq={}
        for k in self.keys:
            for q in self.g.qubits_of(k,[0,0,0]): self.perq.setdefault(q,[]).append(k)
        for qs in self.perq.values(): c.add_all_different([self.v[k] for k in qs])
        for t in range(3):
            u=self.v[t,'U','']; m=g2.TILES[t][0]; n=(m[0]+1,m[1])
            for k,v in self.v.items():
                if k[0]!=t or k[1]=='U': continue
                q=self.g.qubits_of(k,[0,0,0])[0]
                if q not in (m,n): continue
                # After U: attachment parent must be X-reader; data type must match reader.
                want_x=k[1]=='A' or k[2]=='X'
                allowed_orientation=int((q==n)==want_x)
                # q==m and X -> orientation0; q==n and X -> orientation1.
                disallowed=self.o[t] if allowed_orientation==0 else ~self.o[t]
                c.add(v<u).only_enforce_if(disallowed)
        for t,q,parent,ds in self.g.extras:
            for d in ds: c.add(self.v[t,'A',q]<self.v[t,d,'X'])
            for tt,qq,pp,_ in self.g.extras:
                if pp==q: c.add(self.v[t,'A',q]<self.v[tt,'A',qq])
        for ta,(_,da) in enumerate(g2.TILES):
            for tb,(_,db) in enumerate(g2.TILES):
                terms=[]
                for d in set(da)&set(db):
                    b=c.new_bool_var(f'parity_{ta}_{tb}_{d}')
                    c.add(self.v[ta,d,'X']<self.v[tb,d,'Z']).only_enforce_if(b)
                    c.add(self.v[ta,d,'X']>=self.v[tb,d,'Z']).only_enforce_if(~b); terms.append(b)
                c.add(sum(terms)==2*c.new_int_var(0,len(terms)//2,f'even_{ta}_{tb}'))
        if seed:
            a,o=seed
            for k,v in self.v.items(): c.add_hint(v,a[k])
            for v,b in zip(self.o,o): c.add_hint(v,b)
            if fixed_order:
                for q,ks in self.perq.items():
                    seq=sorted(ks,key=a.__getitem__)
                    for ka,kb in zip(seq,seq[1:]): c.add(self.v[ka]<self.v[kb])
                for v,b in zip(self.o,o): c.add(v==b)

    def extract(self, solver):
        return {k:solver.value(v) for k,v in self.v.items()}, [solver.value(v) for v in self.o]

    def forbid(self,a,o):
        self.model.add_forbidden_assignments(list(self.v.values())+self.o, [[a[k] for k in self.keys]+list(o)])

    def solve(self,seconds=30,workers=8,seed=0):
        s=cp_model.CpSolver(); s.parameters.num_search_workers=workers
        if getattr(self,'disable_presolve',False): s.parameters.cp_model_presolve=False
        s.parameters.max_time_in_seconds=seconds; s.parameters.random_seed=seed
        status=s.solve(self.model)
        return s,status

def compact(a):
    levels={v:i+2 for i,v in enumerate(sorted(set(a.values())))}
    return {k:levels[v] for k,v in a.items()}
