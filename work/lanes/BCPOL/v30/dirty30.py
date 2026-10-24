"""Four-wire dirty-bus rewrites inside BC preparation, with the data wire returned intact.

Enumerate shortest CNOT words on a grid square. The target transformation is
the original three-BC-wire word tensor identity on the fourth, dirty data wire.
Require both dirty-wire links, excluding simple two-CX echo edits.
"""
from evaluator import *
from build30 import S,native_times
from contract30 import B,C
from moments_batch import evaluate
from ortools.sat.python import cp_model
import random,re,copy,lzma,itertools

EDGES=[(0,1),(1,0),(1,2),(2,1),(2,3),(3,2),(3,0),(0,3)]
ID=(1,2,4,8)
def step(st,e):
    s=list(st);a,b=e;s[b]^=s[a];return tuple(s)
def hmask(e):return (1 if set(e)=={0,3} else 2 if set(e)=={2,3} else 0)

def catalogue():
    start=(ID,0);dist={start:0};prev=collections.defaultdict(list);queue=[start]
    for st,mask in queue:
        depth=dist[st,mask]
        if depth==8:continue
        for e in EDGES:
            nxt=(step(st,e),mask|hmask(e))
            if nxt not in dist:dist[nxt]=depth+1;queue.append(nxt)
            if dist[nxt]==depth+1 and len(prev[nxt])<6:prev[nxt].append(((st,mask),e))
    return dist,prev

def words(target,dist,prev,rng):
    key=(target,3)
    if key not in dist:return []
    out=set()
    for trial in range(32):
        cur=key;word=[]
        while cur!=(ID,0):cur,e=rng.choice(prev[cur]);word.append(e)
        out.add(tuple(reversed(word)))
        if len(out)==8:break
    return sorted(out)

