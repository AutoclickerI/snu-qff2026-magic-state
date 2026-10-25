"""Operation/lifetime model of the complete incumbent, including the correlated r3.

All native instructions and classical records survive the round trip. A lifetime
starts at a reset, or implicit initialization; measurement followed by reuse is
part of that lifetime. Locations and times are explicit CP-SAT variables.
"""
import copy, hashlib, json, re
from pathlib import Path
from ortools.sat.python import cp_model
from qedit import Circ, QRE, CRE

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
D=[0,20,7,10,3,22,21]; A=[1,14,8,9,2,16,15]
B=[6,26,13,11,4,23,27]; C=[12,25,19,17,5,29,28]
RELEASE_BITS=[64,67,54,55,56,57,8,12,274,280,45]

def classify(g):
    s=g[0]; qs=tuple(map(int,QRE.findall(s)))
    bit=next((int(CRE.search(x).group(1)) for x in g if x.startswith('measure')),None)
    kind='MX' if s.startswith('h ') and bit is not None else 'RX' if s.startswith('reset') and len(g)>1 else {'reset':'R','measure':'M','cx':'CX','t':'T','tdg':'TDG'}.get(s.split()[0],s.split()[0].upper())
    return kind,qs,bit

def nodes(c):
    out=[]
    for t,seg in enumerate(c.segs):
        for g in seg:
            kind,qs,bit=classify(g)
            out.append(dict(id=len(out),t=t,qs=list(qs),kind=kind,bit=bit,lines=g[:]))
    return out

def commute(x,y):
    if not set(x['qs'])&set(y['qs']): return True
    k,l=x['kind'],y['kind']
    if k==l=='CX': return x['qs'][0]!=y['qs'][1] and x['qs'][1]!=y['qs'][0]
    if l=='CX': x,y=y,x;k,l=l,k
    if k=='CX':
        if l in ('T','TDG','S','SDG','Z','M'): return y['qs'][0]==x['qs'][0]
        if l in ('X','MX'): return y['qs'][0]==x['qs'][1]
    return k in ('T','TDG','S','SDG','Z','M') and l in ('T','TDG','S','SDG','Z','M')

def save(c,name,change,meta=None):
    p=HERE/'builds'/name
    p.with_suffix('.qasm').write_text(c.text())
    md=dict(data_qubits=D,iface_change=change)
    if meta:md.update(meta)
    p.with_suffix('.json').write_text(json.dumps(md,indent=2)+'\n')
    return p

def profile(c):
    ns=nodes(c)
    records={str(x['bit']):dict(t=x['t'],q=x['qs'][0],basis=x['kind']) for x in ns if x['bit'] is not None}
    return dict(source_release={str(b):records[str(b)]['t']+1 for b in RELEASE_BITS if str(b) in records},
                data_qubits=D,records=records,
                occupancy={str(q):[x['t'] for x in ns if q in x['qs']] for q in range(36)},
                late_spare_cells=[q for q in range(36) if not any(q in x['qs'] and 33<=x['t']<=44 for x in ns)])

