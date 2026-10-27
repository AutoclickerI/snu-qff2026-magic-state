"""Constructive alternative and warm start for the wide15 constraint model."""
import os,sys,json,random,heapq,math
from pathlib import Path
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[key]='1'
import wide15_sat as ws
from qtools import price
from qtools.validity import raw_check
from search_phase import singles
H=Path(__file__).resolve().parent

def expand(seed=0,width=1800,maxdepth=65):
    rng=random.Random(seed);rows=tuple(ws.FINAL)
    sig=tuple((ws.A.index(q)+1)|8 if q in ws.A else 0 if q==3 else 1<<(4+ws.ZEROS.index(q)) for q in ws.CELLS)
    front=[(rows,sig,[])];seen={rows:0};target=set(ws.TARGET)
    for dep in range(1,maxdepth+1):
        nxt=[];this={}
        for rows,xs,path in front:
            for a,b in ws.EDGES:
                if not rows[a] or rows[a]^rows[b]==8 or xs[a]^xs[b]==8:continue
                nr=list(rows);nr[b]^=nr[a];nr=tuple(nr)
                if seen.get(nr,999)<dep:continue
                xx=list(xs);xx[a]^=xx[b];xx=tuple(xx);pp=path+[(a,b)]
                missing=15-len(set(nr)&target)
                if not missing:return dict(rows=nr,path=pp,x_signatures=xx,seed=seed,cx=dep)
                xor={nr[c]^nr[d] for c,d in ws.EDGES}
                near=len((target-set(nr))&xor)
                nz=sum(v!=0 for v in nr);bad=sum(v!=0 and v not in target for v in nr)
                score=5*missing+.45*(15-nz)+.55*bad-.55*near+rng.random()*.5
                if nr not in this or score<this[nr][0]:this[nr]=(score,nr,xx,pp)
        front=[(r,x,p) for _,r,x,p in heapq.nsmallest(width,this.values(),key=lambda z:z[0])]
        for r,x,p in front:seen[r]=dep
        if dep%5==0:
            lead=front[0] if front else None
            print('expand',seed,dep,len(front),'missing',15-len(set(lead[0])&target) if lead else None,flush=True)
        if not front:return None
        if len(seen)>700000:seen={r:dep for r,x,p in front}
    return None

def reduce(rows,seed=0,width=1800,maxdepth=65):
    rng=random.Random(seed);front=[(tuple(rows),[])];seen={tuple(rows):0}
    for dep in range(1,maxdepth+1):
        this={}
        for rows,path in front:
            for a,b in ws.EDGES:
                if not rows[a] or rows[a]^rows[b]==8:continue
                nr=list(rows);nr[b]^=nr[a];nr=tuple(nr)
                if seen.get(nr,999)<dep:continue
                pp=path+[(a,b)];nz=sum(v!=0 for v in nr)
                safe=all(not v or (v&24).bit_count()%2 for v in nr)
                if nz==5 and safe:return dict(rows=nr,path=pp,seed=seed,cx=dep)
                present=set(nr)-{0}
                near=sum(nr[c]!=0 and nr[d]!=0 and nr[c]^nr[d] in present for c,d in ws.EDGES)
                equal=sum(nr[c]!=0 and nr[c]==nr[d] for c,d in ws.EDGES)
                bad=sum(v!=0 and not (v&24).bit_count()%2 for v in nr)
                score=5*(nz-5)-.65*equal-.16*near+.12*bad+rng.random()*.5
                if nr not in this or score<this[nr][0]:this[nr]=(score,nr,pp)
        front=[(r,p) for _,r,p in heapq.nsmallest(width,this.values(),key=lambda z:z[0])]
        for r,p in front:seen[r]=dep
        if dep%5==0:print('reduce',seed,dep,len(front),'nonzero',sum(v!=0 for v in front[0][0]) if front else None,flush=True)
        if not front:return None
        if len(seen)>700000:seen={r:dep for r,p in front}
    return None

def layers(path):
    last=[-1]*15;out=[]
    for a,b in path:
        t=max(last[a],last[b])+1
        while len(out)<=t:out.append([])
        out[t].append([a,b]);last[a]=last[b]=t
    return out

def main():
    out=[]
    for seed in range(3):
        e=expand(seed)
        if e is None:continue
        (H/f'wide_expand_s{seed}.json').write_text(json.dumps(e,indent=2)+'\n')
        p=reduce(e['rows'],seed)
        if p is None:continue
        before=layers(reversed(p['path']));after=layers(reversed(e['path']))
        rec=dict(pre=len(before),post=len(after),layers=before+after,initial=p['rows'],phase=e['rows'],
                 cx=len(p['path'])+len(e['path']),expansion=e,preparation=p)
        (H/f'wide_constructive_s{seed}.network.json').write_text(json.dumps(rec,indent=2)+'\n')
        st=ws.build(rec,f'wide_constructive_s{seed}');raw=raw_check(st.with_suffix('.qasm').read_text(),ws.D)
        row=dict(stem=str(st),cx=rec['cx'],pre=rec['pre'],post=rec['post'],raw=raw)
        if raw['ok']:
            c1,n=singles(st);row.update(c1=c1,harmful=n)
            if c1<1e-5:row['price']=price(st,1)
        print(json.dumps(row),flush=True);out.append(row)
        (H/'wide_constructive_results.json').write_text(json.dumps(out,indent=2)+'\n')

if __name__=='__main__':main()
