"""Parallel-layer beam construction of the 15-cell source architecture."""
import os,sys,json,random,heapq
from pathlib import Path
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[key]='1'
import wide15_sat as ws
from qtools import price
from qtools.validity import raw_check
from search_phase import singles
H=Path(__file__).resolve().parent;TARGET=set(ws.TARGET)

def metric(rows,kind):
    present=set(rows);nz=sum(x!=0 for x in rows)
    bad=sum(x!=0 and x not in TARGET for x in rows)
    if kind=='expand':
        missing=15-len(present&TARGET)
        near=len((TARGET-present)&{rows[a]^rows[b] for a,b in ws.EDGES})
        return missing*5+.4*(15-nz)+.5*bad-.45*near
    near=sum(rows[a]!=0 and rows[b]!=0 and rows[a]^rows[b] in present-{0} for a,b in ws.EDGES)
    equal=sum(rows[a]!=0 and rows[a]==rows[b] for a,b in ws.EDGES)
    return (nz-5)*5-.6*equal-.14*near+.12*bad

def search(kind,initial,seed=0,width=850,maxdepth=18):
    rng=random.Random(seed)
    if kind=='expand':xs=tuple((ws.A.index(q)+1)|8 if q in ws.A else 0 if q==3 else 1<<(4+ws.ZEROS.index(q)) for q in ws.CELLS)
    else:xs=None
    front=[(tuple(initial),xs,[],0)];seen={tuple(initial):0}
    for depth in range(1,maxdepth+1):
        keep={};solutions=[]
        for rows,xs,layers,count in front:
            base=metric(rows,kind);opts=[]
            for a,b in ws.EDGES:
                if not rows[a] or rows[a]^rows[b]==8 or xs is not None and xs[a]^xs[b]==8:continue
                nr=list(rows);nr[b]^=nr[a]
                gain=base-metric(nr,kind);opts.append((a,b,gain))
            candidates=[[(a,b)] for a,b,gain in opts]
            for trial in range(14):
                ordered=sorted(opts,key=lambda z:z[2]*1.5+(rng.random()*5 if trial else 0),reverse=True)
                used=set();layer=[]
                for a,b,gain in ordered:
                    if a not in used and b not in used:
                        layer.append((a,b));used.update([a,b])
                if layer:candidates.append(layer)
            for layer in candidates:
                nr=list(rows);xx=list(xs) if xs is not None else None
                for a,b in layer:
                    nr[b]^=nr[a]
                    if xx is not None:xx[a]^=xx[b]
                nr=tuple(nr);xx=tuple(xx) if xx is not None else None
                if seen.get(nr,999)<depth:continue
                nc=count+len(layer);ls=layers+[layer]
                goal=(set(nr)==TARGET if kind=='expand' else sum(v!=0 for v in nr)==5 and all(not v or v in TARGET for v in nr))
                if goal:
                    solutions.append(dict(rows=nr,layers=ls,cx=nc,depth=depth,seed=seed));continue
                score=metric(nr,kind)+.04*nc+rng.random()*.3
                if nr not in keep or score<keep[nr][0]:keep[nr]=(score,nr,xx,ls,nc)
        if solutions:
            print(kind,'solution',seed,depth,min(x['cx'] for x in solutions),flush=True)
            return min(solutions,key=lambda s:s['cx'])
        front=[(r,x,l,c) for _,r,x,l,c in heapq.nsmallest(width,keep.values(),key=lambda z:z[0])]
        for r,x,l,c in front:seen[r]=depth
        print(kind,seed,depth,len(front),metric(front[0][0],kind) if front else None,flush=True)
        if not front:break
        if len(seen)>300000:seen={r:depth for r,x,l,c in front}
    return None

def main():
    out=[]
    for seed in range(3):
        e=search('expand',ws.FINAL,seed)
        if e is None:continue
        (H/f'wide_layer_expand_s{seed}.json').write_text(json.dumps(e,indent=2)+'\n')
        p=search('reduce',e['rows'],seed)
        if p is None:continue
        before=list(reversed(p['layers']));after=list(reversed(e['layers']))
        rec=dict(pre=len(before),post=len(after),initial=p['rows'],phase=e['rows'],layers=before+after,cx=p['cx']+e['cx'],encoder=p,decoder=e)
        name=f'wide_layers_s{seed}';(H/f'{name}.network.json').write_text(json.dumps(rec,indent=2)+'\n')
        st=ws.build(rec,name);raw=raw_check(st.with_suffix('.qasm').read_text(),ws.D)
        row=dict(stem=str(st),cx=rec['cx'],pre=rec['pre'],post=rec['post'],raw=raw)
        if raw['ok']:
            c1,n=singles(st);row.update(c1=c1,harmful=n)
            if c1<1e-5:row['price']=price(st,1)
        print(json.dumps(row),flush=True);out.append(row)
        (H/'wide_layer_results.json').write_text(json.dumps(out,indent=2)+'\n')

if __name__=='__main__':main()
