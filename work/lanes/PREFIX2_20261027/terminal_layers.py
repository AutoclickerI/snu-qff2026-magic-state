"""Layer search for native |+_L> ancilla encoders and short CSS decoders."""
import os,sys,json,itertools,random
from pathlib import Path
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[key]='1'
import terminal_plus as tp
H=Path(__file__).resolve().parent
MATCHES=[]
for n in range(1,4):
    for edges in itertools.combinations(tp.EDGES,n):
        qs=[q for a,b in edges for q in (a,b)]
        if len(set(qs))==len(qs):MATCHES.append(edges)

def span(rows):
    out={0}
    for x in rows:out|={v^x for v in tuple(out)}
    return out

def flags(rows):
    return [i for i,r in enumerate(rows) if r and r not in span(rows[:i]+rows[i+1:])]

def search(seed=0,width=1800,depth=9):
    rng=random.Random(seed);beam=[(tuple(range(9,16)),[],[],0)];seen={};sol=[]
    for dep in range(1,depth+1):
        nxt={}
        for rows,path,layers,nc in beam:
            for layer in MATCHES:
                nr=list(rows);ok=True
                for a,b in layer:
                    if not rows[a] or rows[a]^rows[b]==8:ok=False;break
                    nr[b]^=nr[a]
                if not ok:continue
                nr=tuple(nr);ng=nc+len(layer)
                if seen.get(nr,999)<dep:continue
                nz=sum(x!=0 for x in nr)
                if nz==4:
                    sol.append(dict(rows=nr,path=path+list(layer),layers=layers+[layer],depth=dep,cx=ng,seed=seed))
                    continue
                score=4*nz+.4*sum(x!=0 and x<8 for x in nr)+.08*ng+rng.random()*.3
                if nr not in nxt or score<nxt[nr][0]:nxt[nr]=(score,nr,path+list(layer),layers+[layer],ng)
        beam=[(r,p,l,n) for score,r,p,l,n in sorted(nxt.values())[:width]]
        for rows,*rest in beam:seen[rows]=dep
        print('layers',seed,dep,'states',len(beam),'found',len(sol),flush=True)
        if sol:break
    unique={tuple(s['path']):s for s in sol}
    return sorted(unique.values(),key=lambda s:(s['depth'],s['cx']))[:30]

def decoders():
    beam=[(tuple(range(9,16)),[])];seen={};out=[]
    for dep in range(1,6):
        nxt={}
        for rows,path in beam:
            for a,b in tp.EDGES:
                if not rows[a]:continue
                nr=list(rows);nr[b]^=nr[a];nr=tuple(nr)
                if seen.get(nr,999)<dep:continue
                ff=flags(list(nr))
                if ff:out.append(dict(rows=nr,path=path+[(a,b)],flags=ff,depth=dep))
                if nr not in nxt:nxt[nr]=(nr,path+[(a,b)])
        beam=list(nxt.values())
        for rows,path in beam:seen[rows]=dep
        if len(beam)>60000:beam=beam[:60000]
        print('decoders',dep,len(beam),len(out),flush=True)
    unique={tuple(s['path']):s for s in out}
    return sorted(unique.values(),key=lambda s:(-len(s['flags'])/len(s['path']),len(s['path'])))

if __name__=='__main__':
    out=[]
    for seed in range(3):out+=search(seed)
    (H/'terminal_layer_networks.json').write_text(json.dumps(out,indent=2)+'\n')
    dd=decoders();(H/'terminal_decoders.json').write_text(json.dumps(dd,indent=2)+'\n')
