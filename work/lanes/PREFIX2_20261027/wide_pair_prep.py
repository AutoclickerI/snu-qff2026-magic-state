"""Pair-aware preparation of a fixed spatial15T phase block.

The exact accepted-pair response of every pre-phase Z class to every later fault
is measured from the real complete circuit. Native layer synthesis then tracks
Z-equivalent noise weights and their logical complements8. An isolated plus
input can be frozen at its final backward use, accounting for just-in-time reset
rather than charging it for fictitious earlier waiting.
"""
import os,sys,json,random,heapq,math
from pathlib import Path
from collections import defaultdict
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[key]='1'
import wide15_sat as ws
from qtools.evaluator import frontend as fa,sparse_walsh as sw
from qtools import price
from qtools.validity import raw_check
from search_phase import singles
H=Path(__file__).resolve().parent;TARGET=set(ws.TARGET)

def kernel(stem,rec):
    stem=Path(stem);fa.DATA=ws.D;ops,dets=fa.parse_current(stem.with_suffix('.qasm').read_text())
    m=fa.make_model(ops,dets);e=fa.Engine(m);sw.canonicalize_detector_rows(m,e);e=fa.Engine(m)
    phase=max(o.time for o in ops if o.kind in ('T','TDG'))
    byq={}
    for f in m.faults:
        op=ops[f['ins']]
        if op.time==phase and op.kind=='TDG' and f['pauli']=='Z':byq[f['qs'][0]]=(f['s'],f['d'],f['e'])
    basis=fa.Basis();sig=[]
    for q,r in zip(ws.CELLS,rec['phase']):
        if basis.express(r) is None:basis.add(r);sig.append(byq[q])
    signatures=[]
    for r in range(32):
        mask=basis.express(r);s=d=z=0
        for j,k in enumerate(sig):
            if mask>>j&1:s^=k[0];d^=k[1];z^=k[2]
        assert s==0;signatures.append((s,d,z))
    later=[f for f in m.faults if ops[f['ins']].time>=phase]
    tables={};K=[]
    for s,d,z in signatures:
        total=0
        for f in later:
            key=(s^f['s'],d^f['d'])
            if key not in tables:tables[key]=e.ntable(*key)
            a,n=tables[key]
            if n is not None:total+=f['p']*float(n[z^f['e']])/.001
        K.append(total)
    ans=dict(stem=str(stem),phase_time=phase,K=K,post_faults=len(later),tables=len(tables))
    (H/'wide_Z_kernel.json').write_text(json.dumps(ans,indent=2)+'\n');print('K',K,flush=True)
    return K

def span(rows):
    s={0}
    for r in rows:s|={x^r for x in tuple(s)}
    return s

def codewords(rows):
    words={0}
    for j in range(5):
        column=sum(((r>>j)&1)<<i for i,r in enumerate(rows))
        words|={w^column for w in tuple(words)}
    return words

def freeze(rows,mask,words=None):
    if words is None:words=codewords(rows)
    for i,r in enumerate(rows):
        if not r or mask>>i&1 or r not in TARGET:continue
        other=[x for j,x in enumerate(rows) if j!=i and not mask>>j&1]
        if 1<<i not in words:continue
        if any(other) and not any(x in TARGET for x in other):continue
        mask|=1<<i
    return mask

def add(w,cost,adds,K):
    nw=list(w)
    for r,p in adds:
        if r:
            cost+=p*(K[r]+nw[r^8]);nw[r]+=p
    return tuple(nw),cost

def noise_context(rows):
    # Before the T block the state is uniform on this binary column space.
    words=codewords(rows);gates={}
    for a,b in ws.EDGES:
        adds=[]
        for pa in 'IXYZ':
            for pb in 'IXYZ':
                if pa==pb=='I':continue
                x=(int(pa in 'XY')<<a)|(int(pb in 'XY')<<b)
                if x not in words:continue
                r=(rows[a] if pa in 'YZ' else 0)^(rows[b] if pb in 'YZ' else 0)
                if r:adds.append((r,1/15))
        gates[(a,b)]=adds
    return words,gates

def noise(rows,layer,frozen,words,gates):
    used={q for ab in layer for q in ab};adds=[]
    for edge in layer:adds.extend(gates[edge])
    for q,r in enumerate(rows):
        if q not in used and not frozen>>q&1 and r:adds.append((r,(1+int(1<<q in words))/3))
    return adds

def metric(rows):
    nz=sum(v!=0 for v in rows);present=set(rows)-{0}
    eq=sum(rows[a]!=0 and rows[a]==rows[b] for a,b in ws.EDGES)
    near=sum(rows[a]!=0 and rows[b]!=0 and rows[a]^rows[b] in present for a,b in ws.EDGES)
    return 5*(nz-5)-.5*eq-.12*near

