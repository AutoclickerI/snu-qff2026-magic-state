"""Native terminal Clifford decoders with exact detector-row conjugation."""
from common import *
import itertools,collections

def save(c,name,edits):
    c=C.normalize(C.clone(c));text=C.textof(c)
    md={k:v for k,v in c['meta'].items() if k in ('data_qubits','R','round_range','native_depth','cx','terminal_decoder','terminal_cancellations','terminal_BC_check')}
    md.update(base='MAIN/v34m',comp29_edits=edits,source=str(c.get('source','')),qasm_sha256=hashlib.sha256(text.encode()).hexdigest())
    (H/(name+'.qasm')).write_text(text);(H/(name+'.json')).write_text(json.dumps(md,indent=2)+'\n')
    return dict(stem=name,edits=edits,sha256=md['qasm_sha256'],cx=md['cx'],R=md['R'],native_depth=md['native_depth'])

def terminal(c):
    last={}
    for i,u in enumerate(c['u']):
        for q in u.qs:last[q]=i
    out={}
    for q,i in last.items():
        u=c['u'][i]
        if u.name in ('MX','MEASURE'):
            out[q]=dict(index=i,bit=int(re.search(r'c\[(\d+)\]',' '.join(u.lines))[1]),basis='X' if u.name=='MX' else 'Z')
    return out

def columns(c,term):
    bybit={v['bit']:(q,v['basis']) for q,v in term.items()};xs=[0]*36;zs=[0]*36;external=[]
    for i,line in enumerate(c['tail']):
        outside=[]
        for b in map(int,re.findall(r'c\[(\d+)\]',line)):
            if b in bybit:
                q,p=bybit[b];(xs if p=='X' else zs)[q]^=1<<i
            else:outside.append(b)
        external.append(outside)
    return xs,zs,external

def conjugate(xs,zs,network):
    xs=xs.copy();zs=zs.copy()
    for a,b in network:xs[b]^=xs[a];zs[a]^=zs[b]
    return xs,zs

def build(base,network,axes=None,flags=()):
    c=C.clone(base);term=terminal(c);xs,zs,external=columns(c,term);xs,zs=conjugate(xs,zs,network)
    assert all(not(xs[q] and zs[q]) for q in term),'old detector rows need incompatible bases'
    axes={q:('X' if xs[q] else 'Z' if zs[q] else (axes or {}).get(q,term[q]['basis'])) for q in term}
    affected={q for edge in network for q in edge}|set(flags)
    drop={term[q]['index'] for q in affected};uu=[];tt=[];free={q:0 for q in term}
    for i,(u,t) in enumerate(zip(c['u'],c['t'])):
        if i in drop:continue
        uu.append(u);tt.append(t)
        for q in affected.intersection(u.qs):free[q]=max(free[q],t+1)
    for a,b in network:
        t=max(free[a],free[b]);v=C.Unit([f'cx q[{a}],q[{b}];']);v.decoder_added=True;uu.append(v);tt.append(t);free[a]=free[b]=t+1
    for q in affected:
        b=term[q]['bit'];lines=[f'measure q[{q}] -> c[{b}];']
        if axes[q]=='X':lines=[f'h q[{q}];',*lines,f'h q[{q}];']
        v=C.Unit(lines);v.decoder_readout=True;uu.append(v);tt.append(free[q])
    c['u']=uu;c['t']=tt;c['tail']=[]
    for i,ext in enumerate(external):
        bits=ext+[term[q]['bit'] for q in term if (xs[q]|zs[q])>>i&1]
        c['tail'].append('// DETECTOR '+' '.join(f'c[{b}]' for b in sorted(bits)))
    for q in flags:
        assert not(xs[q] or zs[q]),('flag is not independent',q)
        c['tail'].append(f"// DETECTOR c[{term[q]['bit']}]")
    order=sorted(range(len(uu)),key=lambda i:(tt[i],i));c['u']=[uu[i] for i in order];c['t']=[tt[i] for i in order]
    c['meta'].update(terminal_decoder=dict(network=network,axes=axes,flags=list(flags),detector_rows_preserved=True))
    return c

def cancel_added(c):
    c=C.clone(c);removed=[]
    while True:
        found=False
        for i,u in enumerate(c['u']):
            if u.name!='CX' or not getattr(u,'decoder_added',False):continue
            for j in range(i-1,-1,-1):
                v=c['u'][j]
                if v.lines==u.lines:
                    removed.append(dict(lines=u.lines,old_time=c['t'][j],new_time=c['t'][i]))
                    for k in [i,j]:del c['u'][k];del c['t'][k]
                    found=True;break
                if not C.commute(u,v):break
            if found:break
        if not found:break
    free={};nt=[]
    for u,t in zip(c['u'],c['t']):
        lower=0 if getattr(u,'decoder_added',False) or getattr(u,'decoder_readout',False) else t
        t=max([lower]+[free.get(q,0) for q in u.qs]);nt.append(t)
        for q in u.qs:free[q]=t+1
    c['t']=nt;c['meta']['terminal_cancellations']=removed
    return c

def enumerate_networks(base,maxgates=3):
    term=terminal(base);qs=sorted(term);xs,zs,_=columns(base,term)
    edges=[(a,b) for a in qs for b in qs if abs(a//6-b//6)+abs(a%6-b%6)==1]
    rows=[];counts=collections.Counter();seen=set()
    def visit(net,vertices,x,z):
        depth=len(net)
        if depth:
            counts['networks_'+str(depth)]+=1
            compatible=all(not(x[q] and z[q]) for q in qs)
            if compatible:
                counts['compatible_'+str(depth)]+=1
                free=[q for q in qs if not(x[q] or z[q])]
                if free:
                    counts['free_'+str(depth)]+=1
                    key=(tuple(x),tuple(z),tuple(net))
                    if key not in seen:
                        seen.add(key);rows.append(dict(network=net,free=free,depth=depth))
        if depth==maxgates:return
        for a,b in edges:
            if net and ((a,b)==tuple(net[-1]) or not({a,b}&vertices)):continue
            xx=x.copy();zz=z.copy();xx[b]^=xx[a];zz[a]^=zz[b]
            visit(net+[(a,b)],vertices|{a,b},xx,zz)
    visit([],set(),xs,zs)
    return dict(terminal=term,edges=edges,counts=counts,networks=rows)

if __name__=='__main__':
    c=C.read(H/'g_base');r=enumerate_networks(c,3)
    (H/'v34_decoder_enumeration.json').write_text(json.dumps(r,indent=2)+'\n');print(dict(counts=r['counts'],free_networks=len(r['networks'])));print(r['networks'][:15])