def run(limit=500):
    start=time.monotonic();dist,prev=catalogue();rng=random.Random(1600)
    source=V/'inputs/v30f';text=source.with_suffix('.qasm').read_text();md=json.loads(source.with_suffix('.json').read_text());head,raw,tail=S.qasm_ops(text);us=S.fold_units(raw);ts=native_times(text,us);R=md['R'];initial={int(q):t for q,t in md['init_times'].items()}
    # Each square contains three BC cells and one dirty data cell, last.
    squares=[(6,12,13,7),(4,5,11,10),(19,25,26,20),(23,29,28,22)]
    proposals=[];seen=set();baseline=sum(u.name=='CX' for u in us)
    for square in squares:
        tri=set(square[:3]);helper=square[3];mp={q:i for i,q in enumerate(square)}
        touched=[i for i,u in enumerate(us) if set(u.qs)&tri]
        for at in range(len(touched)):
            for length in range(2,7):
                ids=touched[at:at+length]
                if len(ids)!=length:continue
                if any(us[i].name!='CX' or not set(us[i].qs)<=tri or ts[i]>=R or any(ts[i]<=initial[q] for q in us[i].qs) for i in ids):continue
                lo,hi=ts[ids[0]],ts[ids[-1]]
                if any(helper in u.qs and lo<=t<=hi for u,t in zip(us,ts)):continue
                target=ID
                for i in ids:
                    a,b=map(int,re.findall(r'q\[(\d+)\]',us[i].lines[0]));target=step(target,(mp[a],mp[b]))
                assert target[3]==8 and all(not(row&8) for row in target[:3])
                for word in words(target,dist,prev,rng):
                    if len(word)>length+2:continue
                    key=(square,tuple(ids),word)
                    if key in seen:continue
                    seen.add(key);proposals.append((square,ids,word,target))
    print(json.dumps(dict(event='catalogue',states=len(dist),proposals=len(proposals))),flush=True)
    best={};priced=valid=0;rows=[]
    with lzma.open(V/'runs/dirty_bus.jsonl.xz','wt') as log:
        for number,(square,ids,word,target) in enumerate(proposals[:limit]):
            helper=square[3];drop=set(ids);movable=[]
            for q in square[:3]:
                before=[i for i,u in enumerate(us) if q in u.qs and i<ids[0]]
                if before:
                    i=before[-1]
                    if ts[i]==initial[q] and us[i].name in ('RESET','RX','MEASURE','MX'):movable.append(i);drop.add(i)
            new=[S.Unit([f'cx q[{square[a]}],q[{square[b]}];'],[]) for a,b in word]
            opunits=[us[i] for i in movable]+new
            m=cp_model.CpModel();tv=[m.NewIntVar(0,R-1,f't{i}') for i in range(len(opunits))]
            for q in square:
                sub=[j for j,u in enumerate(opunits) if q in u.qs]
                if not sub:continue
                left=max((ts[i] for i,u in enumerate(us) if q in u.qs and i<ids[0] and i not in drop),default=-1)
                right=min((ts[i] for i,u in enumerate(us) if q in u.qs and i>ids[-1] and i not in drop),default=R)
                m.Add(tv[sub[0]]>left);m.Add(tv[sub[-1]]<right)
                for a,b in zip(sub,sub[1:]):m.Add(tv[b]>tv[a])
            m.Maximize(sum(tv));solver=cp_model.CpSolver();solver.parameters.num_workers=1;solver.parameters.max_time_in_seconds=1;status=solver.Solve(m)
            row=dict(index=number,square=square,removed=ids,word=word,initialization_moves=movable,unitary_target=target)
            if status not in (cp_model.OPTIMAL,cp_model.FEASIBLE):row['status']='SCHEDULE_INFEASIBLE'
            else:
                nt=[solver.Value(t) for t in tv];units=[u for i,u in enumerate(us) if i not in drop]+opunits;times=[t for i,t in enumerate(ts) if i not in drop]+nt;order=sorted(range(len(units)),key=lambda i:(times[i],i));units=[units[i] for i in order];times=[times[i] for i in order];candidate=S.emit(head,units,times,tail)
                tag=f'dirty_bus_{number:04d}';current=V/'inputs/dirty_current';meta=copy.deepcopy(md);meta.pop('prep',None);meta.pop('verification',None);meta.update(method='dirty data bus inside BC resource',dirty_bus=row,CX=baseline-len(ids)+len(word),boundary_step=R+1,region_qubits=B+C+[helper])
                for j,i in enumerate(movable):meta['init_times'][str(us[i].qs[0])]=nt[j]
                try:
                    _,rr,_=S.qasm_ops(candidate);nu=S.fold_units(rr);actual=native_times(candidate,nu)
                    kept=collections.Counter((tuple(u.lines),t) for i,(u,t) in enumerate(zip(us,ts)) if i not in drop);actuals=collections.Counter((tuple(u.lines),t) for u,t in zip(nu,actual));assert not (kept-actuals),'retained exterior native timing changed'
                    ev=exact2.Eval(candidate,md['data_qubits']);c1=float(ev.fp@ev.n_single);valid+=1
                    price=evaluate(ev) if abs(c1)<1e-12 else dict(c1=c1,exp_minus_A1=math.exp(-float(ev.fp@(1-ev.a_single))),invalid_cubic=True)
                    row.update(price,status='SCREENED',tag=tag,scheduled_times=nt);priced+=1
                    objective=price.get('total',price['c1']);key=(helper,abs(c1)>=1e-12)
                    if price['exp_minus_A1']>=.5002 and objective<best.get(key,(float('inf'),None))[0]-1e-13:
                        best[key]=(objective,tag);s=V/'finalists'/tag;s.with_suffix('.qasm').write_text(candidate);s.with_suffix('.json').write_text(json.dumps(meta,indent=2));s.with_suffix('.screen.json').write_text(json.dumps(price,indent=2));print(json.dumps(dict(tag=tag,helper=helper,**price)),flush=True)
                except (ValueError,AssertionError) as ex:row.update(status='REJECTED',error=str(ex))
            log.write(json.dumps(row)+'\n');log.flush();rows.append(row)
    result=dict(status='FINITE_SCAN_COMPLETE',proposals=len(proposals),attempted=len(rows),priced=priced,valid=valid,best={str(k):v for k,v in best.items()},seconds=time.monotonic()-start,scope='Shortest helper-using words up to length 8 and at most two CX more than each isolated 2–6-gate BC window. The dirty data qubit is returned exactly, for arbitrary entangled input.')
    (V/'dirty_bus.receipt.json').write_text(json.dumps(result,indent=2));(V/'dirty.selected.json').write_text(json.dumps([tag for objective,tag in best.values()],indent=2));print(json.dumps(result),flush=True)

if __name__=='__main__':run()
