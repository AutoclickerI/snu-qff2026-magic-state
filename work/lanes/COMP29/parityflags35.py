"""Audit all compatible short decoders for new parity flags, not only free wires.

The ranking evaluator is unchanged. This ideal-only audit exposes the existing
frontend's final Pauli images before terminal measurements, then queries them
in its exact noiseless rotation state.
"""
from core35 import *
import inspect,functools,collections
sys.path.insert(0,str(H/'sparse35'))
import frontend as fa

def reduce(v,basis):
    while v:
        p=v.bit_length()-1
        if p not in basis:return v
        v^=basis[p]
    return 0
def row_basis(rows):
    out={}
    for v in rows:
        v=reduce(v,out)
        if v:out[v.bit_length()-1]=v
    return out

def audit(base):
    text=C.textof(base);ops,dets=fa.parse_current(text);tr=terminal(base);term_bits={v['bit'] for v in tr.values()};bybit={v['bit']:q for q,v in tr.items()}
    ops=[o for o in ops if o.bit not in term_bits];dets=[d for d in dets if not(d&term_bits)]
    src=inspect.getsource(fa.make_model).replace('    return model','    model.final_paulis={q:{P:pull(physical([q],P)) for P in "XZ"} for q in range(36)}\n    return model')
    scope=dict(fa.__dict__);exec(src,scope);m=scope['make_model'](ops,dets);e=fa.Engine(m);phi=e.phi(0)
    @functools.lru_cache(None)
    def expect(P):
        x,z,co=P;xx=e.B.express(x)
        if xx is None:return 0.
        return e.expect(phi,(xx,e._w(z),co))
    def pull(x,z):
        P=(0,0,1)
        for q in range(36):
            if x>>q&1:P=fa.mul(P,m.final_paulis[q]['X'])
        for q in range(36):
            if z>>q&1:P=fa.mul(P,m.final_paulis[q]['Z'])
        return P
    for line in base['tail']:
        x=z=0;P=(0,0,1)
        for b in map(int,re.findall(r'c\[(\d+)\]',line)):
            if b in bybit:
                q=bybit[b]
                if tr[q]['basis']=='X':x^=1<<q
                else:z^=1<<q
            else:P=fa.mul(P,m.record_ps[b])
        assert abs(expect(fa.mul(pull(x,z),P))-1)<1e-10,line
    random_records=[b for b,P in m.record_ps.items() if abs(expect(P))<1-1e-10]
    assert len(random_records)<=4,random_records
    corrections=[]
    for mask in range(1<<len(random_records)):
        P=(0,0,1);bits=0
        for i,b in enumerate(random_records):
            if mask>>i&1:P=fa.mul(P,m.record_ps[b]);bits^=1<<b
        corrections.append((bits,P))
    qs=sorted(tr);xs,zs,external=columns(base,tr);edges=[(a,b) for a in qs for b in qs if abs(a//6-b//6)+abs(a%6-b%6)==1]
    found=[];counts=collections.Counter()
    def visit(net,vertices,x,z):
        if net and all(not(x[q] and z[q]) for q in qs):
            counts['compatible']+=1
            axes={q:'X' if x[q] else 'Z' if z[q] else ('X' if q in C.A else tr[q]['basis']) for q in qs}
            rows=[]
            for i,ext in enumerate(external):rows.append(sum(1<<b for b in ext)^sum(1<<tr[q]['bit'] for q in qs if (x[q]|z[q])>>i&1))
            basis=row_basis(rows);vs=sorted(vertices);new=[]
            for subset in range(1,1<<len(vs)):
                picked=[q for j,q in enumerate(vs) if subset>>j&1]
                if not any(q in C.A and axes[q]=='X' for q in picked):continue
                xx=sum(1<<q for q in picked if axes[q]=='X');zz=sum(1<<q for q in picked if axes[q]=='Z')
                for a,b in reversed(net):
                    if xx>>a&1:xx^=1<<b
                    if zz>>b&1:zz^=1<<a
                P=pull(xx,zz);mbits=sum(1<<tr[q]['bit'] for q in picked)
                for correction,Q in corrections:
                    candidate=mbits^correction;residual=reduce(candidate,basis)
                    if not residual:continue
                    if abs(expect(fa.mul(P,Q))-1)<1e-10:
                        new.append([b for b in range(candidate.bit_length()) if candidate>>b&1]);basis[residual.bit_length()-1]=residual
            if new:found.append(dict(network=net,flags=new,axes={q:axes[q] for q in vertices},has_free_wire=any(not(x[q] or z[q]) for q in qs)))
        if len(net)==3:return
        for a,b in edges:
            if net and ((a,b)==tuple(net[-1]) or not({a,b}&vertices)):continue
            xx=x.copy();zz=z.copy();xx[b]^=xx[a];zz[a]^=zz[b];visit(net+[(a,b)],vertices|{a,b},xx,zz)
    visit([],set(),xs,zs)
    return dict(counts=counts,random_prefix_records=random_records,networks=found,without_free_wire=sum(not r['has_free_wire'] for r in found),expectation_cache=expect.cache_info()._asdict())

if __name__=='__main__':
    base=C.read(H/'h_prep_07');r=audit(base);(H/'v35_decoder_parity_audit.json').write_text(json.dumps(r,indent=2)+'\n');print({k:v for k,v in r.items() if k!='networks'});print('networks',len(r['networks']))