def search(initial,K,seed=0,gamma=.3,width=450,maxdepth=20):
    rng=random.Random(seed);rows=tuple(initial);fro=freeze(rows,0)
    w,cost=add((0.,)*32,0.,[(r,1.) for i,r in enumerate(rows) if fro>>i&1],K)
    front=[(rows,[],0,fro,w,cost)];seen={};sol=[];first=None
    for depth in range(1,maxdepth+1):
        keep={}
        for rows,layers,ncx,frozen,w,cost in front:
            words,gatenoise=noise_context(rows)
            opts=[];base=metric(rows)
            for a,b in ws.EDGES:
                if frozen>>a&1 or frozen>>b&1 or not rows[a] or rows[a]^rows[b]==8:continue
                nr=list(rows);nr[b]^=nr[a];gain=base-metric(nr);opts.append((a,b,gain))
            candidates=[[(a,b)] for a,b,g in opts]
            for trial in range(10):
                order=sorted(opts,key=lambda z:z[2]*1.5+(rng.random()*5 if trial else 0),reverse=True)
                used=set();layer=[]
                for a,b,g in order:
                    if a not in used and b not in used:layer.append((a,b));used.update([a,b])
                if layer:candidates.append(layer)
            for layer in candidates:
                nr=list(rows)
                for a,b in layer:nr[b]^=nr[a]
                nr=tuple(nr)
                newwords=set()
                for word in words:
                    for a,b in layer:word^=((word>>a)&1)<<b
                    newwords.add(word)
                nf=freeze(nr,frozen,newwords)
                adds=noise(rows,layer,frozen,words,gatenoise)+[(r,1.) for q,r in enumerate(nr) if nf>>q&1 and not frozen>>q&1]
                nw,cc=add(w,cost,adds,K);ls=layers+[layer];ng=ncx+len(layer)
                key=(nr,nf)
                if seen.get(key,math.inf)<=cc+1e-10:continue
                seen[key]=cc
                if nf.bit_count()==5 and sum(r!=0 for r in nr)==5:
                    sol.append(dict(rows=nr,layers=ls,cx=ng,depth=depth,cost=cc,seed=seed,gamma=gamma));first=depth if first is None else first
                    continue
                score=metric(nr)+gamma*cc+.025*ng+rng.random()*.25
                if key not in keep or score<keep[key][0]:keep[key]=(score,nr,ls,ng,nf,nw,cc)
        front=[(r,l,n,f,w,c) for _,r,l,n,f,w,c in heapq.nsmallest(width,keep.values(),key=lambda z:z[0])]
        lead=front[0] if front else None
        print('prep',seed,gamma,depth,len(front),len(sol),('nz',sum(r!=0 for r in lead[0]),'cost',lead[-1]) if lead else None,flush=True)
        if not front or first is not None and depth>=first+2:break
        if len(seen)>300000:seen={(r,f):c for r,l,n,f,w,c in front}
    return sorted(sol,key=lambda s:s['cost'])[:3]

def main():
    old=json.loads((H/'wide_constructive_s0.network.json').read_text())
    K=kernel(H/'cand/wide_constructive_s0',old);results=[]
    for gamma in [.1,.3,.8]:
        for seed in range(2):
            found=search(old['phase'],K,seed,gamma)
            (H/f'wide_pairprep_g{gamma}_s{seed}.json').write_text(json.dumps(found,indent=2)+'\n')
            for k,p in enumerate(found[:2]):
                pre=list(reversed(p['layers']));post=old['layers'][old['pre']:]
                rec=dict(pre=len(pre),post=len(post),initial=p['rows'],phase=old['phase'],layers=pre+post,cx=p['cx']+sum(map(len,post)),pair_prep=p)
                name=f'wide_pair_g{gamma}_s{seed}_k{k}';(H/f'{name}.network.json').write_text(json.dumps(rec,indent=2)+'\n')
                st=ws.build(rec,name);raw=raw_check(st.with_suffix('.qasm').read_text(),ws.D)
                ans=dict(stem=str(st),cost=p['cost'],pre=len(pre),cx=rec['cx'],raw=raw)
                if raw['ok']:
                    c1,n=singles(st);ans.update(c1=c1,harmful=n)
                    if c1<1e-5:ans['price']=price(st,1)
                print(json.dumps(ans),flush=True);results.append(ans)
                (H/'wide_pair_results.json').write_text(json.dumps(results,indent=2)+'\n')

if __name__=='__main__':main()
