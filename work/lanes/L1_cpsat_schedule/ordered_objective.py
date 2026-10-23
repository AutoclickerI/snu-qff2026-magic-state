"""Full finite-noise DEM proxy for a fixed per-qubit CNOT order.

Each independent Pauli component contributes to one detector/observable signature.
For signature g the merged mass is (1 - a1**n1 * a2**n2 * ar**nr)/2,
where a1=sqrt(1-4p/3), a2=(1-16p/15)**(1/8), ar=1-2p.
n1 is affine in waiting times; n2,nr are fixed by the gate order.
All equal-signature pairs, including non-empty detector signatures, are included.
"""
from collections import defaultdict
from itertools import combinations
import math
import stim
from common import *
from cpsat import Schedule, compact

P=1e-3
SCALE=10**9
A1=math.sqrt(1-4*P/3)
A2=(1-16*P/15)**(1/8)
AR=1-2*P

def addexpr(a,b,factor=1):
    out=dict(a)
    for k,v in b.items(): out[k]=out.get(k,0)+factor*v
    return {k:v for k,v in out.items() if v}

def evaluate(expr,a):
    return sum(v*(1 if k=='const' else max(a.values()) if k=='end' else a[k]) for k,v in expr.items())

def signature(terms):
    det=obs=0
    for x in terms:
        t=x.dem_target if hasattr(x,'dem_target') else x
        if t.is_relative_detector_id(): det^=1<<t.val
        elif t.is_logical_observable_id(): obs^=1<<t.val
    return det,obs

