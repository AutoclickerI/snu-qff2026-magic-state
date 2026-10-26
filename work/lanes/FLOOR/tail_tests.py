"""Exact all-orders perfect-prefix tail tests using project evaluator, not reviewer code.
Every suppressed channel is identified by an explicit native-schedule cut.
"""
import dataclasses, importlib, itertools, json, os, re, sys, time
from collections import deque
from pathlib import Path
import numpy as np
import tprep, xtim
from tprep.qasm import to_stim
from tprep.noise import noise_blocks, schedule, STANDARD, _repeated
from tprep.exact import verify
from tprep.parse import declarations

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
sys.path.insert(0,str(ROOT/'work/tools'))
from qtools.evaluator import sparse_walsh as qs
xtim.cache_dir=str(OUT/'cache/xtim')
os.environ['XTIM_TWIRL_CACHE_DIR']=str(OUT/'cache/twirl')
D=[0,2,4,12,14,16,24]
A=[q+1 for q in D]
B=[q+6 for q in D]
BAR='barrier '+','.join(f'q[{q}]' for q in range(36))+';'
HEADER='OPENQASM 2.0;\ninclude "qelib1.inc";\nqreg q[36];\ncreg c[32];\n'

def independent(vs):
    piv={}
    for v in vs:
        while v:
            k=v.bit_length()-1
            if k not in piv:piv[k]=v;break
            v^=piv[k]
        if not v:return False
    return True