def lifetime_model(c):
    ns=nodes(c); lives=[];current={}
    for x in ns:
        x['lifetimes']=[]
        for q in x['qs']:
            if q not in current or x['kind'] in ('R','RX'):
                current[q]=len(lives);lives.append(dict(id=len(lives),cell=q,begin=x['t'],end=x['t'],nodes=[]))
            j=current[q];lives[j]['end']=x['t'];lives[j]['nodes'].append(x['id']);x['lifetimes'].append(j)
    r3=json.loads((ROOT/'work/lanes/BFLAG/syn/r3.json').read_text())
    r3_ids=[]
    for dt,es in enumerate(r3['ops']):
        for e in es:
            match=[x for x in ns if x['t']==r3['T0']+dt and x['qs']==e and x['kind']=='CX']
            assert len(match)==1,(dt,e);r3_ids.append(match[0]['id'])
    m=cp_model.CpModel(); tv=[];pv=[]
    for life in lives:
        v=m.NewIntVar(0,35,f"cell{life['id']}");m.Add(v==life['cell']);pv.append(v)
    adjacent=[(i,j) for i in range(36) for j in range(36) if abs(i//6-j//6)+abs(i%6-j%6)==1]
    for x in ns:
        v=m.NewIntVar(0,46,f"time{x['id']}");m.Add(v==x['t']);tv.append(v)
        if x['kind']=='CX':m.AddAllowedAssignments([pv[j] for j in x['lifetimes']],adjacent)
    for q in range(36):m.AddAllDifferent([tv[x['id']] for x in ns if q in x['qs']])
    for i,x in enumerate(ns):
        for y in ns[:i]:
            if not commute(x,y):m.Add(tv[x['id']]>tv[y['id']])
    s=cp_model.CpSolver();s.parameters.num_search_workers=1
    st=s.Solve(m);assert st==cp_model.OPTIMAL,s.StatusName(st)
    rebuilt=copy.deepcopy(c);rebuilt.segs=[[] for _ in range(47)]
    for x in ns:rebuilt.segs[s.Value(tv[x['id']])].append(x['lines'])
    assert rebuilt.text()==c.text()
    result=dict(status=s.StatusName(st),ops=ns,lifetimes=lives,roles=dict(D=D,A=A,B=B,C=C),r3_nodes=r3_ids,
                records=profile(c)['records'],detectors=c.dets,release_profile=profile(c),seconds=s.WallTime(),
                serialized_qasm_sha256=hashlib.sha256(c.text().encode()).hexdigest())
    (HERE/'model.json').write_text(json.dumps(result,indent=2)+'\n')
    return rebuilt,result

def retime(c,weights,seed=0,seconds=10,workers=3,round_shift=0,release_only=False):
    ns=nodes(c);m=cp_model.CpModel();tt=[]
    r3=json.loads((ROOT/'work/lanes/BFLAG/syn/r3.json').read_text())
    resource={(33+i,tuple(e)) for i,es in enumerate(r3['ops']) for e in es}
    aenc={(37,(8,2)),(38,(2,1)),(38,(14,8)),(39,(1,2)),(39,(9,8)),(40,(8,2)),(40,(9,15)),(41,(8,9)),(41,(16,15)),(42,(9,8)),(42,(15,14)),(43,(14,8))}
    for x in ns:
        v=m.NewIntVar(0,46+round_shift,f"t{x['id']}");tt.append(v)
        # The prefix and its guards may commute/retime; suffix is represented
        # instruction-for-instruction and optionally shifted as a whole.
        if x['t']<16: m.Add(v==x['t'])
        elif x['t']>=40 and x['kind']!='TDG': m.Add(v==x['t']+round_shift)
        elif (x['t'],tuple(x['qs'])) in resource|aenc and x['kind']=='CX':m.Add(v==x['t']+round_shift)
        elif x['t']>=38 and x['kind'] in ('R','RX'):m.Add(v==x['t']+round_shift)
        elif x['t']>=32 and x['bit'] in (295,298,299,301,303,304,300,297,302):m.Add(v==x['t']+round_shift)
        else:m.Add(v>=16);m.Add(v<=min(43+round_shift,x['t']+2))
        m.AddHint(v,min(x['t'],46+round_shift))
    for q in range(36):m.AddAllDifferent([tt[x['id']] for x in ns if q in x['qs']])
    for i,x in enumerate(ns):
        for y in ns[:i]:
            if not commute(x,y):m.Add(tt[x['id']]>tt[y['id']])
    dev=[]
    for x in ns:
        z=m.NewIntVar(0,46,'d'+str(x['id']));m.AddAbsEquality(z,tt[x['id']]-x['t']);dev.append(z)
    main=sum(w*tt[x['id']] for b,w in weights.items() for x in ns if x['bit']==b)
    m.Minimize(main*10000+sum(dev)*10-sum(tt))
    s=cp_model.CpSolver();s.parameters.num_search_workers=workers;s.parameters.max_time_in_seconds=seconds;s.parameters.random_seed=seed
    st=s.Solve(m);info=dict(status=s.StatusName(st),seconds=s.WallTime(),weights=weights,seed=seed,round_shift=round_shift)
    if st not in (cp_model.OPTIMAL,cp_model.FEASIBLE):return None,info
    new=copy.deepcopy(c);new.segs=[[] for _ in range(47+round_shift)]
    moves=[]
    for x in ns:
        t=s.Value(tt[x['id']]);new.segs[t].append(x['lines'])
        if t!=x['t']:moves.append(dict(id=x['id'],old=x['t'],new=t,lines=x['lines']))
    info.update(objective=s.ObjectiveValue(),bound=s.BestObjectiveBound(),moves=moves,profile=profile(new))
    return new,info

if __name__=='__main__':
    c=Circ((HERE/'builds/v36h.qasm').read_text());new,cert=lifetime_model(c)
    p=save(new,'roundtrip','Fixed lifetime/placement/record/r3 model round trip')
    print(json.dumps({k:cert[k] for k in ('status','seconds','serialized_qasm_sha256')}))
    print('operations',len(cert['ops']),'lifetimes',len(cert['lifetimes']),'r3',len(cert['r3_nodes']))
