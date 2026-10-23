from experiment import *

def raw():
    c=base()
    boundary=next(i for i,op in enumerate(c.sops) if op[0]=='barrier')
    return c,boundary

def commute(a,b):
    ka,qa,_=a;kb,qb,_=b
    if not set(qa)&set(qb):return True
    if ka==kb=='cx':return qa[0]!=qb[1] and qb[0]!=qa[1]
    if ka=='cx' and kb in ('g:t','g:tdg','g:s','g:sdg','g:z'):return qb[0]==qa[0]
    if kb=='cx' and ka in ('g:t','g:tdg','g:s','g:sdg','g:z'):return qa[0]==qb[0]
    return False

def dag(ops,can_commute=True):
    pred=[set() for _ in ops];succ=[set() for _ in ops]
    for j,b in enumerate(ops):
        for i,a in enumerate(ops[:j]):
            if (set(a[1])&set(b[1])) and not (can_commute and commute(a,b)):
                pred[j].add(i);succ[i].add(j)
    return pred,succ

def greedy(ops,seed=0,reverse=False,can_commute=True):
    pred,succ=dag(ops,can_commute)
    if reverse:pred,succ=succ,pred
    longest=[0]*len(ops)
    for i in (range(len(ops)) if reverse else reversed(range(len(ops)))):
        longest[i]=1+max((longest[j] for j in succ[i]),default=0)
    rng=random.Random(seed)
    priority=[longest[i]+(rng.random()*3 if seed else 0) for i in range(len(ops))]
    remaining=set(range(len(ops)));done=set();times=[None]*len(ops);t=0
    while remaining:
        ready=sorted([i for i in remaining if pred[i]<=done],key=lambda i:(-priority[i],i))
        taken=set();selected=[]
        for i in ready:
            if not taken&set(ops[i][1]):
                selected.append(i);taken.update(ops[i][1])
        assert selected
        for i in selected:times[i]=t
        remaining.difference_update(selected);done.update(selected);t+=1
    if reverse:times=[t-1-s for s in times]
    # Resets as late as first use, independent of the backwards/forwards scheduler.
    for i,(k,qs,b) in enumerate(ops):
        if k in ('R','RX'):
            later=[times[j] for j in range(i+1,len(ops)) if set(qs)&set(ops[j][1])]
            if later:times[i]=min(later)-1
    return times

def fixed_cycle(seed=0,reverse=False,can_commute=True):
    c,split=raw()
    pre=c.sops[:split]
    ts=greedy(pre,seed,reverse,can_commute)
    sched=from_times(pre,ts,c)
    sched.sops += c.sops[split:]
    return emit(sched.sops,c).rescheduled(lazy_init=True)

def all_asap():
    c,_=raw()
    return emit([op for op in c.sops if op[0]!='barrier'],c).rescheduled(lazy_init=True)

if __name__=='__main__':
    c,b=raw()
    evaluate('boundary_unlocked',emit(c.sops[:b]+c.sops[b+1:],c).rescheduled(lazy_init=True),'Remove initial final-cycle synchronization only')
    evaluate('all_asap',all_asap(),'Remove cycle synchronization barriers, preserve operation order')
    for rev in (False,True):
        for cm in (False,True):
            evaluate(f'pre_{"alap" if rev else "asap"}_{"commute" if cm else "ordered"}',fixed_cycle(reverse=rev,can_commute=cm),'Reschedule pre-cycle; final cycle unchanged relative schedule')
