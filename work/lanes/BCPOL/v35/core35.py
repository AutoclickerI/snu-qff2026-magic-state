"""Native B/C rewrites of frozen v35a; preserves every unselected operation."""
import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
V=Path(__file__).resolve().parent;H=V.parent;ROOT=H.parents[2]
os.environ.setdefault('XTIM_TWIRL_CACHE_DIR',str(H/'.xtim_cache'))
sys.path[:0]=[str(V),str(H),str(ROOT/'work/lanes/EVAL')]
import schedule as S
from util import native_times
from cache import setup
from boundary_api import AllOrdersCache,PreparedRegion
import exact2
import wide_masks
import json,re,copy,hashlib,collections,time,random
B=[6,26,13,11,4,23,27];C=[12,25,19,17,5,29,28];BC=set(B+C)
def bit(u):return int(re.search(r'c\[(\d+)\]',' '.join(u.lines))[1])
def edge(u):return tuple(map(int,re.findall(r'q\[(\d+)\]',u.lines[0])))
def load(stem=None):
    stem=Path(stem or V/'inputs/v35a');text=stem.with_suffix('.qasm').read_text();md=json.loads(stem.with_suffix('.json').read_text());head,raw,tail=S.qasm_ops(text);us=S.fold_units(raw);ts=native_times(text,us)
    return dict(head=head,us=us,ts=ts,tail=tail,md=md,source=str(stem))
def init_indices(c):
    return {q:next(i for i,u in enumerate(c['us']) if u.qs==(q,) and c['ts'][i]==c['md']['init_times'][str(q)] and u.name in ('RESET','RX','MEASURE','MX')) for q in BC}
def prep_indices(c):
    init=init_indices(c)
    return [i for i,u in enumerate(c['us']) if u.name=='CX' and set(u.qs)<=BC and c['ts'][i]<c['md']['R'] and all(c['ts'][i]>c['ts'][init[q]] for q in u.qs)]
def seed(c,joint=False):
    ix=prep_indices(c);assert ix
    if joint:ix += [i for i,u in enumerate(c['us']) if u.name=='CX' and edge(u) in list(zip(B,C)) and c['ts'][i]==44]
    lo=min(c['ts'][i] for i in ix);hi=max(c['ts'][i] for i in ix)
    return dict(ops=[[list(edge(c['us'][i])) for i in ix if c['ts'][i]==t] for t in range(lo,hi+1)],pivots=[q for q,i in init_indices(c).items() if c['us'][i].name in ('MX','RX')],cells=B+C,start=lo,joint=joint)
def emit(c,stem=None,recipe=None):
    head,us,ts,tail=c['head'],c['us'],c['ts'],c['tail'];order=sorted(range(len(us)),key=lambda i:(ts[i],i))
    per=collections.defaultdict(set)
    for i in order:
        for q in us[i].qs:assert ts[i] not in per[q],('native collision',q,ts[i]);per[q].add(ts[i])
    text=S.emit(head,us,ts,tail);_,raw,_=S.qasm_ops(text);nu=S.fold_units(raw);nt=native_times(text,nu)
    assert [us[i].lines for i in order]==[u.lines for u in nu],'native folding changed'
    assert [ts[i] for i in order]==nt,'native timing changed'
    md=dict(data_qubits=c['md']['data_qubits'],R=c['md']['R'],init_times=c['md']['init_times'],region_qubits=B+C,boundary_step=c['md']['R']+1,source=c['source'],recipe=recipe or {},CX=sum(u.name=='CX' for u in us),native_depth=max(ts)+1,qasm_sha256=hashlib.sha256(text.encode()).hexdigest())
    if stem:
        stem=Path(stem);stem.with_suffix('.qasm').write_text(text);stem.with_suffix('.json').write_text(json.dumps(md,indent=2)+'\n')
    return text,md
def region(stem):
    ev,b,ks,prep,ext,hh=setup(Path(stem))
    return PreparedRegion(hh,tuple(tuple((int(k),float(ev.fp[i])) for i,k in items) for items in prep.values()),len(ks)),ev
def frame_corrections(c):
    init=init_indices(c);fi={i:(q,bit(c['us'][i])) for q,i in init.items() if c['us'][i].name=='MX'}
    frames={q:[set(),set()] for q in range(36)};corr={}
    for i in sorted(range(len(c['us'])),key=lambda i:(c['ts'][i],i)):
        u=c['us'][i]
        if i in fi:q,b=fi[i];frames[q]=[set(),{b}];continue
        if u.name in ('RESET','RX'):frames[u.qs[0]]=[set(),set()]
        elif u.name=='CX':a,b=edge(u);frames[b][0]^=frames[a][0];frames[a][1]^=frames[b][1]
        elif u.name in ('MEASURE','MX'):corr[bit(u)]=frames[u.qs[0]][u.name=='MX'].copy()
        elif u.name=='H':frames[u.qs[0]].reverse()
        elif any(any(frames[q]) for q in u.qs):raise ValueError('non-Clifford frame crossing')
    assert all(not any(frames[q]) for q in c['md']['data_qubits'])
    return corr
