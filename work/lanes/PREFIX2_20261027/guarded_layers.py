"""Parallel native layer search for temporally heralded parity arithmetic."""
import os,sys,json,random,heapq,math
from pathlib import Path
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[key]='1'
import flag6 as f6
from guarded_poly import allowed,isolated
from qtools import price
from qtools.validity import raw_check
from search_phase import singles
H=Path(__file__).resolve().parent;GOALS=set(f6.GOALS);GI={v:i for i,v in enumerate(f6.GOALS)}

def score_rows(rows,cov):
    missing=15-cov.bit_count();nz=sum(r!=0 for r in rows)
    near=sum(v in {rows[a]^rows[b] for a,b in f6.EDGES} for v in GOALS if not cov>>GI[v]&1)
    dirty=sum(bool(r&32) for r in rows)-1
    return missing*5+(nz-6)*(.7 if missing else 3)+.3*dirty-.2*near

def search(seed=0,width=700,maxdepth=35):
    rng=random.Random(seed);cov=f6.synth.coverage(f6.INIT,GI)
    front=[(f6.INIT,cov,[],[],[],0)];seen={};solutions=[];first=None
    for depth in range(1,maxdepth+1):
        keep={}
        for rows,cov,path,layers,checks,age in front:
            opts=[];base=score_rows(rows,cov);oldclean=isolated(rows)
            for a,b in f6.EDGES:
                if not rows[a] or not allowed(rows[a]^rows[b]):continue
                nr=list(rows);nr[b]^=nr[a]
                nc=cov|f6.synth.coverage(nr,GI)
                opts.append((a,b,base-score_rows(nr,nc)))
            candidates=[[(a,b)] for a,b,g in opts]
            for trial in range(18):
                order=sorted(opts,key=lambda z:z[2]+(rng.random()*5 if trial else 0),reverse=True)
                used=set();layer=[]
                for a,b,g in order:
                    if a not in used and b not in used:
                        layer.append((a,b));used.update([a,b])
                if layer:candidates.append(layer)
            for layer in candidates:
                nr=list(rows)
                for a,b in layer:nr[b]^=nr[a]
                nr=tuple(nr);nc=cov|f6.synth.coverage(nr,GI);pp=path+layer;ll=layers+[layer];cp=list(checks)
                newclean=isolated(nr);aa=age+1
                if newclean is not None:
                    aa=0
                    if oldclean is None:cp.append((len(pp),newclean))
                missing=15-nc.bit_count();nz=sum(r!=0 for r in nr)
                if not missing and nz==6 and len(cp)>=2 and all(not r or (r&56).bit_count()%2 for r in nr):
                    solutions.append(dict(rows=nr,path=pp,layers=ll,depth=len(pp),native_cx_layers=depth,
                                          goals=f6.GOALS,seed=seed,checkpoints=cp,guarded_arithmetic=True))
                    first=depth if first is None else first;continue
                key=(nr,nc,min(len(cp),2));cost=len(pp)+.1*aa
                if seen.get(key,math.inf)<=cost-1e-9:continue
                seen[key]=cost
                score=score_rows(nr,nc)+.08*len(pp)+.12*aa+.15*max(0,2-len(cp))+rng.random()*.35
                if key not in keep or score<keep[key][0]:keep[key]=(score,nr,nc,pp,ll,cp,aa)
        front=[(r,c,p,l,k,a) for _,r,c,p,l,k,a in heapq.nsmallest(width,keep.values(),key=lambda z:z[0])]
        lead=front[0] if front else None
        print('layerguard',seed,depth,len(front),len(solutions),
              (15-lead[1].bit_count(),sum(r!=0 for r in lead[0]),len(lead[2]),len(lead[4])) if lead else None,flush=True)
        if not front or first is not None and depth>=first+2:break
        if len(seen)>400000:seen={(r,c,min(len(k),2)):len(p)+.1*a for r,c,p,l,k,a in front}
    unique={tuple(x['path']):x for x in solutions}
    return sorted(unique.values(),key=lambda r:(r['native_cx_layers'],r['depth']))[:4]

def main():
    out=[];best=1;num=0
    for seed in range(5):
        nets=search(seed)
        (H/f'guarded_layer_network_s{seed}.json').write_text(json.dumps(nets,indent=2)+'\n')
        for net in nets[:2]:
            for mode,pseed in [('first',0),('last',0),('random',1),('random',2)]:
                rec=dict(net,phase_mode=mode,phase_seed=pseed)
                name=f'guardlayer_{num}_{mode}{pseed}'
                try:
                    st=f6.build(rec,name);raw=raw_check(st.with_suffix('.qasm').read_text(),f6.D)
                    r=dict(stem=str(st),source_cx=net['depth'],cx_layers=net['native_cx_layers'],checks=len(net['checkpoints']),raw=raw)
                    if raw['ok']:
                        c1,n=singles(st);r.update(c1=c1,harmful=n)
                        if c1<1e-5:
                            p=price(st,1);r.update(loss=p['loss'],acceptance=p['acceptance'])
                            if p['acceptance']>=.5002 and p['loss']<best:
                                best=p['loss'];(H/'guarded_layer_best.json').write_text(json.dumps(r,indent=2)+'\n')
                    print(json.dumps(r),flush=True);out.append(r)
                except Exception as ex:
                    print('ERROR',name,repr(ex),flush=True);out.append(dict(name=name,error=repr(ex)))
                (H/'guarded_layer_results.json').write_text(json.dumps(out,indent=2)+'\n')
            num+=1

if __name__=='__main__':main()
