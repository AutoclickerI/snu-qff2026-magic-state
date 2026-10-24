"""Build grid-free direct and measured-clean-bus Steane rounds after the v11 prefix.

No grid embedding is claimed. The bus suffix uses 35 cells; the complete
circuit uses all 36 cells because the prefix also uses q19.
At R>=34 the seven bus helpers reuse prefix ancillas after measurement at32.
The bus pipeline does not delay B->data or the final data output tick.
"""
import sys,json
from pathlib import Path
from collections import Counter
HERE=Path(__file__).resolve().parent
EVALUATOR=HERE.parent/'evaluator'
sys.path.insert(0,str(EVALUATOR))
import frontend as fa
from frontend import parse_current, Op

OUT=Path(__file__).resolve().parent
D=[0,20,7,4,3,15,8]
FREE=[5,11,12,16,17,18,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35]
A,B,C=FREE[:7],FREE[7:14],FREE[14:]
H=[1,2,6,9,10,13,14]
GENS=[[0,2,4,6],[1,2,5,6],[3,4,5,6]]
LAYERS=[[(0,2),(1,6),(3,5)],[(0,4),(1,2),(3,6)],[(0,6),(1,5),(3,4)]]
PREFIX=(HERE/'prefix_v11.qasm').read_text()
PD=[{i}for i in range(14)];PD[10].add(7)

def build(variant,R):
    assert variant in ('direct','bus')
    if variant=='bus':assert R>=34
    ops,_=parse_current(PREFIX)
    dets=[set(x)for x in PD]
    def op(t,k,qs,bit=None):ops.append(Op(k,tuple(qs),t,bit))
    def enc(cells,plus,t0):
        for i,q in enumerate(cells):op(t0-1,'RX'if((i in(0,1,3))!=plus)else'R',[q])
        for j,layer in enumerate(LAYERS):
            for c,t in layer:
                pair=(cells[t],cells[c])if plus else(cells[c],cells[t])
                op(t0+j,'CX',pair)
    enc(A,True,R-3);enc(B,False,R-3)
    enc(C,False,R-3+(variant=='bus'))
    bits={};n=14
    for block in 'acb'+('h'if variant=='bus'else''):
        for i in range(7):bits[block,i]=n;n+=1
    if variant=='bus':
        for h in H:op(R-1,'R',[h])
    for i in range(7):
        op(R,'CX',(D[i],A[i]))
        op(R,'CX',(B[i],H[i]if variant=='bus'else C[i]))
        op(R+1,'M',[A[i]],bits['a',i])
        op(R+1,'CX',(B[i],D[i]))
        op(R+2,'MX',[B[i]],bits['b',i])
        if variant=='bus':
            op(R+1,'CX',(H[i],C[i]))
            op(R+2,'MX',[H[i]],bits['h',i])
            op(R+2,'M',[C[i]],bits['c',i])
        else:op(R+1,'M',[C[i]],bits['c',i])
    for block in 'abc':
        for S in GENS:
            row={bits[block,i]for i in S}
            if block=='b'and variant=='bus':row^={bits['h',i]for i in S}
            dets.append(row)
    dets.append({bits['c',i]for i in range(7)})
    # Consecutive empty barriers do not consume ticks in the judge scheduler.
    # q19 was measured by the prefix and is never used in this suffix.
    for t in range(R+3):
        if not any(o.time==t for o in ops):op(t,'ID',[19])
    ops.sort(key=lambda o:o.time)
    for t in range(R+3):
        active=[q for o in ops if o.time==t for q in o.qs]
        assert len(active)==len(set(active)),(variant,R,t,Counter(active))
    out=['OPENQASM 2.0;','include "qelib1.inc";','qreg q[36];',f'creg c[{n}];']
    bar='barrier '+','.join(f'q[{q}]'for q in range(36))+';'
    for t in range(R+3):
        for o in ops:
            if o.time!=t:continue
            qs=','.join(f'q[{q}]'for q in o.qs)
            if o.kind in ('M','MX'):
                if o.kind=='MX':out.append(f'h {qs};')
                out.append(f'measure {qs} -> c[{o.bit}];')
            elif o.kind in ('R','RX'):
                out.append(f'reset {qs};')
                if o.kind=='RX':out.append(f'h {qs};')
            else:out.append(f'{o.kind.lower()} {qs};')
        if t!=R+2:out.append(bar)
    out.extend('// DETECTOR '+' '.join(f'c[{i}]'for i in sorted(s))for s in dets)
    stem=OUT/f'bus_{variant}_r{R}'
    stem.with_suffix('.qasm').write_text('\n'.join(out)+'\n')
    meta=dict(data_qubits=D,scope=__doc__,variant=variant,R=R,
              A=A,B=B,C=C,helpers=H if variant=='bus'else[],
              CX=sum(o.kind=='CX'for o in ops),native_depth=R+3)
    stem.with_suffix('.json').write_text(json.dumps(meta,indent=2)+'\n')
    return stem

if __name__=='__main__':
    for v,r in [('direct',33),('direct',34),('bus',34),('direct',45),('bus',45)]:
        stem=build(v,r)
        fa.DATA=D
        ops,ds=parse_current(stem.with_suffix('.qasm').read_text())
        model=fa.make_model(ops,ds);engine=fa.Engine(model)
        A0,N0=engine.ntable(0,0)
        single_loss=0.
        for f in model.faults:
            a,n=engine.ntable(f['s'],f['d'])
            if n is not None:single_loss+=f['p']*n[f['e']]
        print(json.dumps(dict(stem=stem.name,ideal_acceptance=A0,ideal_loss=N0[0],
                              first_order_loss=single_loss,channels=len(model.chans),
                              engine_rank=engine.r,projector_nontrivial=sum(p[:2]!=(0,0)for p in engine.projs))),flush=True)
