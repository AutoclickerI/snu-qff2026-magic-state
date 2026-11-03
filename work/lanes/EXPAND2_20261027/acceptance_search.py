"""Accept selected linear syndrome sectors, screened by exact single/pair loss."""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import argparse,collections,itertools,json,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'work/tools'))
sys.path.insert(0,str(ROOT/'work/lanes/FRAME20261027'))
import frame_tools as ft
from qtools.evaluator import frontend as f,sparse_walsh as sw
from qtools import price


def xor_rows(rows,mask):
    out=set()
    while mask:
        b=mask&-mask;mask^=b;out^=set(rows[b.bit_length()-1])
    return sorted(out)


def null_rows(vectors,n):
    piv={}
    for value in vectors:
        v=value
        while v:
            h=v.bit_length()-1
            if h not in piv:piv[h]=v;break
            v^=piv[h]
    for h in sorted(piv):
        for g in piv:
            if g!=h and piv[g]>>h&1:piv[g]^=piv[h]
    out=[]
    for j in range(n):
        if j in piv:continue
        row=1<<j
        for h,v in piv.items():
            if v>>j&1:row|=1<<h
        assert all((row&v).bit_count()%2==0 for v in vectors)
        out.append(row)
    return out


def prepare(stem):
    text=stem.with_suffix('.qasm').read_text();data=json.loads(stem.with_suffix('.json').read_text())['data_qubits']
    ops,dets=f.parse_current(text);f.DATA=data;m=f.make_model(ops,dets);eng=f.Engine(m)
    changes=sw.canonicalize_detector_rows(m,eng)
    rows=[sorted(d) for d in dets]
    for i,mask in changes.items():rows[i]=xor_rows(dets,mask)
    if changes:eng=f.Engine(m)
    active=sum(1<<i for i,p in enumerate(eng.projs) if p[:2]!=(0,0))
    groups=collections.defaultdict(lambda:collections.defaultdict(lambda:collections.defaultdict(float)))
    for ff in m.faults:
        key=(ff['s'],ff['d']&active,ff['e'])
        groups[ff['d']&~active][key][ff['chan']]+=ff['p']/.001
    records={}
    for sector,entries in groups.items():
        records[sector]=[(s,d,e,sum(ch.values()),dict(ch)) for (s,d,e),ch in entries.items()]
    return ops,rows,data,m,eng,records


def search(stem,max_directions=60):
    started=time.perf_counter();ops,rows,data,m,eng,groups=prepare(stem)
    cache={}
    def table(s,d):
        k=(s,d)
        if k not in cache:cache[k]=eng.ntable(s,d)
        return cache[k]
    single={}
    for v,entries in groups.items():
        a=n=0.
        for s,d,e,w,ch in entries:
            aa,nn=table(s,d);a+=w*aa
            if nn is not None:n+=w*max(0.,float(nn[e]))
        single[v]=(a,n)
    candidates=sorted((v for v,(a,n) in single.items() if v and a>1e-10 and n<1e-10),key=lambda v:-single[v][0])[:max_directions]
    risks={}
    def pair_risk(v):
        if v in risks:return risks[v]
        total=0.
        for u,aa in groups.items():
            w=u^v
            if w<u or w not in groups:continue
            bb=groups[w]
            for ia,a in enumerate(aa):
                for ib,b in enumerate(bb):
                    if u==w and ib<ia:continue
                    _,nn=table(a[0]^b[0],a[1]^b[1])
                    if nn is None:continue
                    loss=max(0.,float(nn[a[2]^b[2]]))
                    if loss<1e-12:continue
                    weight=a[3]*b[3]-sum(x*b[4].get(ch,0.) for ch,x in a[4].items())
                    if u==w and ia==ib:weight*=.5
                    total+=weight*loss
        risks[v]=total;return total
    scored=[]
    for i,v in enumerate(candidates):
        r=dict(direction=v,single_acceptance_coefficient=single[v][0],single_loss_coefficient=single[v][1],extra_pair_coefficient=pair_risk(v))
        scored.append(r);print('screen',i,json.dumps(r),flush=True)
    scored.sort(key=lambda r:(r['extra_pair_coefficient']/max(.1,r['single_acceptance_coefficient']),-r['single_acceptance_coefficient']))
    results=[];ft.OUT=HERE/'accept_cand';ft.OUT.mkdir(exist_ok=True)
    def evaluate(vecs,name):
        ds=[xor_rows(rows,r) for r in null_rows(vecs,len(rows))]
        s=ft.emit(name,ops,ds,data,metadata=dict(source=str(stem),accepted_sector_basis=vecs))
        try:r=price(s,1)
        except Exception as err:r=dict(error=str(err))
        ans=dict(stem=str(s.relative_to(ROOT)),directions=list(vecs),**r)
        results.append(ans);print('price',name,json.dumps({k:r.get(k) for k in ('loss','acceptance','error')}),flush=True)
        (HERE/'accept_results.json').write_text(json.dumps(results,indent=2)+'\n')
        return r
    for i,r in enumerate(scored[:20]):evaluate([r['direction']],f'one_{i}')
    # Combine directions only when every newly accepted sector has no harmful
    # single contribution; score the real complete circuit after each addition.
    selected=[];span={0}
    for step in range(6):
        opts=[]
        for r in scored:
            v=r['direction']
            if v in span:continue
            extra={v^w for w in span}
            if any(single.get(w,(0.,0.))[1]>1e-10 for w in extra):continue
            a=sum(single.get(w,(0.,0.))[0] for w in extra)
            if a<.01:continue
            n=sum(pair_risk(w) for w in extra)
            opts.append((n/a,-a,v,n))
        if not opts:break
        cost,neg_a,v,n=min(opts);selected.append(v);span|={v^w for w in list(span)}
        print('combine',step,cost,-neg_a,n,flush=True)
        evaluate(selected,f'combined_{step}')
    summary=dict(source=str(stem),single_sector_count=len(groups),screened=scored,prices=results,seconds=time.perf_counter()-started,kernel_tables=len(cache))
    (HERE/'accept_summary.json').write_text(json.dumps(summary,indent=2)+'\n')


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('stem');ap.add_argument('--directions',type=int,default=60);a=ap.parse_args()
    search(Path(a.stem).resolve(),a.directions)