def encoder():
    cols=[127,85,102,120]
    for k in range(7):
        if independent(cols+[1<<k]):cols.append(1<<k)
    rows=[sum(((v>>k)&1)<<j for j,v in enumerate(cols)) for k in range(7)]
    ops=[]
    def add(c,t):rows[t]^=rows[c];ops.append((c,t))
    for k in range(7):
        r=next(r for r in range(k,7) if rows[r]>>k&1)
        if r!=k:add(r,k);add(k,r);add(r,k)
        for t in range(7):
            if t!=k and rows[t]>>k&1:add(k,t)
    assert rows==[1<<k for k in range(7)]
    ans=[f'h q[{D[0]}];',f't q[{D[0]}];']+[f'h q[{D[k]}];' for k in (1,2,3)]
    def path(c,t):
        todo=deque([[c]]);seen={c}
        while todo:
            ps=todo.popleft();q=ps[-1]
            if q==t:return ps
            for r in range(36):
                if abs(q//6-r//6)+abs(q%6-r%6)==1 and r not in seen:seen.add(r);todo.append(ps+[r])
    def cx(c,t):ans.append(f'cx q[{c}],q[{t}];')
    def sw(c,t):cx(c,t);cx(t,c);cx(c,t)
    for c,t in reversed(ops):
        p=path(D[c],D[t])
        for a,b in zip(p[:-2],p[1:-1]):sw(a,b)
        cx(p[-2],p[-1])
        for a,b in reversed(list(zip(p[:-2],p[1:-1]))):sw(a,b)
    return ans

def sequential(lines):return ('\n'+BAR+'\n').join(lines)+'\n'+BAR+'\n'
def layer(lines):return '\n'.join(lines)+'\n'+BAR+'\n'
def cxs(xs,ys):return [f'cx q[{x}],q[{y}];' for x,y in zip(xs,ys)]
def preps(qs,x=False):return [v for q in qs for v in ([f'reset q[{q}];',f'h q[{q}];'] if x else [f'reset q[{q}];'])]

def price(text,stem,cut,engine):
    fa=engine.fa
    old=fa.noise_blocks
    def cut_noise(native,p,first_order=False):
        prog,steps,gaps=schedule(native)
        _,blocks=noise_blocks(native,p,dataclasses.replace(STANDARD,idle=0),first_order=False)
        for i,block in enumerate(blocks):
            if steps[i][0][1]<cut:
                blocks[i]=[re.sub(r'\([^)]*\)','(0.0)',l) if '(' in l else l for l in block]
        for i,q,start,n in gaps:
            keep=max(0,start+n-max(start,cut))
            if keep:blocks[i].append(f'DEPOLARIZE1({_repeated(p,keep,False)}) {q}')
        return prog,blocks
    fa.noise_blocks=cut_noise
    try:
        m,e,g,nd,ks,psi,where,_=engine.prepare(stem,True)
    finally:fa.noise_blocks=old
    compiled=engine.compile_channels(m,g,nd,ks)
    elim=engine.minfill([set(x[0]) for x in compiled])
    engine._CTX.update(eng=e,ks=ks,psi=psi,where=where,compiled=compiled,elim=elim)
    rr=[engine._row(k) for k in [None]+e.keys]
    acc=rr[0]['value'];obs=sum(w*b*r['value'] for w,b,r in zip(e.W,e.beta,rr[1:]))
    out=dict(loss=(acc-obs)/(2*acc),acceptance=acc,channels=len(m.chans),cut=cut,
             omission=max(r['absolute_kernel_omission_bound'] for r in rr),width=elim['width'])
    engine._CTX.clear();engine.COLUMNS.clear()
    return out

def main():
    enc=sequential(encoder())
    zeroA=layer(preps(A));plusA=layer(preps(A,True));plusB=layer(preps(B,True))
    invA=layer(cxs(D,A));invB=layer(cxs(D,B))
    measureA=layer([f'measure q[{a}] -> c[{k}];' for k,a in enumerate(A)])
    dets='\n'.join(f'// DETECTOR c[{k}]' for k in range(7))+'\n'
    # prefix, noisy tail, declarations. Prefix is perfect, but its terminal waiting noise is retained.
    cases={
      'one_idle':(enc,layer(['id q[35];']),''),
      'two_idle':(enc,layer(['id q[35];'])+layer(['id q[35];']),''),
      'one_helper_CX':(enc+plusA,invA,''),
      'inverse_two_CX':(enc+zeroA,invA+invA,''),
      'measured_helper':(enc+zeroA+invA,invA+measureA,dets),
      'measured_helper_then_fresh_helper':(enc+zeroA+invA,
           layer(cxs(D,A)+preps(B,True))+layer(cxs(D,B)+[f'measure q[{a}] -> c[{k}];' for k,a in enumerate(A)]),dets),
      'measured_helper_then_early_helper':(enc+zeroA+invA+plusB,
           invA+layer(cxs(D,B)+[f'measure q[{a}] -> c[{k}];' for k,a in enumerate(A)]),dets),
      'logical_X_gate_with_frame':(enc,layer([f'x q[{q}];' for q in D]),'// FRAME_X(1)\n// FRAME_Z(0)\n'),
      'logical_S_gate':(sequential(encoder()+[f'sdg q[{q}];' for q in D]),layer([f's q[{q}];' for q in D]),''),
      'physical_XZ_perfect_inverse':(enc+layer([f'y q[{q}];' for q in D]),layer([f'y q[{q}];' for q in D]),''),
    }
    results={}
    for name,(prefix,tail,decl) in cases.items():
        begin=time.perf_counter()
        text=HEADER+prefix+tail+decl
        stem=OUT/'experiments'/name
        stem.with_suffix('.qasm').write_text(text);stem.with_suffix('.json').write_text(json.dumps({'data_qubits':D})+'\n')
        st,errors=to_stim(text);assert not errors,errors
        fr,ps=declarations(st)
        raw=verify(st,D,frame=fr,postselect=ps)
        assert not raw['errors'],(name,raw)
        judge=tprep.check(text,D,p=0,shots=64)
        assert judge.correct_ok,(name,str(judge))
        # All boundaries are full barriers; determine native tail start from source line numbers.
        useframe=name in ('logical_X_gate_with_frame','logical_S_gate','physical_XZ_perfect_inverse')
        if useframe:
            sys.path.insert(0,str(ROOT/'work/lanes/WHOLEEND/sparseframe'))
            engine=importlib.import_module('sparse_walsh')
        else:engine=qs
        ops,_=engine.fa.parse_current(text)
        native,labels=engine.fa.native_text(ops)
        _,steps,_=schedule(native)
        tail_line=len((HEADER+prefix).splitlines())+1
        cut=min(steps[i][0][1] for i,o in enumerate(labels) if o.line>=tail_line)
        result=price(text,stem,cut,engine)
        result.update(raw=raw,judge=str(judge),seconds=time.perf_counter()-begin,
                      prefix_noise='suppressed before native cut; straddling idles retained',engine='WHOLEEND/sparseframe' if useframe else 'qtools')
        results[name]=result
        (OUT/'experiments/tail_results.json').write_text(json.dumps(results,indent=2)+'\n')
        if result['loss']<2.18925128e-5:
            # Save these immediately, explicitly scoped to cuts that omit compulsory earlier layers.
            for ext in ('.qasm','.json'):(OUT/'counterexamples'/(name+ext)).write_text(stem.with_suffix(ext).read_text())
            (OUT/'counterexamples'/(name+'_scope.json')).write_text(json.dumps(result,indent=2)+'\n')
        print(name,json.dumps(result),flush=True)
    print('COMPLETE',flush=True)

if __name__=='__main__':main()
