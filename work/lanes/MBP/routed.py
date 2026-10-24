"""Physical diagnostic: MB B/C on L5 through exact nearest-neighbour CX bridges.

The bridge returns every intermediate quantum state unchanged noiselessly. Its
fault propagation is deliberately left to the judge; no FT assumption is made.
"""
from mbp import *
from collections import deque
A=[1,14,8,9,2,16,15];B=[6,26,13,11,4,23,27];C=[12,25,19,17,5,29,28];D=[0,20,7,10,3,22,21]

def build_routed(kind):
    physical();src=OUT/'inputs/v22h_c2c9';text=src.with_suffix('.qasm').read_text();h,raw,tail=S.qasm_ops(text);us=S.fold_units(raw);ts=native_times(text,us)
    bc=set(B+C);starts={}
    for q in bc:
        cand=[i for i,u in enumerate(us) if ts[i]<45 and u.qs==(q,) and (u.name in ('RESET','RX') or (u.name=='MEASURE' and any(int(x)>=35 for l in u.lines for x in re.findall(r'c\[(\d+)\]',l))))]
        starts[q]=max(cand)
    drop={i for i,u in enumerate(us) if ts[i]<45 and set(u.qs)<=bc and all(i>=starts[q] for q in u.qs)}
    assert sum(us[i].name=='CX' for i in drop)==82
    deadbits={int(b) for i in drop for l in us[i].lines for b in re.findall(r'c\[(\d+)\]',l)}
    old=[];roundops=[];cur={q:0 for q in range(36)}
    for i,(u,t) in enumerate(zip(us,ts)):
        if i in drop:continue
        if t>=45:roundops.append((t-45,u.lines,'round'));continue
        old.append((t,u.lines,'retained'))
        for q in u.qs:cur[q]=max(cur[q],t+1)
    allowed=set(range(36))-set(A+D)
    def path(u,v):
        todo=deque([[u]]);seen={u}
        while todo:
            p=todo.popleft()
            if p[-1]==v:return p
            for q in sorted(allowed-seen):
                if ORIG_ADJ(p[-1],q):todo.append(p+[q]);seen.add(q)
        raise ValueError((u,v))
    def add(ls,qs,tag):
        t=max(cur[q] for q in qs);old.append((t,ls,tag))
        for q in qs:cur[q]=t+1
    def cx(u,v,tag):
        p=path(u,v);edges=list(zip(p,p[1:]));d=len(edges)
        seq=edges if d==1 else edges+edges[-2::-1]+edges[1:]+edges[-2:0:-1]
        for a,b in seq:add([f'cx q[{a}],q[{b}];'],[a,b],tag)
    bit=60;frames={};extras=[]
    for k,cells,anc in [('B',B,18),('C',C,24)]:
        oo,ff,ee,bit=mbprep(cells,False,40,[anc]*16,bit,kind)
        frames[k]=ff;extras+=ee
        # Recycled physical ancilla requires the sequential projector variant.
        # For a tree hybrid only one projector remains.
        for t,ls,_ in sorted(oo,key=lambda x:x[0]):
            if ls[0].startswith('cx '):
                u,v=map(int,re.findall(r'q\[(\d+)\]',ls[0]));cx(u,v,k)
            else:
                qs=sorted({int(q) for l in ls for q in re.findall(r'q\[(\d+)\]',l)});add(ls,qs,k)
    R=max(cur.values())
    old += [(R+t,ls,tag) for t,ls,tag in roundops]
    dets=[]
    for line in tail:
        if not line.startswith('// DETECTOR'):continue
        bits=list(map(int,re.findall(r'c\[(\d+)\]',line)))
        if set(bits)&deadbits:continue
        for j,ss in enumerate(GENS):
            if set(bits)=={28+i for i in ss}:bits+=frames['B'][j]+frames['C'][j]
        dets.append(bits)
    dets+=extras;text,tags=emit(old,dets,36)
    ss,labels,errors=model.convert(text,36,model.STANDARD);assert not errors
    prog,steps,gaps=model.schedule(ss);ql=exact2.qasm_lines(text);native=[];pairs=set(zip(D,A))|set(zip(B,C))
    for ins,st in zip(prog,steps):
        mat=re.match(r'instruction (\d+)',labels[ins.line_no-1]);line=ql[int(mat[1])-1][0] if mat else None
        if ins.name=='CX' and tuple(ins.qubits) in pairs and tags.get(line)=='round':native.append(st[0][1])
    assert len(native)==14 and len(set(native))==1
    return text,dict(data_qubits=D,grid_free=False,n_qubits=36,kind='routed_BC_'+kind,R=native[0],requested_R=R,R_native_range=[min(native),max(native)],native_depth=max(t for ss in steps for q,t in ss)+1,cx=text.count('cx '),line_regions=tags)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--kind',default='hybrid2t');p.add_argument('--procs',type=int,default=1);a=p.parse_args()
    text,meta=build_routed(a.kind);stem=OUT/('physical_'+a.kind);stem.with_suffix('.qasm').write_text(text);stem.with_suffix('.json').write_text(json.dumps(meta,indent=2)+'\n')
    row=price(text,meta,a.procs);stem.with_suffix('.result.json').write_text(json.dumps(dict(meta,**row),indent=2)+'\n');print(json.dumps(row),flush=True)
