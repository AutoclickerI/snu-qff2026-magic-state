"""Complete native circuit rebuilding after a free-placement phase completion.

Preserve every classical record and all r3/A operations. Re-synthesize nonlocal
CXs as exact dirty-ancilla bridges, absorb a relocated output into an existing
known-zero data hop when possible, then solve the full downstream timing model.
"""
import os,sys,json,copy,re,collections,itertools,hashlib
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
sys.dont_write_bytecode=True
from ortools.sat.python import cp_model
H=Path(__file__).resolve().parent
sys.path.insert(0,str(H.parent/'INTEG'))
import lib
lib.C=H/'builds'
from lifetime import commute
D=lib.D
CORE={(24,8,7),(25,8,14),(26,2,8)}
DROP={(23,14,15),(24,14,15)}|{(t,9,10) for t in range(24,28)}
def edge(o):
    u=lib.unit(o)
    if u.name!='CX':return None
    return (o['t'],*map(int,re.findall(r'q\[(\d+)\]',' '.join(o['lines']))))
def shortest(a,b):
    if a==b:return [[a]]
    paths=[[a]]
    while paths:
        nxt=[];out=[]
        for p in paths:
            for q in range(36):
                if abs(q//6-p[-1]//6)+abs(q%6-p[-1]%6)!=1:continue
                if abs(q//6-b//6)+abs(q%6-b%6)>=abs(p[-1]//6-b//6)+abs(p[-1]%6-b%6):continue
                if q==b:out.append(p+[q])
                else:nxt.append(p+[q])
        if out:return out
        paths=nxt
def bridge(path):
    es=list(zip(path,path[1:]));d=len(es)
    if d==1:return es
    return es+es[-2::-1]+es[1:]+es[-2:0:-1]
def timing(ops,name,seconds=30,pin=23):
    m=cp_model.CpModel();ts=[];last=collections.defaultdict(list);edges=[];nodes=[];hintlast={}
    upper=max(100,len(ops));end=m.new_int_var(0,upper,'end')
    for i,o in enumerate(ops):
        v=m.new_int_var(0,upper,f't{i}');ts.append(v);u=lib.unit(o)
        if o.get('fixed'):m.add(v==o['t'])
        else:m.add(v>=pin+1)
        nq=list(map(int,re.findall(r'q\[(\d+)\]',o['lines'][0])))
        node=dict(qs=nq,kind={'RESET':'R','MEASURE':'M'}.get(u.name,u.name))
        prev=set(j for q in u.qs for j in last[q])
        for j in prev:
            if not commute(nodes[j],node):m.add(v>ts[j]);edges.append((j,i))
        nodes.append(node)
        for q in u.qs:last[q].append(i)
        m.add(end>=v)
        hint=o['t'] if o.get('fixed') else max([pin+1,o['t']]+[hintlast.get(q,-1)+1 for q in u.qs])
        m.add_hint(v,min(upper,hint))
        for q in u.qs:hintlast[q]=hint
    for seq in last.values():m.add_all_different([ts[i] for i in seq])
    # Minimize true circuit end first; preserve incumbent timing when slack remains.
    dev=[]
    for i,o in enumerate(ops):
        z=m.new_int_var(0,upper,'d');m.add_abs_equality(z,ts[i]-o['t']);dev.append(z)
    m.minimize(end*1000000+sum(dev))
    s=cp_model.CpSolver();s.parameters.num_search_workers=1;s.parameters.max_time_in_seconds=seconds
    status=s.solve(m);assert status in (cp_model.OPTIMAL,cp_model.FEASIBLE),s.status_name(status)
    new=copy.deepcopy(ops)
    for i,o in enumerate(new):o['t']=s.value(ts[i]);o.pop('fixed',None)
    info=dict(status=s.status_name(status),seconds=s.wall_time,objective=s.objective_value,
              bound=s.best_objective_bound,depth=s.value(end)+1,dependencies=len(edges))
    (H/'logs'/f'{name}_timing.json').write_text(json.dumps(info,indent=2))
    return new,info
def generate(comp,name,route='bridge',retime=True,seconds=30):
    base=lib.read(H/'builds/roundtrip');ops=[];mapping={i:i for i in range(36)}
    for i,o in enumerate(base['ops']):o.update(original_index=i,nominal_t=o['t'])
    mapping.update({int(a):b for a,b in comp['permutation'].items()})
    prefix=[];suffix=[];stats=dict(removed_guards=6,completion_cx=comp['cx'],bridges=[],absorbed_hops=[])
    for o in base['ops']:
        if edge(o) in CORE|DROP:continue
        if o['t']<=23:prefix.append(dict(o,fixed=True))
        else:suffix.append(copy.deepcopy(o))
    if route=='rebind':
        bounds={1:37,14:37,8:35,9:37,2:35,16:37,15:39}
        aops=[];roundops=[];source=[]
        for o in suffix:
            if o['t']>=43:roundops.append(dict(o,rebind=True))
            elif any(q in bounds and o['t']>bounds[q] for q in lib.unit(o).qs):aops.append(dict(o,rebind=True))
            else:source.append(o)
        # A14 reused the old cat's X measurement. A placement exchange may
        # bring a Z-measured zero to physical14 instead; prepare the required
        # plus state explicitly, pricing its reset and new release dependency.
        if mapping[14]!=14:aops.insert(0,dict(t=37,nominal_t=37,lines=['reset q[14];','h q[14];'],rebind=True,stage='A_extra_init'))
        suffix=source+aops+roundops
        stats['A_rebind']=dict(boundary_records=[64,12,54,56,67,55,57],physical_cells=[1,14,8,9,2,16,15],extra_RX14=mapping[14]!=14)
    ops.extend(prefix)
    for j,(a,b) in enumerate(comp['gates']):ops.append(dict(t=24+j,lines=[f'cx q[{a}],q[{b}];'],stage='completion'))
    skip=set();avail={q:23 for q in range(36)}
    for o in ops:
        for q in lib.unit(o).qs:avail[q]=max(avail[q],o['t'])
    for o in suffix:
        ed=edge(o)
        if ed in skip:continue
        if ed==(33,8,9) and mapping[8]==9 and mapping[9]==8:
            mapping[8],mapping[9]=mapping[9],mapping[8];skip.add((34,9,8));stats['absorbed_hops'].append([8,9]);continue
        logicalqs=list(map(int,re.findall(r'q\[(\d+)\]',o['lines'][0])))
        if o.pop('rebind',False):
            o.setdefault('stage','A_rebind' if o['nominal_t']<43 else 'round')
            ops.append(o)
            continue
        if route=='restore' and ed is not None:
            a,b=[mapping[q] for q in logicalqs]
            if abs(a//6-b//6)+abs(a%6-b%6)!=1:
                # Restore only the required token. Exact SWAPs update the full
                # mapping, then the downstream native graph is rebuilt afresh.
                for logical in logicalqs:
                    physical=mapping[logical]
                    if physical==logical:continue
                    path=min(shortest(physical,logical),key=lambda p:sum(avail[q] for q in p))
                    for x,y in zip(path,path[1:]):
                        for c,d in [(x,y),(y,x),(x,y)]:ops.append(dict(t=o['t'],lines=[f'cx q[{c}],q[{d}];'],stage='restore'))
                        for token,cell in list(mapping.items()):
                            if cell==x:mapping[token]=y
                            elif cell==y:mapping[token]=x
                    stats.setdefault('restorations',[]).append(dict(logical=logical,path=path,before=list(ed)))
        o['lines']=[re.sub(r'q\[(\d+)\]',lambda m:f'q[{mapping[int(m[1])]}]',ln) for ln in o['lines']]
        if ed is None:ops.append(o);avail[lib.unit(o).qs[0]]=max(avail[lib.unit(o).qs[0]],o['t']);continue
        a,b=map(int,re.findall(r'q\[(\d+)\]',o['lines'][0]));paths=shortest(a,b)
        def cost(p):
            aa=avail.copy()
            for c,d in bridge(p):aa[c]=aa[d]=max(aa[c],aa[d],o['t']-1)+1
            return max(aa.values()),sum(aa.values()),p
        path=min(paths,key=cost);es=bridge(path)
        if len(es)>1:stats['bridges'].append(dict(original=list(ed),mapped=[a,b],path=path,cx=len(es)))
        for j,(c,d) in enumerate(es):
            ops.append(dict(t=o['t']+j,lines=[f'cx q[{c}],q[{d}];'],stage='bridge' if len(es)>1 else 'suffix',nominal_t=o['nominal_t'],original_index=o['original_index']))
            avail[c]=avail[d]=max(avail[c],avail[d],o['t']-1)+1
    if retime:ops,ti=timing(ops,name,seconds=seconds)
    else:ti={}
    base['ops']=ops;base['meta']=dict(data_qubits=[mapping[q] for q in D],source=f'COMPLETE state-specific phase completion, downstream {route} routing and timing',completion=comp,build=stats,timing=ti)
    lib.fix(base);st=lib.save(base,name)
    return st
def archive():
    data=json.loads((H/'completions.json').read_text());profiles=[];seen=set()
    for c in data['completions']:
        rel={q:24 for q in data['cells']}
        for j,e in enumerate(c['gates']):
            for q in e:rel[q]=25+j
        v=tuple(rel[q] for q in data['cells'])
        if v in seen:continue
        seen.add(v);profiles.append(dict(id=f'p{len(profiles):02}',release=rel,completion=c))
        if len(profiles)==30:break
    assert len(profiles)>=20,len(profiles)
    (H/'archive.json').write_text(json.dumps(dict(window=[24,26],profiles=profiles,selection='Distinct cell-by-final-completion-use vectors; no fixed-suffix loss pruning'),indent=2))
    return profiles
if __name__=='__main__':
    archive();cs=json.loads((H/'completions.json').read_text())['completions']
    for p in [(8,8),(8,2),(8,14),(8,9)]:
        c=next(c for c in cs if {int(a):b for a,b in c['permutation'].items()}=={q:(p[1] if q==p[0] else p[0] if q==p[1] else q) for q in [2,7,8,9,14]})
        print(generate(c,f'swap{p[0]}_{p[1]}'),flush=True)
