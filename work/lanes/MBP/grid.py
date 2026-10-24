"""Time-expanded MB-cat placement: prefix lifetimes, data hops, reusable helpers.

Finite models reserve full quantum-state lifetimes, not merely gate instants.
The solver proposes feasible schedules; only built exact loss ranks candidates.
"""
import os,sys,json,re,itertools,argparse,time
from pathlib import Path
from mbp import *
P0={0,1,2,3,4,6,7,8,9,10,13,14,15,19,20}
D0=gf33.PRE_DATA
EDGES=[(u,v) for u in range(36) for v in range(36) if abs(u//6-v//6)+abs(u%6-v%6)==1]

def transform(sym,row,col):
    def f(q):
        r,c=divmod(q,6)
        return [(r,c),(r,5-c),(5-r,c),(5-r,5-c),(c,r),(c,5-r),(5-c,r),(5-c,5-r)][sym]
    rr=[f(q) for q in P0];mr=min(r for r,c in rr);mc=min(c for r,c in rr)
    return {q:6*(f(q)[0]-mr+row)+f(q)[1]-mc+col for q in P0}

def solve(a):
    physical();m=cp_model.CpModel();H=a.horizon
    def V(name,lo=0,hi=H+3):return m.new_int_var(lo,hi,name)
    occx=[];occt=[];gates=[]
    def occ(pos,start,end,name):
        st=V(name+'start');en=V(name+'end');m.add(st==start);m.add(en==end)
        size=V(name+'size');m.add(size==end-start)
        occx.append(m.new_fixed_size_interval_var(pos,1,name+'cell'))
        occt.append(m.new_interval_var(st,size,en,name+'life'))
    R=V('R',33,H)
    ops,d0=prefix('v22h');mp=transform(a.sym,a.row,a.col)
    pre=[];pts=[];per={}
    for i,(t,ls,tag) in enumerate(ops):
        qs=set(int(q) for s in ls for q in re.findall(r'q\[(\d+)\]',s))
        tvar=V('pre'+str(i),0,H-1);pts.append(tvar);m.add(tvar<R)
        pre.append(([re.sub(r'q\[(\d+)\]',lambda x:f'q[{mp[int(x[1])]}]',s) for s in ls],qs))
        for q in qs:per.setdefault(q,[]).append(i)
    for q,seq in per.items():
        for i,j in zip(seq,seq[1:]):m.add(pts[j]>pts[i])
        if q not in D0:
            occ(m.new_constant(mp[q]),pts[seq[0]],pts[seq[-1]]+1,'preq'+str(q))
    tokens={};jobs=[];hopbits=[];final={};cost=[]
    for i in range(7):
        key=f'D{i}';positions=[m.new_constant(mp[D0[i]])]+[V(key+f'p{j}',0,35) for j in range(1,a.hops+1)]
        initial=pts[per[D0[i]][0]];last=pts[per[D0[i]][-1]]
        starts=[initial];ends=[];moves=[]
        for j in range(a.hops):
            yes=m.new_bool_var(key+f'mv{j}');t=V(key+f't{j}');e=V(key+f'e{j}')
            m.add_allowed_assignments([positions[j],positions[j+1],yes],[(u,v,1) for u,v in EDGES]+[(q,q,0) for q in range(36)])
            m.add(t>=last+1);m.add(e==t+2*yes);m.add(e<=R)
            if moves:m.add(yes<=moves[-1][2])
            starts.append(t-yes);ends.append(e);last=e-1
            moves.append((positions[j],positions[j+1],yes,t));cost.append(yes)
        ends.append(R+3)
        for j,(st,en) in enumerate(zip(starts,ends)):occ(positions[j],st,en,key+str(j))
        tokens[key]=moves;final[key]=positions[-1]
    init={};checks=[];bper={};encjobs=[];initplus={};kinds=dict(zip('ABC',a.kinds.split(',')));prep={};bmove={};stages={};stage_moves={};checkpos={};spines={}
    template=json.loads((OUT/'inputs/prepA_L5_s7307.json').read_text());ac=[1,14,8,9,2,16,15]
    nbs={q:[v for u,v in EDGES if u==q] for q in range(36)};tree_embeddings=[]
    for q6 in range(36):
        for q0,q1,q2,anc in itertools.permutations(nbs[q6],4):
            for q4 in (set(nbs[q0])&set(nbs[anc]))-{q6}:
                for q5 in (set(nbs[q1])&set(nbs[anc]))-{q6}:
                    for q3 in nbs[anc]:
                        qs=[q0,q1,q2,q3,q4,q5,q6,anc]
                        if len(set(qs))==8:tree_embeddings.append(qs)
    assert len(tree_embeddings)==96
    spine_embeddings=[]
    for h0 in range(36):
        for h1 in nbs[h0]:
            for h2 in set(nbs[h1])-{h0}:
                for q2,q3,q6 in itertools.permutations(set(nbs[h0])-{h1},3):
                    for q1,q4 in itertools.permutations(set(nbs[h1])-{h0,h2},2):
                        for q0,q5 in itertools.permutations(set(nbs[h2])-{h1},2):
                            row=[q0,q1,q2,q3,q4,q5,q6,h0,h1,h2]
                            if len(set(row))==10:spine_embeddings.append(row)
    # All block qubits stay at their final cells; ancillas may occupy any other
    # token's cell outside its lifetime, including future C, A, and data cells.
    for k in 'ABC':
        kind=kinds[k];hybrid=2 if kind=='h2t' else int(kind[-1]) if kind[-1].isdigit() else 0
        ncat=(int(kind[3]) if kind.startswith('cat') and len(kind)>3 else 2) if kind.startswith('c') else 1
        selected=tuple(range(hybrid)) if not kind.startswith('cat') else ()
        if kind=='u':
            pluspiv={ac.index(q) for q in template['pivots']}
            piv=pluspiv if k=='A' else set(range(7))-pluspiv
            enc=[(ac.index(u),ac.index(v)) if k=='A' else (ac.index(v),ac.index(u)) for L in template['ops'] for u,v in L]
            rows=[]
        else:
            piv={gf33.PIV[i] for i in selected}
            if k=='A':piv=set(range(7))-piv
            edges=[(0,4),(1,5),(0,6),(1,6),(6,2)] if kind=='h2t' else [(u,v) for L in gf33.LAYERS0 for j,(u,v) in enumerate(L) if j in selected]
            enc=[(v,u) if k=='A' else (u,v) for u,v in edges]
            rows=[j for j in range(4 if kind.endswith('red') else 3) if j not in selected]
        for i in range(7):
            key=f'{k}{i}';p=V(key,0,35);t=V(key+'init',0,H-1)
            final[key]=p;init[key]=t;bper[key]=[];initplus[key]=i in piv
            if kind=='seqmove':
                positions=[V(key+f'stage{j}',0,35) for j in range(3)]+[p]
                moves=[];arrivals=[t];departures=[]
                for j in range(3):
                    mv=m.new_bool_var(key+f'mv{j}');mt=V(key+f'mt{j}',1,H-1);beg=V(key+f'destinit{j}');end=V(key+f'srcend{j}')
                    m.add_allowed_assignments([positions[j],positions[j+1],mv],[(u,v,1) for u,v in EDGES]+[(q,q,0) for q in range(36)])
                    m.add(mt>arrivals[-1]);m.add(beg==mt-mv);m.add(end==mt+2*mv);m.add(end<=R)
                    if j:m.add(mt>=moves[-1][4])
                    arrivals.append(beg);departures.append(end);moves.append((positions[j],positions[j+1],mv,mt,end));cost.append(mv)
                departures.append(R+(3 if k=='B' else 2))
                for j in range(4):occ(positions[j],arrivals[j],departures[j],key+f'stage{j}')
                prep[key]=positions[0];stages[key]=positions;stage_moves[key]=moves
            elif a.block_hop:
                positions=[V(key+f'pos{j}',0,35) for j in range(a.block_hops)]+[p]
                moves=[];arrivals=[t];departures=[]
                for j in range(a.block_hops):
                    mv=m.new_bool_var(key+f'mv{j}');mt=V(key+f'mt{j}',1,H-1);beg=V(key+f'destinit{j}');end=V(key+f'srcend{j}')
                    m.add_allowed_assignments([positions[j],positions[j+1],mv],[(u,v,1) for u,v in EDGES]+[(q,q,0) for q in range(36)])
                    m.add(mt>t);m.add(beg==mt-mv);m.add(end==mt+2*mv);m.add(end<=R)
                    if moves:m.add(mt>=moves[-1][4]);m.add(mv<=moves[-1][2])
                    arrivals.append(beg);departures.append(end);moves.append((positions[j],positions[j+1],mv,mt,end));cost.append(mv)
                departures.append(R+(3 if k=='B' else 2))
                for j in range(a.block_hops+1):occ(positions[j],arrivals[j],departures[j],key+f'pos{j}')
                prep[key]=positions[0];bmove[key]=moves
            else:
                prep[key]=p;occ(p,t,R+(3 if k=='B' else 2),key)
        last={i:init[f'{k}{i}'] for i in range(7)}
        if kind=='u':m.add_allowed_assignments([prep[f'{k}{i}'] for i in range(7)],json.loads((OUT/'inputs/l5_11.embeddings.json').read_text()))
        for j,(u,v) in enumerate(enc):
            t=V(k+f'enc{j}',1,H-1);m.add(t>last[u]);m.add(t>last[v]);last[u]=last[v]=t;m.add(t<R)
            pu,pv=prep[f'{k}{u}'],prep[f'{k}{v}'];m.add_allowed_assignments([pu,pv],EDGES)
            encjobs.append((k,pu,pv,t));bper[f'{k}{u}'].append(t);bper[f'{k}{v}'].append(t)
        for row in rows:
            supp=SUPPORTS[row];key=f'{k}s{row}';aa=[V(key+f'a{j}',0,35) for j in range(ncat)]
            if 'spine' in kind:
                if k in spines:
                    for x,y in zip(aa,spines[k]):m.add(x==y)
                else:
                    spines[k]=aa
                    m.add_allowed_assignments([prep[f'{k}{i}'] for i in range(7)]+aa,spine_embeddings)
            if kind=='h2t':m.add_allowed_assignments([prep[f'{k}{i}'] for i in range(7)]+aa,tree_embeddings)
            m.add_all_different(aa)
            for u,v in zip(aa,aa[1:]):m.add_allowed_assignments([u,v],EDGES)
            ti=[V(key+f'i{j}',0,H-2) for j in range(ncat)];tc=[V(key+f'cat{j}',1,H-2) for j in range(ncat-1)];tm=[V(key+f'm{j}',1,H-1) for j in range(ncat)]
            for j,t in enumerate(tc):
                m.add(t>ti[j]);m.add(t>ti[j+1])
                if j:m.add(t>tc[j-1])
            for j in range(ncat):
                m.add(tm[j]>ti[j]);m.add(tm[j]<R);occ(aa[j],ti[j],tm[j]+1,key+f'anc{j}')
                for t in tc:m.add(tm[j]>t)
            sides=[];couples=[]
            for i in supp:
                side=V(key+f'side{i}',0,ncat-1);anc=V(key+f'target{i}',0,35);t=V(key+f't{i}',1,H-1)
                if 'spine' in kind:m.add(side==({2:0,3:0,6:0,1:1,4:1,0:2,5:2}[i]))
                pp=stages[f'{k}{i}'][row] if kind=='seqmove' else prep[f'{k}{i}'];checkpos[(k,row,i)]=pp
                m.add_element(side,aa,anc);m.add_allowed_assignments([pp,anc],EDGES)
                for ct in tc:m.add(t>ct)
                for it in ti:m.add(t>it)
                for et in last.values():m.add(t>et)
                if kind=='seqmove':
                    for z in range(7):
                        if row:m.add(t>=stage_moves[f'{k}{z}'][row-1][4])
                        m.add(t<stage_moves[f'{k}{z}'][row][3])
                flags=[]
                for j in range(ncat):
                    yes=m.new_bool_var(key+f'at{i}_{j}');m.add(side==j).only_enforce_if(yes);m.add(side!=j).only_enforce_if(yes.Not());m.add(t<tm[j]).only_enforce_if(yes);flags.append(yes)
                sides.append(side);couples.append((i,side,anc,t));bper[f'{k}{i}'].append(t)
            for j in range(ncat):
                uses=[]
                for i,side,_,t in couples:
                    yes=m.new_bool_var(key+f'uses{i}_{j}');m.add(side==j).only_enforce_if(yes);m.add(side!=j).only_enforce_if(yes.Not());uses.append(yes)
                m.add(sum(uses)>=1);m.add(sum(uses)<=4-(int(j>0)+int(j+1<ncat)))
            # The two interactions at each member need distinct steps.
            for (i,si,_,t),(j,sj,_,u) in itertools.combinations(couples,2):
                same=m.new_bool_var(key+f'eq{i}_{j}');m.add(si==sj).only_enforce_if(same);m.add(si!=sj).only_enforce_if(same.Not());m.add(t!=u).only_enforce_if(same)
            checks.append((k,row,aa,ti,tc,tm,couples))
    for key,ts in bper.items():
        m.add_all_different(ts)
        if key in bmove:
            for t in ts:m.add(t<bmove[key][0][3])
    m.add_all_different(list(final.values()))
    perms={};partners={}
    autos=[]
    for aa in range(1,8):
        for bb in range(1,8):
            for cc in range(1,8):
                pp=[((aa if i&1 else 0)^(bb if i&2 else 0)^(cc if i&4 else 0))-1 for i in range(1,8)]
                if sorted(pp)==list(range(7)):autos.append(pp)
    for k in 'ABC':
        pp=[V(k+f'perm{i}',0,6) for i in range(7)]
        if a.automorphisms:m.add_allowed_assignments(pp,autos)
        else:
            for i,x in enumerate(pp):m.add(x==i)
        perms[k]=pp;partners[k]=[V(k+f'partner{i}',0,35) for i in range(7)]
        for i in range(7):m.add_element(pp[i],[final[f'{k}{j}'] for j in range(7)],partners[k][i])
    for i in range(7):
        m.add_allowed_assignments([final[f'D{i}'],partners['A'][i]],EDGES)
        m.add_allowed_assignments([final[f'D{i}'],partners['B'][i]],EDGES)
        m.add_allowed_assignments([partners['B'][i],partners['C'][i]],EDGES)
    if a.fixed_final:
        targets={'D':[0,20,7,10,3,22,21],'A':[1,14,8,9,2,16,15],'B':[6,26,13,11,4,23,27],'C':[12,25,19,17,5,29,28]}
        for i in range(7):
            m.add(final[f'D{i}']==targets['D'][i])
            for k in 'ABC':m.add(partners[k][i]==targets[k][i])
    m.add_no_overlap_2d(occx,occt)
    # First feasible solves only. A surrogate chooses diverse compact starts;
    # actual selection uses exact third-order after QASM reconstruction.
    m.minimize(50*R+5*sum(cost)+sum(R-t for t in init.values())+sum(R-t for t in pts))
    s=cp_model.CpSolver();s.parameters.num_workers=a.workers;s.parameters.max_time_in_seconds=a.seconds;s.parameters.random_seed=a.seed;s.parameters.cp_model_presolve=False
    name=OUT/a.name
    class CB(cp_model.CpSolverSolutionCallback):
        def on_solution_callback(self):
            qasm,meta=build(self);name.with_suffix('.qasm').write_text(qasm);name.with_suffix('.json').write_text(json.dumps(meta,indent=2)+'\n')
            print('FEASIBLE',self.value(R),self.objective_value,self.wall_time,flush=True)
            if a.first:self.stop_search()
    def build(sol):
        oo=[]
        for (ls,qs),t in zip(pre,pts):oo.append((sol.value(t),ls,'pre'))
        rr=sol.value(R);dets=prefix_detectors('v22h')
        for i in range(7):
            for src,dst,yes,t in tokens[f'D{i}']:
                if not sol.value(yes):continue
                p,q,tt=sol.value(src),sol.value(dst),sol.value(t)
                oo += [(tt-1,[f'reset q[{q}];'],'hop'),(tt,[f'cx q[{p}],q[{q}];'],'hop'),(tt+1,[f'cx q[{q}],q[{p}];'],'hop')]
        for key,t in init.items():
            p=sol.value(prep[key]);oo.append((sol.value(t),[f'reset q[{p}];']+([f'h q[{p}];'] if initplus[key] else []),key[0]))
        for k,pu,pv,t in encjobs:oo.append((sol.value(t),[f'cx q[{sol.value(pu)}],q[{sol.value(pv)}];'],k))
        bit=60;frames={k:[[],[],[],[]] for k in 'ABC'}
        for k,row,aa,ti,tc,tm,couples in checks:
            av=[sol.value(x) for x in aa]
            for j in range(len(aa)):
                q=av[j];oo.append((sol.value(ti[j]),[f'reset q[{q}];']+([f'h q[{q}];'] if (j==0)!=(k=='A') else []),k))
            for j,t in enumerate(tc):
                u,v=av[j:j+2]
                if k=='A':u,v=v,u
                oo.append((sol.value(t),[f'cx q[{u}],q[{v}];'],k))
            for i,side,anc,t in couples:
                p,q=sol.value(checkpos[(k,row,i)]),sol.value(anc)
                if k!='A':p,q=q,p
                oo.append((sol.value(t),[f'cx q[{p}],q[{q}];'],k))
            for j in range(len(aa)):
                q=av[j];oo.append((sol.value(tm[j]),([] if k=='A' else [f'h q[{q}];'])+[f'measure q[{q}] -> c[{bit}];'],k));frames[k][row].append(bit);bit+=1
        for k in 'ABC':
            if kinds[k].endswith('red'):dets.append(sum(frames[k],[]))
        for key,moves in bmove.items():
            for src,dst,mv,mt,end in moves:
                if not sol.value(mv):continue
                u,v,t=sol.value(src),sol.value(dst),sol.value(mt);k=key[0];i=int(key[1:]);plus=k=='A'
                oo.append((t-1,[f'reset q[{v}];']+([f'h q[{v}];'] if plus else []),k))
                p,q=(v,u) if plus else (u,v);oo.append((t,[f'cx q[{p}],q[{q}];'],k))
                oo.append((t+1,([] if plus else [f'h q[{u}];'])+[f'measure q[{u}] -> c[{bit}];'],k))
                for j,ss in enumerate(GENS):
                    if i in ss:frames[k][j].append(bit)
                bit+=1
        for key,moves in stage_moves.items():
            for stage,(src,dst,mv,mt,end) in enumerate(moves):
                if not sol.value(mv):continue
                u,v,t=sol.value(src),sol.value(dst),sol.value(mt);k=key[0];i=int(key[1:]);plus=k=='A'
                oo.append((t-1,[f'reset q[{v}];']+([f'h q[{v}];'] if plus else []),k))
                p,q=(v,u) if plus else (u,v);oo.append((t,[f'cx q[{p}],q[{q}];'],k))
                oo.append((t+1,([] if plus else [f'h q[{u}];'])+[f'measure q[{u}] -> c[{bit}];'],k))
                for j,ss in enumerate(GENS):
                    if j<=stage and i in ss:frames[k][j].append(bit)
                bit+=1
        for i in range(7):
            d=sol.value(final[f'D{i}']);aa,b,c=[sol.value(partners[k][i]) for k in 'ABC']
            oo += [(rr,[f'cx q[{d}],q[{aa}];'],'round'),(rr,[f'cx q[{b}],q[{c}];'],'round'),(rr+1,[f'cx q[{b}],q[{d}];'],'round'),
                   (rr+1,[f'measure q[{aa}] -> c[{14+i}];'],'round'),(rr+1,[f'measure q[{c}] -> c[{21+i}];'],'round'),(rr+2,[f'h q[{b}];',f'measure q[{b}] -> c[{28+i}];'],'round')]
        def frame_for(k,ss):
            target={sol.value(perms[k][i]) for i in ss}
            for mask in range(8):
                support=set();bits=set()
                for j in range(3):
                    if mask>>j&1:support^=set(GENS[j]);bits^=set(frames[k][j])
                if support==target:return sorted(bits)
            raise AssertionError(target)
        for j,ss in enumerate(GENS):dets += [[14+i for i in ss]+frame_for('A',ss),[28+i for i in ss]+frame_for('B',ss)+frame_for('C',ss),[21+i for i in ss]]
        dets.append(list(range(21,28)));text,tags=emit(oo,dets,36)
        return text,dict(data_qubits=[sol.value(final[f'D{i}']) for i in range(7)],kind='physical_'+a.kinds,R=rr,cx=text.count('cx '),n_qubits=36,line_regions=tags,args=vars(a),placement={k:[sol.value(final[f'{k}{i}']) for i in range(7)] for k in 'DABC'})
    status=s.solve(m,CB());receipt=dict(status=s.status_name(status),stats=s.response_stats(),args=vars(a))
    name.with_suffix('.receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
    if status in (cp_model.OPTIMAL,cp_model.FEASIBLE):
        text,meta=build(s);row=price(text,meta,procs=a.workers);name.with_suffix('.result.json').write_text(json.dumps(dict(meta,**row),indent=2)+'\n');print(json.dumps(row),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('name');p.add_argument('--kinds',default='c0,c0,c0');p.add_argument('--block-hop',action='store_true');p.add_argument('--block-hops',type=int,default=1);p.add_argument('--automorphisms',action='store_true');p.add_argument('--fixed-final',action='store_true');p.add_argument('--sym',type=int,default=0);p.add_argument('--row',type=int,default=0);p.add_argument('--col',type=int,default=0);p.add_argument('--horizon',type=int,default=60);p.add_argument('--hops',type=int,default=2);p.add_argument('--seconds',type=float,default=600);p.add_argument('--workers',type=int,default=4);p.add_argument('--seed',type=int,default=0);p.add_argument('--first',action='store_true');solve(p.parse_args())
