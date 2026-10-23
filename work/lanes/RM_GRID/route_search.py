import re, json, math, random, heapq, argparse, time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
SRC=ROOT/'work/lanes/RM_PROTO/rm_circuit.qasm'
OUT=ROOT/'work/lanes/RM_GRID'
QASM=SRC.read_text()
# parse ordered operations; preserve comments and detector/frame separately
ops=[]
for line in QASM.splitlines():
    s=line.strip()
    if not s or s.startswith(('OPENQASM','include','qreg','creg','//')): continue
    if s.startswith('barrier'): ops.append(('barrier', tuple(map(int,re.findall(r'q\[(\d+)\]',s))))); continue
    m=re.match(r'(reset|h|t|tdg|measure) q\[(\d+)\](?: -> c\[(\d+)\])?;',s)
    if m:
        ops.append((m.group(1),int(m.group(2)), int(m.group(3)) if m.group(3) is not None else None)); continue
    m=re.match(r'cx q\[(\d+)\],q\[(\d+)\];',s)
    if m: ops.append(('cx',int(m.group(1)),int(m.group(2)))); continue
    raise ValueError(line)

N=6
cells=[r*N+c for r in range(N) for c in range(N)]
neigh={p:[x for x in (p-1,p+1,p-N,p+N) if 0<=x<36 and (x//N==p//N or x%N==p%N)] for p in cells}
# only protocol qubits 0..18; route barriers omitted
OUTLOG=[4,2,3,0,5,1,6]

class Router:
    def __init__(self,init,seed=0,allow_barrier=False):
        self.rng=random.Random(seed)
        self.owner={p:None for p in cells}
        self.pos={q:init[q] for q in range(19)}
        for q,p in self.pos.items():
            if self.owner[p] is not None: raise ValueError('collision')
            self.owner[p]=q
        self.lines=[]; self.cx=0; self.resets=0; self.seed=seed
        self.last=[0]*36; self.step=0; self.maxdepth=0
        self.used_empty=set()
        self.logical_cx=0; self.routes=0; self.route_swaps=0; self.route_moves=0
        self.stage=None
    def emit(self,s,*ps):
        self.lines.append((s,ps));
        if s=='cx': self.cx+=1
        if s=='reset': self.resets+=1
    def dcost(self,p):
        # weighted movement cost to destination cell; empties use reset+2 CX, occupied swap 3 CX
        # A longer empty corridor is preferable to swapping live tokens, because a swap
        # perturbs the future interaction layout and costs three CX per edge.
        return 2 if self.owner[p] is None else 100
    def path_to_neighbor(self,src,block,nb):
        # Dijkstra from src to target nb, not through block. Dynamic occupancy cost.
        pq=[(0,0,src,None)]; best={(src,0):(0,[])}
        dist={src:0}; hops={src:0}; prev={}
        while pq:
            cost,hh,u,_=heapq.heappop(pq)
            if cost!=dist.get(u) or hh!=hops.get(u): continue
            if u==nb:
                path=[]
                while u!=src:
                    path.append(u);u=prev[u]
                return list(reversed(path)),cost
            for v in neigh[u]:
                if v==block: continue
                nc=cost+self.dcost(v); nh=hh+1
                if nc<dist.get(v,10**9) or (nc==dist.get(v,10**9) and nh<hops.get(v,10**9)):
                    dist[v]=nc;hops[v]=nh;prev[v]=u;heapq.heappush(pq,(nc,nh,v,None))
        return None,10**9
    def move_token_step(self,q,dst):
        src=self.pos[q]; occ=self.owner[dst]
        if occ is None:
            # reset known empty destination and move state in 2 CX
            self.emit('reset',dst); self.emit('cx',src,dst); self.emit('cx',dst,src)
            self.owner[src]=None; self.owner[dst]=q; self.pos[q]=dst; self.route_moves+=1
        else:
            # swap arbitrary tokens in 3 CX
            self.emit('cx',src,dst);self.emit('cx',dst,src);self.emit('cx',src,dst)
            self.owner[src]=occ;self.owner[dst]=q;self.pos[q]=dst;self.pos[occ]=src;self.route_swaps+=1
    def route_endpoint(self,qa,qb):
        pa,pb=self.pos[qa],self.pos[qb]
        if pb in neigh[pa]: return
        # If a shortest path has only empty internal cells, implement a remote CX
        # through those |0> helpers and restore them. This often beats moving a
        # logical token and preserves the interaction layout for later gates.
        def empty_path(a,b):
            todo=[a]; prev={a:None}
            for u in todo:
                if u==b: break
                for v in neigh[u]:
                    if v in prev: continue
                    if v not in (a,b) and self.owner[v] is not None: continue
                    prev[v]=u; todo.append(v)
            if b not in prev:return []
            path=[];u=b
            while u is not None:path.append(u);u=prev[u]
            return list(reversed(path))
        ep=empty_path(pa,pb)
        bridge_cost=(2*len(ep)-3) if ep else 10**9
        # Estimate the cheapest endpoint move using the same weighted path search.
        move_cost=10**9
        for moving,block in ((qa,qb),(qb,qa)):
            bc=self.pos[block]
            for nb in neigh[bc]:
                _,cc=self.path_to_neighbor(self.pos[moving],bc,nb)
                move_cost=min(move_cost,cc+1)
        if ep and bridge_cost <= move_cost:
            for x in ep[1:-1]: self.emit('reset',x)
            for x,y in zip(ep,ep[1:]): self.emit('cx',x,y)
            for x,y in zip(ep[-3::-1],ep[-2::-1]): self.emit('cx',x,y)
            self.routes+=1; return
        self.routes+=1
        options=[]
        for moving,target,block in [(qa,pb,qb),(qb,pa,qa)]:
            block_cell=self.pos[block]
            for nb in neigh[block_cell]:
                path,cost=self.path_to_neighbor(self.pos[moving],block_cell,nb)
                if path is not None:
                    # avoid path ending at the other endpoint and ensure moving can reach; cost plus cx
                    options.append((cost,len(path),moving,path))
        if not options: raise RuntimeError((qa,qb,pa,pb,self.owner))
        _,_,moving,path=min(options,key=lambda x:(x[0],x[1],self.rng.random()))
        for dst in path: self.move_token_step(moving,dst)
        # sanity adjacent
        if self.pos[qb] not in neigh[self.pos[qa]]: raise RuntimeError('route failed')
    def run(self):
        # We omit source barriers: per-qubit order and resets/measurements enforce logical dependencies; this minimizes idle.
        for op in ops:
            typ=op[0]
            if typ=='barrier': continue
            if typ=='cx':
                qa,qb=op[1:]; self.route_endpoint(qa,qb)
                self.emit('cx',self.pos[qa],self.pos[qb]); self.logical_cx+=1
            elif typ in ('reset','h','t','tdg','measure'):
                q=op[1]; p=self.pos[q]
                if typ=='measure': self.emit(typ,p,op[2])
                else: self.emit(typ,p)
        # physical output cells in judge order corresponding to logical q [4,2,3,0,5,1,6]
        data=[self.pos[q] for q in OUTLOG]
        return data

def render(r,data,path):
    # compute max q index 36 and creg 23. Add comments no source barriers.
    nm=23
    lines=['OPENQASM 2.0;','include "qelib1.inc";','qreg q[36];',f'creg c[{nm}];']
    # Preserve stage annotations by infering from original not needed; all frame declarations copied exactly.
    for typ,ps in r.lines:
        if typ=='cx': lines.append(f'cx q[{ps[0]}],q[{ps[1]}];')
        elif typ in ('reset','h','t','tdg'): lines.append(f'{typ} q[{ps[0]}];')
        elif typ=='measure':
            # ps=(physical, cidx) because emit currently lacks c idx! fix via line parser later
            lines.append(f'measure q[{ps[0]}] -> c[{ps[1]}];')
        elif typ=='barrier': lines.append('barrier '+' '.join(f'q[{p}]' for p in ps)+';')
    # detectors and frame exactly from source
    lines += [x for x in QASM.splitlines() if x.strip().startswith('// DETECTOR') or x.strip().startswith('// FRAME_')]
    path.write_text('\n'.join(lines)+'\n')

def run(init,seed=0):
    # Need preserve measure classical indices: override runner emit manually with enriched tuples
    r=Router(init,seed)
    orig_emit=r.emit
    def emit(typ,*ps):
        if typ=='measure': orig_emit(typ,ps[0],ps[1])
        else: orig_emit(typ,*ps)
    r.emit=emit
    data=r.run(); return r,data

def initial_random(rng):
    # random injective placement; q0..18 have no special placement
    ps=rng.sample(cells,19);return dict(enumerate(ps))

def graph_scores():
    d={q:0 for q in range(19)}; e={}
    for op in ops:
        if op[0]=='cx':
            a,b=op[1:]; d[a]+=1;d[b]+=1;e[tuple(sorted((a,b)))]=e.get(tuple(sorted((a,b))),0)+1
    return d,e

def objective(init,seed):
    try:r,d=run(init,seed)
    except Exception:return (10**9,10**9,r if 'r' in locals() else None,d if 'd' in locals() else None)
    return (r.cx, len(r.lines), r)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--trials',type=int,default=100);ap.add_argument('--seed',type=int,default=0);ap.add_argument('--out',default='search.json');ap.add_argument('--emit',action='store_true');args=ap.parse_args()
    rng=random.Random(args.seed); best=[]; t0=time.time()
    # Include graph-aware seeds: random placement plus hill-climb from each.
    for i in range(args.trials):
        init=initial_random(rng)
        # local swap anneal on initial placement using deterministic route score
        cur=objective(init,args.seed+i*1009); curv=cur[0]
        for j in range(50):
            a,b=rng.sample(range(19),2); ni=dict(init);ni[a],ni[b]=ni[b],ni[a]
            nv=objective(ni,args.seed+i*1009+j+1)
            temp=max(0.2,5*(1-j/50))
            if nv[0] < curv or rng.random()<math.exp((curv-nv[0])/temp): init,cur,curv=ni,nv,nv[0]
        route_seed=args.seed+i*1009+51
        r,data=run(init,route_seed)
        rec={'cx':r.cx,'ops':len(r.lines),'routes':r.routes,'moves':r.route_moves,'swaps':r.route_swaps,'data':data,'init':init,'seed':route_seed,'elapsed':time.time()-t0}
        best.append(rec);best=sorted(best,key=lambda x:(x['cx'],x['ops']))[:20]
        if i%10==0: print(i,best[0],flush=True)
    (OUT/args.out).write_text(json.dumps(best,indent=2)+'\n')
    for k,b in enumerate(best[:5]):
        r,_=run({int(q):p for q,p in b['init'].items()},b['seed'])
        render(r,b['data'],OUT/f'candidate_{k}.qasm')
        (OUT/f'candidate_{k}.json').write_text(json.dumps({'status':'routed','source':'RM_PROTO/rm_circuit.qasm','data_qubits':b['data'],'paper_labels':[x+1 for x in b['data']],**b},indent=2)+'\n')
        print('BEST',k,b,flush=True)
if __name__=='__main__':main()
