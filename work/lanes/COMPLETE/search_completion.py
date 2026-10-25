"""Exact five-wire CNOT synthesis on the X8=+ prepared subspace.

Columns modulo the input-plus column describe the accepted isometry exactly.
All 120 output permutations are targets; BFS finds minimum CX count on the star.
This is a state-specific completion, not an arbitrary-input unitary equality.
"""
import os,sys,json,itertools,time,collections
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
sys.dont_write_bytecode=True
H=Path(__file__).resolve().parent
Q=[2,7,8,9,14];N=5;PLUS=2
E=[(i,j) for i,a in enumerate(Q) for j,b in enumerate(Q) if abs(a//6-b//6)+abs(a%6-b%6)==1]
def canon(cols):
    p=cols[PLUS];h=1<<(p.bit_length()-1)
    return sum((v^p if i!=PLUS and v&h else v)<<(5*i) for i,v in enumerate(cols))
def act(key,e):
    c,t=e
    return canon([((key>>(5*i))&31)^((((key>>(5*i+c))&1))<<t) for i in range(N)])
def permute(key,p):
    return canon([sum(((key>>(5*i+j))&1)<<p[j] for j in range(N)) for i in range(N)])
def run():
    # At tick24, CX8->9 has already encoded the local +X8 X9 constraint.
    start=act(canon([1<<i for i in range(N)]),(2,3));target=start
    old=[(2,1),(2,4),(0,2)]
    for e in old:target=act(target,e)
    targets={permute(target,p):p for p in itertools.permutations(range(N))}
    seen={start:None};front=collections.deque([start]);found={};t0=time.time();depth={start:0}
    while front and len(found)<len(targets):
        key=front.popleft()
        if key in targets:
            path=[];k=key
            while seen[k] is not None:
                prev,e=seen[k];path.append(E[e]);k=prev
            path.reverse();p=targets[key]
            found[key]=dict(permutation={str(Q[i]):Q[p[i]] for i in range(N)},
                            gates=[[Q[a],Q[b]] for a,b in path],cx=len(path),depth=depth[key])
            print('target',len(found),'cx',len(path),'states',len(seen),flush=True)
        for j,e in enumerate(E):
            nxt=act(key,e)
            if nxt not in seen:
                seen[nxt]=(key,j);depth[nxt]=depth[key]+1;front.append(nxt)
    out=dict(cells=Q,plus_input=8,input_encoding=[[8,9]],original_gates=[[Q[a],Q[b]] for a,b in old],
             targets=len(targets),states=len(seen),seconds=time.time()-t0,completions=list(found.values()))
    (H/'completions.json').write_text(json.dumps(out,indent=2)+'\n')
    print('done',len(found),len(seen),time.time()-t0,flush=True)
if __name__=='__main__':run()
