"""Official-three-seed MC local/LNS search; no proxy or c1 eligibility filter."""
from search_v10 import *

def read_state(label):
    meta=json.loads((HERE/(label+'.json')).read_text())
    sch=meta['schedule'];ops=[(k,tuple(qs),b) for k,qs,b in sch['ops']]
    raw,_,_,_,_=base()
    if 'template_detectors' in meta:raw.detectors=meta['template_detectors']
    return raw,meta['data_qubits'],ops,sch['times'],sch['npre'],meta

def moves(ops,times,npre,rng,pred,succ):
    for _ in range(200):
        i=rng.randrange(max(0,npre-60),npre) if rng.random()<.65 else rng.randrange(npre)
        if ops[i][0] in ('R','RX') or ops[i][0].startswith('g:'):continue
        lo=max([times[j]+1 for j in pred[i]]+[min(times)-2])
        hi=min([times[j]-1 for j in succ[i]]+[max(times)])
        occupied={(q,t) for j,(op,t) in enumerate(zip(ops,times)) if j!=i for q in op[1]}
        choices=[t for t in range(max(lo,times[i]-5),min(hi,times[i]+5)+1) if t!=times[i] and not any((q,t) in occupied for q in ops[i][1])]
        if choices:
            out=list(times);out[i]=rng.choice(choices)
            return out,{'kind':'single','op':i,'from':times[i],'to':out[i]}
    return None,None

def lns(ops,times,npre,rng,pred,succ):
    pivot=rng.randrange(npre);width=rng.randrange(2,9)
    chosen={i for i in range(npre) if abs(times[i]-times[pivot])<=width and rng.random()<.85}
    # Include reset nodes before/inside this neighborhood so they don't pin first gates.
    for i in list(chosen):
        chosen.update(j for j in pred[i] if ops[j][0] in ('R','RX') and not any(times[j]<times[k]<times[i] and set(ops[j][1])&set(ops[k][1]) for k in pred[i]))
    if not chosen:return None,None
    low={i:max([times[j]+1 for j in pred[i]-chosen]+[min(times)-2]) for i in chosen}
    high={i:min([times[j]-1 for j in succ[i]-chosen]+[max(times[:npre])+1]) for i in chosen}
    occupied={(q,t) for j,(op,t) in enumerate(zip(ops,times)) if j not in chosen for q in op[1]}
    out=list(times);remaining=set(chosen);done=set(range(len(ops)))-chosen
    depth={i:1+len(pred[i])*.05+rng.random()*6 for i in chosen}
    for t in range(max(high.values()),min(low.values())-1,-1):
        ready=sorted((i for i in remaining if succ[i]<=done and low[i]<=t<=high[i] and all(out[j]>t for j in succ[i])),key=lambda i:-depth[i])
        selected=[]
        for i in ready:
            if any((q,t) in occupied for q in ops[i][1]):continue
            selected.append(i);out[i]=t;occupied.update((q,t) for q in ops[i][1])
        remaining.difference_update(selected);done.update(selected)
        if any(low[i]>t-1 for i in remaining):return None,None
    if remaining:return None,None
    return out,{'kind':'lns','pivot':pivot,'width':width,'size':len(chosen)}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('start');p.add_argument('--steps',type=int,default=180);p.add_argument('--procs',type=int,default=20);p.add_argument('--rng',type=int,default=51);p.add_argument('--prefix',default='lns');p.add_argument('--boundary-layers',type=int,default=-1);p.add_argument('--mutable-through',type=int);args=p.parse_args()
    raw,data,ops,times,npre,meta=read_state(args.start)
    if args.boundary_layers>=0:
        cutoff=min(times[npre:])+args.boundary_layers
        npre=max(i for i,t in enumerate(times) if i>=npre and t<=cutoff)+1
    if args.mutable_through is not None:
        npre=max(i for i,t in enumerate(times) if i>=npre and t<=args.mutable_through)+1
    pred,succ=dag(ops,True)
    rng=random.Random(args.rng)
    best=meta['mean'];bestlabel=args.start
    archive=[(best,times,args.start)]
    seen={hashlib.sha256(text_for(raw,ops,times).encode()).hexdigest()}
    completed=0
    while completed<args.steps:
        base_mean,base_times,parent=rng.choice(archive[:min(len(archive),5)])
        proposal,change=(moves if rng.random()<.65 else lns)(ops,base_times,npre,rng,pred,succ)
        if proposal is None:continue
        text=text_for(raw,ops,proposal);h=hashlib.sha256(text.encode()).hexdigest()
        if h in seen:continue
        seen.add(h)
        label=f'{args.prefix}_{completed:04d}';completed+=1
        save(label,raw,data,ops,proposal,npre,{'parent':parent,'change':change,'search':'official common seeds 0,1000,2000, 1e8 shots each','rng':args.rng})
        result=check_one(label,args.procs)
        if result['passed']:
            val=result['mean'];archive.append((val,proposal,label));archive.sort(key=lambda x:x[0]);archive=archive[:8]
            if val<best:
                best,bestlabel=val,label
                print(json.dumps({'BEST':bestlabel,'mean':best,'step':completed,'delta_v10':best-.00012207729961360522}),flush=True)
        progress={'completed':completed,'best':bestlabel,'mean':best,'archive':[{'label':l,'mean':m} for m,t,l in archive]}
        (HERE/f'{args.prefix}_progress.json').write_text(json.dumps(progress,indent=2)+'\n')
    print(json.dumps({'DONE':True,'best':bestlabel,'mean':best}),flush=True)
