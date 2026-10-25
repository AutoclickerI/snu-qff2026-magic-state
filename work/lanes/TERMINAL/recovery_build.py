"""Concrete legal-gate, grid-free recovery witnesses; no atomic lookup gates."""
from lookup_scan import onehot,duplicated_or,schedule
from build_rounds_source import Circuit,D

def put(c,ops,mapping,start):
    ts,depth=schedule(ops,len(mapping))
    for op,t in zip(ops,ts):
        kind,*qs=op;phys=[mapping[q] for q in qs]
        c.add(start+t,kind+' '+','.join(f'q[{q}]' for q in phys)+';')
    return depth

def coherent(relative=False):
    c=Circuit();c.magic()
    maps=[list(range(7,17)),list(range(17,27))]
    for q in range(7,27):c.reset(6,q)
    # Preserve the audited native H gates: reset followed by H otherwise folds
    # across barriers into an earlier RX in the judge.
    for q in range(7,27):c.add(7,f'id q[{q}];')
    for m in maps:depth=put(c,onehot(relative),m,8)
    t=8+depth
    for d in D:c.add(t,f'h q[{d}];')
    for i,d in enumerate(D):c.cx(t+1,maps[1][i+3],d)
    for d in D:c.add(t+2,f'h q[{d}];')
    for i,d in enumerate(D):c.cx(t+3,maps[0][i+3],d)
    c.save('c_coherent_rccx' if relative else 'c_coherent',noise_start=7,lookup_depth=depth,perfect_syndrome_extraction=True,
           mechanism='first-order lookup failures and stale-syndrome data idle factor')

def linear():
    c=Circuit();c.magic();maps=[list(range(7,14)),list(range(14,21))];src=[]
    for q in range(7,21):c.reset(6,q)
    for m in maps:src.append([c.read(7,q) for q in m[:3]])
    for m in maps:
        for q in m[3:]:c.add(7,f'id q[{q}];')
    for j,d in enumerate((0,1,3)):c.cx(8,maps[0][j],d)
    for d in (0,1,3):c.add(9,f'h q[{d}];')
    for j,d in enumerate((0,1,3)):c.cx(10,maps[1][j],d)
    for d in (0,1,3):c.add(11,f'h q[{d}];')
    for m in maps:depth=put(c,duplicated_or(),m,11)
    t=11+depth
    for axis,m,refs in zip('XZ',maps,src):
        r1=c.read(t,m[4]);r2=c.read(t,m[6]);c.dets.append([r1,r2])
        for q,r in zip(m[:3],refs):c.dets.append([r,c.read(t,q)])
        c.frames.append(f'// FRAME_{axis}(0) '+' '.join(f'c[{r}]' for r in [r1]+refs))
    c.save('d_linear_frame',noise_start=7,lookup_depth=depth,perfect_syndrome_extraction=True,
           mechanism='data wait during duplicated OR; records retain all affine frame and memory checks')

if __name__=='__main__':coherent();coherent(True);linear()
