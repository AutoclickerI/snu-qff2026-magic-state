"""Exhaustive CP-SAT feasible-neighborhood enumeration with the complete Stim objective.

No annealing. An OPTIMAL enumeration status certifies exhaustion only within the
declared Hamming neighborhood; this does not establish global proxy optimality.
"""
import argparse
import time
from common import *
from cpsat import Schedule,compact
from ortools.sat.python import cp_model

class Search(cp_model.CpSolverSolutionCallback):
    def __init__(self,sc,args):
        super().__init__(); self.sc=sc; self.args=args; self.g=g2.Model(EXTRAS)
        self.n=self.invalid=0; self.best=[]; self.start=time.time(); self.counts={}
    def on_solution_callback(self):
        a,o=self.sc.extract(self); p=self.g.cost(a,o); self.n+=1
        if p is None: self.invalid+=1; return
        if len(self.best)<self.args.top or p<self.best[-1][0]:
            row=encode(p,a,o,f'{self.args.tag}:{self.n}'); self.best.append(row); self.best.sort(key=lambda r:r[0]); self.best=self.best[:self.args.top]
            save(self.args.tag+'.json',self.best)
            if self.best[0] is row: print('BEST',self.n,p,o,'seconds',time.time()-self.start,flush=True)
        if self.n%1000==0: print('progress',self.n,'invalid',self.invalid,'best',self.best[0][0] if self.best else None,'seconds',time.time()-self.start,flush=True)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--file',default=str(BASE)); ap.add_argument('--idx',type=int,default=0)
    ap.add_argument('--lmax',type=int,default=8); ap.add_argument('--radius',type=int,default=3); ap.add_argument('--seconds',type=float,default=300); ap.add_argument('--tag',default='neighbor'); ap.add_argument('--top',type=int,default=50); ap.add_argument('--orientation-fixed',action='store_true'); ap.add_argument('--strong-validity',action='store_true'); ap.add_argument('--seed',type=int,default=0)
    ap.add_argument('--orientation',default=''); ap.add_argument('--phase',choices=['none','ZX','XZ'],default='none')
    args=ap.parse_args(); a,o=decode(json.load(open(args.file))[args.idx]); a=compact(a)
    sc=Schedule(args.lmax,(a,o)); changes=[]
    for k,v in sc.v.items():
        b=sc.model.new_bool_var(f'change{k}'); sc.model.add(v!=a[k]).only_enforce_if(b); sc.model.add(v==a[k]).only_enforce_if(~b); changes.append(b)
    if args.radius: sc.model.add(sum(changes)<=args.radius)
    if args.orientation: o=list(map(int,args.orientation)); args.orientation_fixed=True
    if args.orientation_fixed:
        for v,b in zip(sc.o,o): sc.model.add(v==b)
    if args.strong_validity:
        import validity
        validity.install(sc)
    if args.phase!='none':
        early=[sc.v[k] for k in sc.keys if k[2]==args.phase[0]]
        late=[sc.v[k] for k in sc.keys if k[2]==args.phase[1]]
        for x in early:
            for y in late: sc.model.add(x<y)
    solver=cp_model.CpSolver(); solver.parameters.num_search_workers=1; solver.parameters.enumerate_all_solutions=True
    solver.parameters.max_time_in_seconds=args.seconds; solver.parameters.random_seed=args.seed
    callback=Search(sc,args); status=solver.solve(sc.model,callback)
    summary=dict(status=solver.status_name(status),enumerated=callback.n,invalid=callback.invalid,best_proxy=callback.best[0][0] if callback.best else None,seconds=solver.wall_time,scope=dict(file=args.file,idx=args.idx,lmax=args.lmax,radius=args.radius,orientation_fixed=args.orientation_fixed,orientation=o if args.orientation_fixed else None,phase=args.phase,strong_validity=args.strong_validity),proxy_lower_bound=0 if status!=cp_model.OPTIMAL else callback.best[0][0] if callback.best else None)
    save(args.tag+'_summary.json',summary); print(summary,flush=True)

if __name__=='__main__': main()
