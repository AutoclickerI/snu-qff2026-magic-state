"""Static support graph lower bounds, independent of prefix embeddings/timing.

Ancillas from different checks may coincide, so UNSAT survives any helper time
multiplexing. Does not cover moving a block between its stabilizer measurements.
"""
from mbp import *
EDGES=[(u,v) for u in range(36) for v in range(36) if abs(u//6-v//6)+abs(u%6-v%6)==1]

def solve(kinds,seconds=60,workers=1,round=True):
    m=cp_model.CpModel();cells={};cats=[]
    for k,kind in enumerate(kinds):
        qs=[m.new_int_var(0,35,f'q{k}{i}') for i in range(7)];cells[k]=qs
        m.add_all_different(qs)
        if kind=='free':continue
        selected=range(int(kind[-1])) if kind.startswith('h') else []
        if kind=='unitary':
            p=json.loads((OUT/'inputs/prepA_L5_s7307.json').read_text());old=[1,14,8,9,2,16,15]
            for L in p['ops']:
                for a,b in L:m.add_allowed_assignments([qs[old.index(a)],qs[old.index(b)]],EDGES)
            continue
        for L in gf33.LAYERS0:
            for j,(u,v) in enumerate(L):
                if j in selected:m.add_allowed_assignments([qs[u],qs[v]],EDGES)
        rows=[j for j in range(4 if kind.endswith('red') else 3) if j not in selected]
        for row in rows:
            supp=SUPPORTS[row];n=int(kind[3]) if kind.startswith('cat') else 1
            if row==3 and 'pairred' in kind:supp=sorted(set(GENS[0])^set(GENS[1]))
            aa=[m.new_int_var(0,35,f'a{k}_{row}_{j}') for j in range(n)];m.add_all_different(qs+aa)
            for u,v in zip(aa,aa[1:]):m.add_allowed_assignments([u,v],EDGES)
            use=[[] for _ in aa]
            for i in supp:
                at=m.new_int_var(0,n-1,f's{k}_{row}_{i}');anc=m.new_int_var(0,35,f't{k}_{row}_{i}');m.add_element(at,aa,anc);m.add_allowed_assignments([qs[i],anc],EDGES)
                for j in range(n):
                    b=m.new_bool_var(f'b{k}_{row}_{i}_{j}');m.add(at==j).only_enforce_if(b);m.add(at!=j).only_enforce_if(b.Not());use[j].append(b)
            for j,us in enumerate(use):m.add(sum(us)>=1);m.add(sum(us)<=4-int(j>0)-int(j+1<n))
            if kind=='cat22':m.add(sum(use[0])==2)
            cats.append(aa)
    if round:
        d=[m.new_int_var(0,35,f'd{i}') for i in range(7)];m.add_all_different(d+sum(cells.values(),[]))
        for i in range(7):
            for u,v in [(d[i],cells[0][i]),(d[i],cells[1][i]),(cells[1][i],cells[2][i])]:m.add_allowed_assignments([u,v],EDGES)
    s=cp_model.CpSolver();s.parameters.max_time_in_seconds=seconds;s.parameters.num_workers=workers;s.parameters.cp_model_presolve=False
    st=s.solve(m);r=dict(kinds=kinds,round=round,status=s.status_name(st),stats=s.response_stats())
    if st in (cp_model.OPTIMAL,cp_model.FEASIBLE):r.update(cells={k:[s.value(q) for q in qs] for k,qs in cells.items()},ancillas=[[s.value(q) for q in aa] for aa in cats])
    return r

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--seconds',type=float,default=120);p.add_argument('--workers',type=int,default=1);p.add_argument('--start',type=int,default=0);a=p.parse_args()
    cases=[([k],False) for k in ['direct','h1','h2','cat22','cat2','cat3','cat4']]
    cases +=[(list(ks),True) for ks in [('free','cat2','cat2'),('unitary','cat2','cat2'),('cat2','free','free'),('free','cat3','cat3'),('unitary','cat3','cat3'),('cat3','cat3','cat3'),('unitary','cat4','cat4')]]
    cases +=[([k],False) for k in ['cat2red','cat3red','cat2pairred']]
    rows=[]
    for index,(ks,rr) in enumerate(cases):
        name=OUT/f'geometry_{index:02d}.json'
        if index<a.start:continue
        assert os.getloadavg()[0]<os.cpu_count()
        r=solve(ks,a.seconds,a.workers,rr);name.write_text(json.dumps(r,indent=2)+'\n');rows.append(r);print(json.dumps(r),flush=True)
    (OUT/'geometry_summary.json').write_text(json.dumps(rows,indent=2)+'\n')