class OrderedObjective:
    def __init__(self,a,o):
        self.a=compact(a); self.o=o; a=self.a; m=g2.Model(EXTRAS)
        c=Circ(); c.g('id',*proxy2.DATA); m.emit(c,a,o)
        bit_check={b:t if B=='X' else t+3 for (t,B),bs in m.checks.items() for b in bs}
        c.detectors=[]; c=c.rescheduled(lazy_init=True)
        ops=[op for op in c.sops if op[0]!='barrier']
        # Assign symbolic operation times. Core Bell preparation precedes every schedule op.
        labels=[]; bell_seen=set()
        q_to_xy={g2.P(q):q for k in m.keys for q in m.qubits_of(k,o)}
        cx_lookup={}
        for k in m.keys:
            t,d,typ=k
            if d=='U': qs=g2.g1.readers(t,o)
            elif d=='A': qs=m.qubits_of(k,o)
            elif typ=='X': qs=(m.anc(t,d,typ),d)
            else: qs=(d,m.anc(t,d,typ))
            cx_lookup[tuple(map(g2.P,qs))]=k
        core_bells={tuple(map(g2.P,(xy,(xy[0]+1,xy[1])))) for xy,_ in g2.TILES}
        for kind,qs,b in ops:
            if kind=='cx':
                if qs in core_bells and qs not in bell_seen:
                    bell_seen.add(qs); labels.append({'const':2})
                else: labels.append({cx_lookup[qs]:1,'const':1})
            elif kind=='g:id': labels.append({})
            elif kind in ('R','RX'):
                extra=next((k for k in m.keys if k[1]=='A' and g2.P(k[2])==qs[0]),None)
                labels.append({extra:1} if extra else {'const':1})
            elif kind in ('M','MX'):
                q=q_to_xy[qs[0]]; last=max((k for k in m.keys if q in m.qubits_of(k,o)),key=a.__getitem__)
                labels.append({last:1,'const':2})
            else: raise AssertionError(kind)
        # All possible idle gaps, even gaps currently zero, are represented in the template.
        next_on={}; gaps={}
        for i in range(len(ops)-1,-1,-1):
            kind,qs,b=ops[i]
            for q in qs:
                j=next_on.get(q)
                if j is not None and ops[j][0] not in ('R','RX'):
                    expr=addexpr(addexpr(labels[j],labels[i],-1),{'const':-1})
                elif j is None and kind not in ('M','MX'):
                    expr=addexpr({'end':1,'const':2},labels[i],-1)
                else: expr={}
                if expr: gaps[i,q]=expr
                next_on[q]=i
        channels={}; noisy=stim.Circuit(); bits=[]; seen=set()
        def noise(name,qs,expr=None):
            tag=str(len(channels)); channels[tag]=(name,expr)
            noisy.append(name,qs,P,tag=tag)
        for i,(kind,qs,b) in enumerate(ops):
            fresh=[q for q in qs if q not in seen]; seen.update(qs)
            if fresh and kind not in ('R','RX'):
                for q in fresh: noise('X_ERROR',[q])
            if kind in ('M','MX'):
                for q in qs: noise('X_ERROR' if kind=='M' else 'Z_ERROR',[q])
                bits.append(b)
            name={'g:id':'I','cx':'CX'}.get(kind,kind)
            noisy.append(name,qs)
            if kind in ('R','RX'):
                for q in qs: noise('X_ERROR' if kind=='R' else 'Z_ERROR',[q])
            elif kind=='cx': noise('DEPOLARIZE2',qs)
            else:
                for q in qs: noise('DEPOLARIZE1',[q],{'const':1})
            for q in qs:
                if (i,q) in gaps: noise('DEPOLARIZE1',[q],gaps[i,q])
        self.channels=channels; self.noisy=noisy
        summaries=[]
        for logical in ('X','Z'):
            circ=m._full(str(noisy),bits,bit_check,logical)
            grouped={}
            for err in circ.explain_detector_error_model_errors():
                sig=signature(err.dem_error_terms); expr={}; n2=nr=0
                for loc in err.circuit_error_locations:
                    name,e=channels[loc.noise_tag]
                    if name=='DEPOLARIZE1': expr=addexpr(expr,e)
                    elif name=='DEPOLARIZE2': n2+=1
                    else: nr+=1
                grouped[sig]=(expr,n2,nr)
            summaries.append(grouped)
        self.basis_groups={}
        for basis,g in enumerate(summaries):
            for (d,s),(expr,n2,nr) in g.items():
                self.basis_groups.setdefault((d,s&63),[[],[]])[basis].append((s>>6,expr,n2,nr))
        self.general=any(len(a)!=1 or len(b)!=1 or a[0][1:]!=b[0][1:] for a,b in self.basis_groups.values())
        if self.general:
            self.mech=[]; self.pairs=[]; self.first=[]
            return
        # Fast path for unambiguous matched mechanisms.
        A,B=[{(d,s&63):(s>>6,expr,n2,nr) for (d,s),(expr,n2,nr) in g.items()} for g in summaries]
        assert len(A)==len(summaries[0]) and len(B)==len(summaries[1]), 'ambiguous mechanism mapping'
        assert A.keys()==B.keys(), 'unmatched mechanism mapping'
        self.mech=[]
        for k in sorted(A):
            fa,expr,n2,nr=A[k]; fb,expr_b,n2b,nrb=B[k]
            assert (expr,n2,nr)==(expr_b,n2b,nrb)
            self.mech.append((*k,fa,fb,expr,n2,nr))
        self.pairs=[]; self.first=[]
        for i,(d,s,fa,fb,*_) in enumerate(self.mech):
            if d==0 and (w:=self.weight(s,fa,fb)): self.first.append((i,w))
            for j in range(i):
                dd,ss,aa,bb,*_=self.mech[j]
                if d==dd and (w:=self.weight(s^ss,fa^aa,fb^bb)): self.pairs.append((i,j,w))

    @staticmethod
    def weight(s,fa,fb):
        fx=fa^bool(s&7); fz=fb^bool(s&56)
        return 2 if fx and not fz else 1 if fz else 0

    def masses(self,a):
        return [(1-A1**evaluate(e,a)*A2**n2*AR**nr)/2 for d,s,fa,fb,e,n2,nr in self.mech]

    def value(self,a):
        if self.general:
            groups=defaultdict(list)
            for (d,s),(la,lb) in self.basis_groups.items():
                vals=[]
                for side in (la,lb):
                    vals.append(sorted([((1-A1**evaluate(e,a)*A2**n2*AR**nr)/2,f) for f,e,n2,nr in side],reverse=True))
                for i in range(max(map(len,vals))):
                    pa,fa=vals[0][i] if i<len(vals[0]) else (0,0)
                    pb,fb=vals[1][i] if i<len(vals[1]) else (0,0)
                    groups[d].append((s,max(pa,pb),fa,fb))
            value=0
            for d,gl in groups.items():
                for i,(s,p,fa,fb) in enumerate(gl):
                    if d==0:value+=p*self.weight(s,fa,fb)/2
                    for ss,pp,aa,bb in gl[:i]: value+=p*pp*self.weight(s^ss,fa^aa,fb^bb)/2
            return value
        ps=self.masses(a)
        return sum(ps[i]*w/2 for i,w in self.first)+sum(ps[i]*ps[j]*w/2 for i,j,w in self.pairs)

    def install(self,schedule):
        # OR-Tools 9.15's presolve falsely declares some of these large integer
        # element/product models infeasible. A feasible fixed assignment and a
        # no-presolve optimum are retained in solver_diagnosis.log and the pbtxt.
        schedule.disable_presolve=True
        if self.general:return self._install_general(schedule)
        c=schedule.model; v=schedule.v; end=schedule.end; lmax=schedule.lmax
        probs=[]; ubs=[]; error_bound=0
        for idx,(d,s,fa,fb,e,n2,nr) in enumerate(self.mech):
            lb=ub=e.get('const',0)
            for k,z in e.items():
                if k=='const': continue
                lb+=z*(2 if z>0 else lmax); ub+=z*(lmax if z>0 else 2)
            lb=max(0,lb); ub=max(lb,ub)
            cnt=c.new_int_var(lb,ub,f'count_{idx}')
            c.add(cnt==sum(z*(1 if k=='const' else end if k=='end' else v[k]) for k,z in e.items()))
            table=[round(SCALE*(1-A1**n*A2**n2*AR**nr)/2) for n in range(lb,ub+1)]
            pvar=c.new_int_var(min(table),max(table),f'prob_{idx}')
            c.add_element(cnt-lb,table,pvar); probs.append(pvar); ubs.append(max(table))
        terms=[]
        for i,w in self.first: terms.append(probs[i]*(w*SCALE)); error_bound+=w/(4*SCALE)
        for n,(i,j,w) in enumerate(self.pairs):
            prod=c.new_int_var(0,ubs[i]*ubs[j],f'pair_{n}')
            c.add_multiplication_equality(prod,[probs[i],probs[j]]); terms.append(w*prod)
            error_bound+=w/2*((ubs[i]+ubs[j])/(2*SCALE**2)+1/(4*SCALE**2))
        c.minimize(sum(terms))
        self.rounding_bound=error_bound
        return len(self.mech),len(self.pairs)

    def _install_general(self,schedule):
        """Mirror joint_loss's probability sorting and max matching, including ambiguity."""
        c=schedule.model; v=schedule.v; end=schedule.end; lmax=schedule.lmax
        cache={}; serial=0
        def probability(e,n2,nr):
            nonlocal serial
            key=(tuple(sorted(e.items(),key=lambda kv:str(kv[0]))),n2,nr)
            if key in cache:return cache[key]
            idx=serial;serial+=1;lb=ub=e.get('const',0)
            for k,z in e.items():
                if k=='const':continue
                lb+=z*(2 if z>0 else lmax);ub+=z*(lmax if z>0 else 2)
            lb=max(0,lb);ub=max(lb,ub)
            cnt=c.new_int_var(lb,ub,f'general_count{idx}')
            c.add(cnt==sum(z*(1 if k=='const' else end if k=='end' else v[k]) for k,z in e.items()))
            real={n:(1-A1**n*A2**n2*AR**nr)/2 for n in range(lb,ub+1)}
            table=[round(SCALE*real[n]) for n in real]
            p=c.new_int_var(min(table),max(table),f'general_prob{idx}');c.add_element(cnt-lb,table,p)
            cache[key]=(cnt,p,max(table),real);return cache[key]
        def sorted_side(side,label):
            raw=[(f,*probability(e,n2,nr)) for f,e,n2,nr in side]
            if len(raw)<2:return [(p,f,ub) for f,cnt,p,ub,real in raw]
            assert len(raw)==2
            a,b=raw
            fa,ca,pa,ua,ra=a;fb,cb,pb,ub,rb=b
            # Sorting uses unrounded probabilities, including the original flip-bit tie break.
            choose=c.new_bool_var(label+'_choose')
            rows=[(na,nb,int((rb[nb],fb)>=(ra[na],fa))) for na in ra for nb in rb]
            c.add_allowed_assignments([ca,cb,choose],rows)
            high=c.new_int_var(0,max(ua,ub),label+'_high');low=c.new_int_var(0,max(ua,ub),label+'_low')
            c.add(high==pb).only_enforce_if(choose);c.add(high==pa).only_enforce_if(~choose)
            c.add(low==pa).only_enforce_if(choose);c.add(low==pb).only_enforce_if(~choose)
            fh=c.new_bool_var(label+'_fh');fl=c.new_bool_var(label+'_fl')
            c.add(fh==fb).only_enforce_if(choose);c.add(fh==fa).only_enforce_if(~choose)
            c.add(fl==fa).only_enforce_if(choose);c.add(fl==fb).only_enforce_if(~choose)
            return [(high,fh,max(ua,ub)),(low,fl,max(ua,ub))]
        mechs=[]
        for idx,((d,s),(a,b)) in enumerate(sorted(self.basis_groups.items())):
            aa=sorted_side(a,f'sortA{idx}');bb=sorted_side(b,f'sortB{idx}')
            for rank in range(max(len(aa),len(bb))):
                pa,fa,ua=aa[rank] if rank<len(aa) else (0,0,0)
                pb,fb,ub=bb[rank] if rank<len(bb) else (0,0,0)
                p=c.new_int_var(0,max(ua,ub),f'joint{idx}_{rank}');c.add_max_equality(p,[pa,pb])
                mechs.append((d,s,fa,fb,p,max(ua,ub)))
        def weight(s,fa,fb,aa,bb,label):
            if all(isinstance(x,int) for x in (fa,fb,aa,bb)):return self.weight(s,fa^aa,fb^bb)
            def xor_bit(a,b,parity,name):
                out=c.new_bool_var(name)
                # out = a xor b xor parity, with constants admitted by add_bool_xor.
                c.add_bool_xor([a,b,out,int(not parity)])
                return out
            fx=xor_bit(fa,aa,bool(s&7),label+'_fx');fz=xor_bit(fb,bb,bool(s&56),label+'_fz')
            w=c.new_int_var(0,2,label+'_weight');c.add_allowed_assignments([fx,fz,w],[(0,0,0),(1,0,2),(0,1,1),(1,1,1)])
            return w
        terms=[];error=0;pair_count=0
        for i,(d,s,fa,fb,p,ub) in enumerate(mechs):
            if d==0:
                w=weight(s,fa,fb,0,0,f'first{i}')
                if isinstance(w,int):
                    if w:terms.append(w*SCALE*p);error+=w/(4*SCALE)
                else:
                    x=c.new_int_var(0,2*ub,f'firstprod{i}');c.add_multiplication_equality(x,[p,w]);terms.append(SCALE*x);error+=1/(2*SCALE)
            for j,(dd,ss,aa,bb,pp,uub) in enumerate(mechs[:i]):
                if dd!=d:continue
                w=weight(s^ss,fa,fb,aa,bb,f'pair{i}_{j}')
                if isinstance(w,int) and w==0:continue
                prod=c.new_int_var(0,ub*uub,f'prod{i}_{j}');c.add_multiplication_equality(prod,[p,pp]);pair_count+=1
                if isinstance(w,int):terms.append(w*prod)
                else:
                    wp=c.new_int_var(0,2*ub*uub,f'wprod{i}_{j}');c.add_multiplication_equality(wp,[prod,w]);terms.append(wp)
                error+=(ub+uub)/(2*SCALE**2)+1/(4*SCALE**2)
        c.minimize(sum(terms));self.rounding_bound=error
        return len(mechs),pair_count

if __name__=='__main__':
    a,o=baseline(); a=compact(a)
    obj=OrderedObjective(a,o)
    print('exact',g2.Model(EXTRAS).cost(a,o),'formula',obj.value(a),'mechs',len(obj.mech),'pairs',len(obj.pairs),'first',obj.first,flush=True)
    sc=Schedule(8,(a,o),fixed_order=True); print('model',obj.install(sc),'rounding_bound',obj.rounding_bound,flush=True)
    solver,status=sc.solve(60)
    print('status',solver.status_name(status),'bound',solver.best_objective_bound/(2*SCALE**2),'obj',solver.objective_value/(2*SCALE**2),flush=True)
    if status in (2,4):
        aa,oo=sc.extract(solver); print('candidate',g2.Model(EXTRAS).cost(aa,oo),obj.value(aa),flush=True); save('ordered_first.json',[encode(g2.Model(EXTRAS).cost(aa,oo),aa,oo)])
