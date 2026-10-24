"""ST1-style exact-priced timing macros and joint interaction cuts, at fixed R48."""
from common import *
import argparse,gzip,concurrent.futures,math,time
from ortools.sat.python import cp_model
from build import finish

def propose(c,index,delta,radius):
    old=c['t'];pred,_=C.S.build_dag(c['u']);R=c['meta']['R'];m=cp_model.CpModel()
    tv=[m.NewIntVar(max(0,t-radius),min(max(old),t+radius),f't{i}') for i,t in enumerate(old)]
    for j,ps in enumerate(pred):
        for i in ps:m.Add(tv[j]>tv[i])
    for i,t in enumerate(old):
        if t>=R:m.Add(tv[i]==t)
    m.Add(tv[index]==old[index]+delta)
    dev=[]
    for i,t in enumerate(old):
        d=m.NewIntVar(0,radius,f'd{i}');m.AddAbsEquality(d,tv[i]-t);dev.append(d)
    m.Minimize(sum(dev));s=cp_model.CpSolver();s.parameters.num_workers=1;s.parameters.cp_model_presolve=False;s.parameters.max_time_in_seconds=2
    st=s.Solve(m)
    return tuple(s.Value(t)-old[i] for i,t in enumerate(tv)) if st in (cp_model.OPTIMAL,cp_model.FEASIBLE) else None

def price(payload):
    c,dv=payload
    try:
        c=C.clone(c);c['t']=[t+d for t,d in zip(c['t'],dv)];c=finish(c)
        mom=module('comp29_timing_moments','work/lanes/BCPOL/moments_batch.py')
        ev=C.exact2.Eval(C.textof(c),c['meta']['data_qubits']);r=mom.evaluate(ev)
        return dict(dv=dv,**r)
    except Exception as e:return dict(dv=dv,error=repr(e))

def run(a):
    c=C.read(H/a.stem);base=screen(a.stem);best=base;history=[];counter=0
    for iteration in range(a.rounds):
        old=c['t'][:];pred,_=C.S.build_dag(c['u']);mac=[];seen=set()
        for i,(u,t) in enumerate(zip(c['u'],old)):
            if t>=c['meta']['R']:continue
            for delta in (-2,-1,1,2):
                dv=propose(c,i,delta,2)
                if dv and dv not in seen:seen.add(dv);mac.append(dv)
        print('proposals',iteration,len(mac),flush=True)
        rated=[]
        with concurrent.futures.ProcessPoolExecutor(a.workers) as pool:
            for r in pool.map(price,[(c,dv) for dv in mac]):
                counter+=1;history.append(dict(iteration=iteration,kind='macro',**r))
                if 'total' not in r:continue
                if r['exp_minus_A1']>=.5002 and r['total']<best['total']-1e-14:
                    d=C.clone(c);d['t']=[t+x for t,x in zip(old,r['dv'])];d=finish(d)
                    save(d,a.out,['timing_feedback',a.stem]);(H/(a.out+'.screen.json')).write_text(json.dumps(r,indent=2));best=r
                    print('best',counter,best['total'],best['exp_minus_A1'],flush=True)
                if r['exp_minus_A1']>=.495 and r['total']<base['total']+2e-6:rated.append(r)
        m=cp_model.CpModel();bs=[m.NewBoolVar(f'b{i}') for i in range(len(rated))];tv=[]
        for i,t in enumerate(old):
            v=m.NewIntVar(max(0,t-2),min(max(old),t+2),f't{i}');m.Add(v==t+sum(b*r['dv'][i] for b,r in zip(bs,rated) if r['dv'][i]));tv.append(v)
        for j,ps in enumerate(pred):
            for i in ps:m.Add(tv[j]>tv[i])
        m.Add(sum(bs)>=1);m.Add(sum(bs)<=8)
        loss=sum(round((r['total']-base['total'])*1e12)*b for b,r in zip(bs,rated));pen=[]
        m.Add(sum(round(math.log(base['exp_minus_A1']/r['exp_minus_A1'])*1e8)*b for b,r in zip(bs,rated))<=round(math.log(base['exp_minus_A1']/.5002)*1e8))
        for trial in range(a.trials):
            m.Minimize(loss+sum(pen));s=cp_model.CpSolver();s.parameters.num_workers=1;s.parameters.cp_model_presolve=False;s.parameters.max_time_in_seconds=5
            st=s.Solve(m)
            if st not in(cp_model.OPTIMAL,cp_model.FEASIBLE):break
            chosen=[i for i,b in enumerate(bs) if s.Value(b)];dv=tuple(s.Value(v)-t for v,t in zip(tv,old));r=price((c,dv));counter+=1
            if 'total' not in r:raise AssertionError(r)
            predval=base['total']+sum(rated[i]['total']-base['total'] for i in chosen);res=r['total']-predval
            history.append(dict(iteration=iteration,kind='joint',chosen=chosen,predicted=predval,residual=res,**r));print('joint',iteration,trial,r['total'],r['exp_minus_A1'],res,flush=True)
            if r['exp_minus_A1']>=.5002 and r['total']<best['total']-1e-14:
                d=C.clone(c);d['t']=[t+x for t,x in zip(old,dv)];d=finish(d);save(d,a.out,['timing_feedback',a.stem]);(H/(a.out+'.screen.json')).write_text(json.dumps(r,indent=2));best=r
            m.AddBoolOr([b.Not() if i in chosen else b for i,b in enumerate(bs)])
            if res>0 and len(chosen)>1:
                z=m.NewBoolVar('pen'+str(trial));m.AddBoolAnd([bs[i] for i in chosen]).OnlyEnforceIf(z);m.AddBoolOr([bs[i].Not() for i in chosen]).OnlyEnforceIf(z.Not());pen.append(round(res*1e12)*z)
        with gzip.open(H/(a.out+'.witnesses.json.gz'),'wt') as f:json.dump(history,f)
        if best['total']>=base['total']-1e-12:break
        c=C.read(H/a.out);base=best
    print('DONE',counter,best['total'],best['exp_minus_A1'],flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stem');p.add_argument('--out',default='f_timing_best');p.add_argument('--workers',type=int,default=8);p.add_argument('--rounds',type=int,default=3);p.add_argument('--trials',type=int,default=20);run(p.parse_args())
