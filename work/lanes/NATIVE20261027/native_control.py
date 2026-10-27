"""Complete grid-native control for the reconstructed joint-flag architecture.

Seven terminal squares are placed first. Code labels, tile orientations, and
the remaining helper positions are jointly optimized for precursor gate cost.
The terminal two CX layers stay local. Earlier remote CXs are realized by
exact dirty-intermediate bridge circuits; this is deliberately a diagnostic
control, not a claim that a bridge compiler solves native fault tolerance.
"""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import argparse,collections,json,math,random,re,time
from pathlib import Path
import numpy as np
import rebuild
from qtools import write_stem,price
from qtools.evaluator.frontend import parse_current

HERE=Path(__file__).resolve().parent
NB={q:[r for r in range(36) if abs(q//6-r//6)+abs(q%6-r%6)==1] for q in range(36)}
TILES=[(r*6+c,r*6+c+1,(r+1)*6+c,(r+1)*6+c+1) for r in (0,2,4) for c in (0,2,4)]

def physical_map(tile_ids,orientations,helpers):
    # Abstract terminal roles D=0:7, B=7:14, A=14:21, C=21:28.
    out=[None]*36
    for i,(ti,o) in enumerate(zip(tile_ids,orientations)):
        base=TILES[ti]; corner=o//2; adj=[j for j in range(4) if (j^corner) in (1,2)]
        if o%2:adj.reverse()
        out[i]=base[corner];out[7+i]=base[adj[0]];out[14+i]=base[adj[1]];out[21+i]=base[corner^3]
    rest=sorted(set(range(36))-set(out[:28]))
    for i,j in enumerate(helpers):out[28+i]=rest[j]
    assert len(set(out))==36
    return out

def optimize_layout(c,seed=611,steps=30000):
    rng=random.Random(seed);ops,_=parse_current(c.text())
    ee=[o.qs for o in ops if o.kind=='CX'];u=np.array([e[0] for e in ee]);v=np.array([e[1] for e in ee])
    def cost(state):
        p=np.array(physical_map(*state));dd=abs(p[u]//6-p[v]//6)+abs(p[u]%6-p[v]%6)
        return int(np.where(dd==1,1,4*dd-4).sum())
    state=[list(range(7)),[rng.randrange(8) for _ in range(7)],list(range(8))]
    current=cost(state);best=(current,[x[:] for x in state]);trace=[]
    for it in range(steps):
        cand=[x[:] for x in state];kind=rng.randrange(4)
        if kind==0:
            a,b=rng.sample(range(7),2);cand[0][a],cand[0][b]=cand[0][b],cand[0][a]
        elif kind==1:cand[1][rng.randrange(7)]=rng.randrange(8)
        elif kind==2:
            a,b=rng.sample(range(8),2);cand[2][a],cand[2][b]=cand[2][b],cand[2][a]
        else:cand[0][rng.randrange(7)]=rng.choice(sorted(set(range(9))-set(cand[0])))
        val=cost(cand);temp=18*(1-it/steps)+.3
        if val<current or rng.random()<math.exp((current-val)/temp):state=cand;current=val
        if current<best[0]:best=(current,[x[:] for x in state]);trace.append([it,current])
    return physical_map(*best[1]),dict(predicted_bridge_cx=best[0],state=best[1],seed=seed,steps=steps,trace=trace)

def path(a,b,forbidden=()):
    forbidden=set(forbidden)-{a,b};queue=collections.deque([a]);parent={a:None}
    while queue:
        q=queue.popleft()
        if q==b:
            out=[]
            while q is not None:out.append(q);q=parent[q]
            return out[::-1]
        for r in NB[q]:
            if r not in forbidden and r not in parent:parent[r]=q;queue.append(r)
    return None

def bridge(p):
    d=len(p)-1
    if d==1:return [(p[0],p[1])]
    return ([(p[i],p[i+1]) for i in range(d)]+
            [(p[i],p[i+1]) for i in range(d-2,-1,-1)]+
            [(p[i],p[i+1]) for i in range(1,d)]+
            [(p[i],p[i+1]) for i in range(d-2,0,-1)])

def compile_native(source,mapping):
    native=rebuild.Circuit();native.bit=source.bit;native.dets=source.dets[:]
    clock=0;statistics=[]
    for tick,lines in sorted(source.ops.items()):
        local=[];cx=[];one_qubits=set()
        for line in lines:
            qs=list(map(int,re.findall(r'q\[(\d+)\]',line)))
            if line.startswith('cx '):cx.append(tuple(mapping[q] for q in qs))
            else:
                local.append(re.sub(r'q\[(\d+)\]',lambda m:f'q[{mapping[int(m[1])]}]',line));one_qubits.update(mapping[q] for q in qs)
        start=clock
        # Execute local operations and any disjoint nearest-neighbor CXs.
        immediate=[e for e in cx if e[1] in NB[e[0]] and not (set(e)&one_qubits)]
        if local or immediate:
            for line in local:native.add(clock,line)
            for a,b in immediate:native.cx(clock,a,b);cx.remove((a,b))
            clock+=1
        while cx:
            supports=set();batch=[];remain=[]
            # Prefer short bridges, allow disjoint supports to run in parallel.
            for a,b in sorted(cx,key=lambda e:abs(e[0]//6-e[1]//6)+abs(e[0]%6-e[1]%6)):
                if {a,b}&supports:remain.append((a,b));continue
                p=path(a,b,supports)
                if p is None:remain.append((a,b));continue
                batch.append(bridge(p));supports.update(p)
            assert batch
            for word in batch:
                for j,(a,b) in enumerate(word):native.cx(clock+j,a,b)
            clock+=max(map(len,batch));cx=remain
        statistics.append(dict(source_tick=tick,start=start,end=clock,cx=sum(l.startswith('cx ') for l in lines)))
    return native,statistics

def verify_bridge_identities():
    # GF(2) operator check on arbitrary intermediate data, not just zero ancillas.
    for d in range(1,7):
        rows=[1<<i for i in range(d+1)]
        for a,b in bridge(list(range(d+1))):rows[b]^=rows[a]
        expected=[1<<i for i in range(d+1)];expected[-1]^=1
        assert rows==expected,(d,rows,expected)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--seed',type=int,default=611);ap.add_argument('--steps',type=int,default=30000);ap.add_argument('--price',action='store_true');args=ap.parse_args()
    verify_bridge_identities()
    c,D=rebuild.build_joint_flags(18,12)
    mapping,layout=optimize_layout(c,args.seed,args.steps)
    native,stats=compile_native(c,mapping)
    outputs=[mapping[q] for q in D]
    stem=write_stem(native.text(),outputs,HERE/'builds',f'native_joint_flags_seed{args.seed}',source=dict(grid_free=False,compiler='terminal-tile placement and exact native bridge synthesis',mapping=mapping,abstract='joint_flags_R18_cat2time12'))
    ops,_=parse_current(native.text());assert all(o.qs[1] in NB[o.qs[0]] for o in ops if o.kind=='CX')
    result=dict(stem=str(stem),layout=layout,mapping=mapping,ticks=max(o.time for o in ops)+1,cx=sum(o.kind=='CX' for o in ops),T=sum(o.kind in ('T','TDG') for o in ops),schedule=stats)
    print(json.dumps({k:v for k,v in result.items() if k not in ('schedule','layout')},indent=2),flush=True)
    if args.price:
        try:result['price']=price(stem,processes=1)
        except Exception as exc:result['error']=str(exc)
        print(json.dumps(result.get('price',result.get('error')),indent=2),flush=True)
    (HERE/f'native_seed{args.seed}.json').write_text(json.dumps(result,indent=2)+'\n')

if __name__=='__main__':main()
