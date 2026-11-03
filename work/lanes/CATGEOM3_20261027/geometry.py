"""Native two-GHZ3 cover, measured-bridge preparation, and terminal packing."""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='1'
import argparse,collections,hashlib,itertools,json,time
from pathlib import Path
from ortools.sat.python import cp_model
from neighborhood_screen import HERE,NEIGHBORS,NB,N,cells,mask


def connected_sets(max_size):
    layer={1<<q for q in range(N)}
    for size in range(1,max_size+1):
        yield size,layer
        following=set()
        for s in layer:
            boundary=0
            for q in cells(s):boundary|=NB[q]
            boundary&=~s
            while boundary:
                bit=boundary&-boundary;boundary^=bit;following.add(s|bit)
        layer=following


def cat_trees(max_helpers=2,ncat=3):
    trees=collections.defaultdict(list);counts={}
    for size,sets in connected_sets(ncat+max_helpers):
        counts[size]=len(sets)
        if size<ncat:continue
        for s in sorted(sets):
            for qs in itertools.combinations(cells(s),ncat):trees[mask(qs)].append(s)
    return trees,counts


def assignments(cat,data):
    options=[[q for q in cat if q in NEIGHBORS[d]]for d in data]
    if any(not o for o in options):return
    for choice in itertools.product(*options):
        counts=collections.Counter(choice)
        wanted={3:[2,2,3],4:[1,2,2,2],5:[1,1,1,2,2],6:[1,1,1,1,1,2],7:[1]*7}[len(cat)]
        if sorted(counts.values())!=wanted:continue
        yield {q:[d for d,c in zip(data,choice)if c==q]for q in cat}


def label_data(data,groups_a,groups_b):
    triples=[set(v)for groups in (groups_a,groups_b)for v in groups.values()if len(v)==3]
    # Only the two size-three supports constrain the Steane-coordinate labels.
    for order in itertools.permutations(data):
        position={q:i+1 for i,q in enumerate(order)}
        if all(__import__('functools').reduce(int.__xor__,[position[q]for q in tri])!=0 for tri in triples):
            return list(order)
    raise AssertionError('No simultaneous nonline labeling')


def terminal(data,seconds=.25):
    dset=set(data);m=cp_model.CpModel();variables=[];choices=[]
    byq=collections.defaultdict(list)
    for i,d in enumerate(data):
        row=[]
        for a in NEIGHBORS[d]:
            if a in dset:continue
            for b in NEIGHBORS[d]:
                if b in dset or b==a:continue
                for c in NEIGHBORS[b]:
                    if c in dset or c in (a,b):continue
                    v=m.NewBoolVar(f'p{i}_{a}_{b}_{c}');row.append(v)
                    variables.append(v);choices.append((i,a,b,c))
                    for q in (a,b,c):byq[q].append(v)
        if not row:return None,'NO_LOCAL_PATH'
        m.AddExactlyOne(row)
    for vv in byq.values():m.AddAtMostOne(vv)
    occupancy={}
    for role in range(1,4):
        for q in range(N):
            vv=[v for v,ch in zip(variables,choices)if ch[role]==q]
            on=m.NewBoolVar(f'o{role}_{q}')
            if vv:m.AddMaxEquality(on,vv)
            else:m.Add(on==0)
            occupancy[role,q]=on
    nearby=[]
    for role in range(1,4):
        for q in range(N):
            for r in NEIGHBORS[q]:
                if q>=r:continue
                edge=m.NewBoolVar(f'e{role}_{q}_{r}')
                m.AddBoolAnd([occupancy[role,q],occupancy[role,r]]).OnlyEnforceIf(edge)
                m.AddBoolOr([occupancy[role,q].Not(),occupancy[role,r].Not(),edge])
                nearby.append(edge)
    m.Maximize(sum(nearby))
    s=cp_model.CpSolver();s.parameters.max_time_in_seconds=seconds;s.parameters.num_search_workers=1
    status=s.Solve(m)
    if status not in (cp_model.FEASIBLE,cp_model.OPTIMAL):return None,s.StatusName(status)
    selected=sorted(c for v,c in zip(variables,choices)if s.Value(v))
    return dict(D=data,A=[r[1]for r in selected],B=[r[2]for r in selected],C=[r[3]for r in selected]),s.StatusName(status)


