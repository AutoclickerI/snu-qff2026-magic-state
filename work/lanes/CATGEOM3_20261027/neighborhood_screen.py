"""Exact native neighbor coverage of two independent cat control sets."""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='1'
import argparse,hashlib,itertools,json,time
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
N=36
NEIGHBORS=[tuple(r for r in range(N) if abs(q//6-r//6)+abs(q%6-r%6)==1) for q in range(N)]
NB=[sum(1<<r for r in ns) for ns in NEIGHBORS]


def mask(seq):return sum(1<<q for q in seq)
def cells(m):return [q for q in range(N) if m>>q&1]


def enumerate_sets(k):
    result=[]
    for qs in itertools.combinations(range(N),k):
        qmask=mask(qs);neighbors=0
        for q in qs:neighbors|=NB[q]
        neighbors&=~qmask
        if neighbors.bit_count()>=7:result.append((qs,qmask,neighbors))
    return result


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--first',type=int,default=3);ap.add_argument('--second',type=int,default=3)
    ap.add_argument('--retain',type=int,default=200);args=ap.parse_args();start=time.perf_counter()
    left=enumerate_sets(args.first);right=left if args.first==args.second else enumerate_sets(args.second)
    qm=np.array([r[1]for r in right],dtype=np.uint64);nm=np.array([r[2]for r in right],dtype=np.uint64)
    best=0;hist={};witnesses=[];eligible=0;examined=0
    for i,(a,am,an) in enumerate(left):
        allowed=(qm & np.uint64(am))==0
        if args.first==args.second:allowed[:i+1]=False
        values=np.bitwise_count(nm & np.uint64(an))
        values[~allowed]=0
        count=int(np.count_nonzero(allowed));examined+=count
        maxval=int(values.max())
        if maxval>best:best=maxval;witnesses=[]
        for n in range(7,maxval+1):
            ids=np.flatnonzero((values==n)&allowed);hist[n]=hist.get(n,0)+len(ids);eligible+=len(ids)
        if maxval==best:
            ids=np.flatnonzero((values==best)&allowed)
            for j in ids:
                b,bm,bn=right[int(j)]
                common=an&bn&~(am|bm)
                # an and bn already exclude own cats; intersection therefore
                # excludes both cat sets. Assert before recording.
                assert common==an&bn
                if len(witnesses)<args.retain:
                    witnesses.append(dict(cat_a=list(a),cat_b=list(b),data_options=cells(common),coverage=best))
    out=dict(grid=[6,6],cat_sizes=[args.first,args.second],left_sets=len(left),right_sets=len(right),
        examined_disjoint_pairs=examined,maximum_coverage=best,eligible_pairs=eligible,
        coverage_histogram=hist,witnesses=witnesses,seconds=time.perf_counter()-start,
        proof_scope='Exhaustive unordered cat subsets of specified sizes on the6x6 grid. Each data cell must be adjacent to at leastone cat from each disjoint set; no connectivity, terminal, preparation, or time restriction is imposed.',
        source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    path=HERE/f'neighborhood_{args.first}_{args.second}.json';path.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k!='witnesses'}),flush=True)
    print(json.dumps(dict(first_witness=witnesses[0]if witnesses else None,path=str(path))),flush=True)


if __name__=='__main__':main()
