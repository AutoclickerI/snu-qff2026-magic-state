from fractions import Fraction as F
from itertools import product
import json

# Encoded, transversal 4-block toy. Block 0 is data; block 1 is an
# unmeasured helper; blocks 2 and 3 are measured at the final tick.
# All native CX/idle Pauli probabilities are represented in units p/15.
edges=[(0,1),(1,2),(2,3),(3,0)]
matchings=[()]
for mask in range(1,1<<len(edges)):
    es=[e for i,e in enumerate(edges) if mask>>i&1]
    if len({v for e in es for v in e})!=2*len(es):continue
    for dirs in product((0,1),repeat=len(es)):
        matchings.append(tuple(e if d==0 else e[::-1] for e,d in zip(es,dirs)))

def cxprop(x,z,a,b):
    return x^(((x>>a)&1)<<b),z^(((z>>b)&1)<<a)

def rates(layer,suffix,bases,final=False):
    used={v for e in layer for v in e};faults=[]
    for a,b in layer:
        for pa in range(4):
            for pb in range(4):
                if pa==pb==0:continue
                x=((pa&1)<<a)|((pb&1)<<b)
                z=(((pa>>1)&1)<<a)|(((pb>>1)&1)<<b)
                faults.append((x,z,1))
    for q in range(4):
        if q in used or (final and q in (2,3)):continue
        for p in (1,2,3):faults.append(((p&1)<<q,((p>>1)&1)<<q,5))
    out=[0,0,0] # X,Y,Z
    for x,z,w in faults:
        for gates in suffix:
            for a,b in gates:x,z=cxprop(x,z,a,b)
        if any(((z if bas=='X' else x)>>q)&1 for q,bas in zip((2,3),bases)):continue
        pa=(x&1)+2*(z&1)
        if pa:out[{1:0,3:1,2:2}[pa]]+=w
    return tuple(out)

def add(a,b):return tuple(x+y for x,y in zip(a,b))
def q(v):
    x,y,z=v
    return F((x+y)**2,2)+z*z+2*y*z
def cross(a,b):return q(add(a,b))-q(a)-q(b)
def coeff(v):return F(21,225)*q(v)

rows=[]
final=((1,0),)
for bases in product('XZ',repeat=2):
    last=rates(final,[],bases,True)
    # Emulates the documented local criterion: cross-with-fixed-suffix,
    # followed only by a small sum-of-rates tie breaker (less than one unit).
    def greedykey(layer,suffix,fr):
        nr=rates(layer,suffix,bases)
        return (cross(nr,fr),sum(nr),layer)
    l1=min(matchings,key=lambda l:greedykey(l,[final],last))
    r1=rates(l1,[final],bases);s1=add(last,r1)
    l0=min(matchings,key=lambda l:greedykey(l,[l1,final],s1))
    gr=add(s1,rates(l0,[l1,final],bases));gc=coeff(gr)
    best=None
    for a,b in product(matchings,repeat=2):
        rr=add(last,add(rates(b,[final],bases),rates(a,[b,final],bases)))
        cc=coeff(rr)
        item=(cc,a,b,rr)
        if best is None or item<best:best=item
    rows.append(dict(bases=bases,greedy=dict(l0=l0,l1=l1,rates=gr,c2=str(gc),c2float=float(gc)),
        joint=dict(l0=best[1],l1=best[2],rates=best[3],c2=str(best[0]),c2float=float(best[0]))))
def basis_action(bits,gate_list):
    for a,b in gate_list:
        bits^=((bits>>a)&1)<<b
    return bits

E=(1,2) # Late ancilla preparation edge, control=pivot 1, target=2.
L=(0,2) # Earlier consumption: data -> ancilla target.
M=(3,0) # Final complementary helper -> data.
identity_equal=all(basis_action(i,[E,L,M])==basis_action(i,[L,E,M]) for i in range(16))
assert identity_equal
interleave=dict(
    identity='CX(1,2); CX(0,2); CX(3,0) == CX(0,2); CX(1,2); CX(3,0)',
    verified_basis_states=16,
    releases={'0':0,'1':4,'2':0,'3':5},
    conventional={'cx_schedule':[(4,E),(5,L),(6,M)],'A_reads':6,'B_read':7,'last_data_cx':6,'last_tick':7},
    interleaved={'cx_schedule':[(0,L),(4,E),(5,M)],'A_reads':5,'B_read':6,'last_data_cx':5,'last_tick':6},
    scope='Exact ideal Clifford identity and one-tick makespan witness; not a complete Steane instrument or a claimed noisy gain.'
)
print(json.dumps(dict(matchings=len(matchings),results=rows,interleave=interleave),indent=2))