def make_prep(cat,tree,t0=0):
    """Choose a root and greedily schedule growth; all tree cells are reset."""
    best=None
    qs=cells(tree)
    for root in qs:
        parent={root:None};queue=[root]
        for q in queue:
            for r in NEIGHBORS[q]:
                if tree>>r&1 and r not in parent:parent[r]=q;queue.append(r)
        assert len(parent)==len(qs)
        pending={(p,q)for q,p in parent.items()if p is not None};infected={root};layers=[]
        while pending:
            ready=[e for e in sorted(pending)if e[0]in infected]
            used=set();layer=[]
            for a,b in ready:
                if a not in used and b not in used:layer.append((a,b));used|={a,b}
            assert layer
            pending-=set(layer);infected|={b for a,b in layer};layers.append(layer)
        helpers=sorted(set(qs)-set(cat))
        operations=[dict(kind='RX'if q==root else'R',qs=[q],time=t0)for q in qs]
        for i,layer in enumerate(layers):operations.extend(dict(kind='CX',qs=list(e),time=t0+1+i)for e in layer)
        operations.extend(dict(kind='MX',qs=[q],time=t0+1+len(layers),bit=100+q)for q in helpers)
        ready=t0+1+len(layers)+int(bool(helpers))
        row=dict(cat=cat,helpers=helpers,tree=qs,root=root,cx=len(qs)-1,ready=ready,
            operations=operations,cat_x_parity_includes=[100+q for q in helpers])
        if best is None or(ready,root)<(best['ready'],best['root']):best=row
    return best


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--helpers',type=int,default=2);ap.add_argument('--limit',type=int,default=40)
    ap.add_argument('--cats',type=int,default=3);ap.add_argument('--future-data-bridges',action='store_true')
    ap.add_argument('--mixed-data',action='store_true')
    ap.add_argument('--terminal-seconds',type=float,default=.25);args=ap.parse_args();begin=time.perf_counter()
    trees,counts=cat_trees(args.helpers,args.cats);cats=[]
    for cm in sorted(trees):
        neigh=0
        for q in cells(cm):neigh|=NB[q]
        neigh&=~cm
        if neigh.bit_count()>=7:cats.append((cm,neigh))
    witnesses=[];seen_data={};stats=collections.Counter();prep_cache={}
    for i,(am,an) in enumerate(cats):
        for bm,bn in cats[i+1:]:
            if am&bm:continue
            common=an&bn
            if common.bit_count()<7:continue
            stats['cat_pairs_with_seven_common_neighbors']+=1
            for data in itertools.combinations(cells(common),7):
                dm=mask(data);stats['data_subsets']+=1
                if args.mixed_data and len({(q//6+q%6)%2 for q in data})==1:continue
                ats=[t for t in trees[am]if args.future_data_bridges or not t&dm]
                bts=[t for t in trees[bm]if args.future_data_bridges or not t&dm]
                if not ats or not bts:continue
                pair=None
                for at in ats:
                    for bt in bts:
                        # The first cat may borrow cells of the second before
                        # those cells are initialized; the reverse must be false.
                        ab=not(bt&am);ba=not(at&bm)
                        if not(ab or ba):continue
                        key=((at.bit_count()+bt.bit_count()),max(at.bit_count(),bt.bit_count()))
                        if pair is None or key<pair[0]:pair=(key,at,bt,'AB'if ab else'BA')
                if pair is None:continue
                stats['preparable_data_subsets']+=1
                aa=list(assignments(cells(am),data));bb=list(assignments(cells(bm),data))
                if not aa or not bb:continue
                stats['balanced_groupings_exist']+=1
                if dm not in seen_data:seen_data[dm]=terminal(list(data),args.terminal_seconds)
                roles,status=seen_data[dm];stats['terminal_'+status]+=1
                if roles is None:continue
                at,bt,order=pair[1:];ga,gb=aa[0],bb[0];labeled=label_data(data,ga,gb)
                mapping={q:i for i,q in enumerate(data)}
                roles={k:[roles[k][mapping[q]]for q in labeled]for k in roles}
                pa=make_prep(cells(am),at);pb=make_prep(cells(bm),bt)
                row=dict(roles=roles,cat_a=cells(am),cat_b=cells(bm),data_groups_a=ga,data_groups_b=gb,
                    prep_a=pa,prep_b=pb,preparation_order=order,
                    preparation_cx=pa['cx']+pb['cx'],data_coupling_cx=14,
                    data_must_be_initialized_after_cats=args.future_data_bridges,
                    future_data_bridges=sorted((set(pa['helpers'])|set(pb['helpers']))&set(data)),
                    scope='Native geometry and cat-preparation instrument only. Full data/resource preparations and noisy integration remain required.')
                witnesses.append(row)
                if len(witnesses)>=args.limit:break
            if len(witnesses)>=args.limit:break
        if len(witnesses)>=args.limit:break
    out=dict(cat_size=args.cats,max_helpers_per_cat=args.helpers,future_data_bridges=args.future_data_bridges,
        mixed_data_required=args.mixed_data,
        connected_sets_by_size=counts,eligible_cat_sets=len(cats),
        statistics=dict(stats),witnesses=witnesses,seconds=time.perf_counter()-begin,
        enumeration_complete=len(witnesses)<args.limit,
        source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    path=HERE/f'geometry_k{args.cats}_h{args.helpers}{"_futureD"if args.future_data_bridges else""}{"_mixed"if args.mixed_data else""}.json'
    path.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items()if k!='witnesses'}),flush=True)
    print(json.dumps(dict(witness_count=len(witnesses),first=witnesses[0]if witnesses else None)),flush=True)


if __name__=='__main__':main()