def reframe(c,old_circuit):
    # Remove only the old propagated correction, then add the new one.
    # Initial MX records can also be real guard flags; deleting all occurrences
    # of those records silently loses such a detector.
    previous=frame_corrections(old_circuit);current=frame_corrections(c)
    records={bit(u) for u in c['us'] if u.name in ('MX','MEASURE')}
    out=[]
    for line in c['tail']:
        if line.startswith('// DETECTOR'):
            bs=set(map(int,re.findall(r'c\[(\d+)\]',line)));logical=bs.copy()
            for b in bs:logical^=previous.get(b,set())
            new=logical.copy()
            for b in logical:new^=current.get(b,set())
            assert new and new<=records,('detector requires removed record',line,new-records)
            line='// DETECTOR '+' '.join(f'c[{b}]' for b in sorted(new))
        out.append(line)
    c['tail']=out;return c
def replace_encoder(base,d):
    c=copy.deepcopy(base);drop=set(prep_indices(c));keep=[i for i in range(len(c['us'])) if i not in drop]
    if d.get('joint'):
        drop|={i for i,u in enumerate(c['us']) if u.name=='CX' and edge(u) in list(zip(B,C)) and c['ts'][i]==44};keep=[i for i in range(len(c['us'])) if i not in drop]
    c['us']=[c['us'][i] for i in keep];c['ts']=[c['ts'][i] for i in keep]
    for t,layer in enumerate(d['ops']):
        for a,b in layer:c['us'].append(S.Unit([f'cx q[{a}],q[{b}];'],[]));c['ts'].append(d.get('start',33)+t)
    return reframe(c,base)
def instrument(base,q,mode):
    c=copy.deepcopy(base);ix=init_indices(c);i=ix[q];u=c['us'][i]
    pivot=u.name in ('MX','RX');b=bit(u) if u.name in ('MX','MEASURE') else 400+q
    if mode=='reset':lines=[f'reset q[{q}];']+([f'h q[{q}];'] if pivot else [])
    else:lines=([f'h q[{q}];'] if pivot else [])+[f'measure q[{q}] -> c[{b}];']+([f'h q[{q}];'] if pivot else [])
    c['us'][i]=S.Unit(lines,[])
    if not pivot:
        c['tail']=[line for line in c['tail'] if line.strip()!=f'// DETECTOR c[{b}]']
        if mode=='measure':c['tail'].append(f'// DETECTOR c[{b}]')
    c['head']=[re.sub(r'creg c\[\d+\]','creg c[512]',s) for s in c['head']]
    return reframe(c,base)
def readout(base,dropmask=0,network=()):
    c=copy.deepcopy(base);copies=[(19,18,265),(25,31,266),(29,35,267),(28,34,268)];drop=set();removed=set()
    for j,(a,b,rec) in enumerate(copies):
        if dropmask>>j&1:
            removed.add(rec)
            for i,u in enumerate(c['us']):
                if b in u.qs and c['ts'][i]>=44:drop.add(i)
    c['us']=[u for i,u in enumerate(c['us']) if i not in drop];c['ts']=[t for i,t in enumerate(c['ts']) if i not in drop]
    c['tail']=[l for l in c['tail'] if not (set(map(int,re.findall(r'c\[(\d+)\]',l)))&removed)]
    # Same conjugation as COMP29/decoder34.py, confined to the C Z readouts.
    reads={u.qs[0]:i for i,u in enumerate(c['us']) if u.name=='MEASURE' and c['ts'][i]>=45 and u.qs[0] in C}
    rb={q:bit(c['us'][i]) for q,i in reads.items()};cols={q:{j for j,line in enumerate(c['tail']) if rb[q] in map(int,re.findall(r'c\[(\d+)\]',line))} for q in C}
    for a,b in network:cols[a]^=cols[b]
    for j,line in enumerate(c['tail']):
        bs=set(map(int,re.findall(r'c\[(\d+)\]',line)))-set(rb.values());bs|={rb[q] for q in C if j in cols[q]};c['tail'][j]='// DETECTOR '+' '.join(f'c[{b}]' for b in sorted(bs))
    affected={q for e in network for q in e};rr={reads[q] for q in affected};uu=[u for i,u in enumerate(c['us']) if i not in rr];tt=[t for i,t in enumerate(c['ts']) if i not in rr];free={q:max([t for u,t in zip(uu,tt) if q in u.qs],default=-1)+1 for q in affected}
    for a,b in network:t=max(free[a],free[b]);uu.append(S.Unit([f'cx q[{a}],q[{b}];'],[]));tt.append(t);free[a]=free[b]=t+1
    for q in affected:uu.append(S.Unit([f'measure q[{q}] -> c[{rb[q]}];'],[]));tt.append(free[q])
    c['us']=uu;c['ts']=tt;return c
