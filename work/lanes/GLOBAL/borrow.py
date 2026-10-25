"""Find extra local controlled stabilizers using correlated A/B/C role cells."""
import copy, itertools, json, re
from pathlib import Path
from qedit import load, QRE

HERE = Path(__file__).resolve().parent
D = [0,20,7,10,3,22,21]
A = [1,14,8,9,2,16,15]
B = [6,26,13,11,4,23,27]
C = [12,25,19,17,5,29,28]
STABS = [0b1010101,0b1100110,0b1111000]

def nb(q):
    return [p for p in range(36) if abs(p//6-q//6)+abs(p%6-q%6)==1]

def save(c, name, desc):
    for t, seg in enumerate(c.segs):
        seen=set()
        for g in seg:
            qs=set(map(int,QRE.findall(' '.join(g))))
            assert not seen & qs,(t,g)
            seen |= qs
    stem=HERE/'builds'/name
    stem.with_suffix('.qasm').write_text(c.text())
    meta=dict(data_qubits=D,global_change=desc,source='GLOBAL',
              cx=sum(g[0].startswith('cx') for ss in c.segs for g in ss),native_depth=len(c.segs))
    stem.with_suffix('.json').write_text(json.dumps(meta,indent=2)+'\n')
    return stem

def main():
    c=load(str(HERE/'builds/v36h'))
    for q,t2 in [(10,38),(20,37)]:
        (t,j),=c.find(lambda g:g[0]==f'tdg q[{q}];')
        c.move(t,j,t2)
    v=[1<<q for q in range(36)]
    nextv=36
    ops=[]
    sources=[]
    for t,seg in enumerate(c.segs):
        if t>=39:
            busy=c.qubits_at(t)
            for h in A+B+C:
                if h in busy or not v[h] or v[h]&((1<<36)-1):continue
                for d in nb(h):
                    if d not in D or d in busy:continue
                    if t>= (43 if d in [10,21] else 44):continue
                    # The data's final T has already happened.
                    dt=next(tt for tt,ss in enumerate(c.segs) if any(g[0]==f'tdg q[{d}];' for g in ss)) if d!=21 else 30
                    if t<=dt:continue
                    sig=0
                    for b in range(nextv):
                        if v[h]>>b&1:
                            for k,row in enumerate(STABS+[127]):
                                if row>>D.index(d)&1:sig^=1<<(b*4+k)
                    ops.append((t,h,d,v[h]));sources.append(sig)
        for g in seg:
            qs=list(map(int,QRE.findall(g[0])))
            q=qs[0]
            if g[0].startswith('reset'):
                v[q]=0
                if len(g)>1:
                    v[q]=1<<nextv;nextv+=1
            elif g[0].startswith('h') and 'measure' in ' '.join(g):
                v[q]=1<<nextv;nextv+=1
            elif g[0].startswith('measure'):
                v[q]=0
            elif g[0].startswith('cx'):
                v[qs[1]]^=v[qs[0]]
    basis={};null=[]
    for i,sig in enumerate(sources):
        mask=1<<i
        while sig:
            p=sig.bit_length()-1
            if p not in basis:
                basis[p]=(sig,mask);break
            a,b=basis[p];sig^=a;mask^=b
        if not sig:null.append(mask)
    print('ops',len(ops),'nullity',len(null),flush=True)
    for i,o in enumerate(ops):print(i,o,flush=True)
    kept=[]
    for subset in range(1,1<<len(null)):
        mask=0
        for j,b in enumerate(null):
            if subset>>j&1:mask^=b
        selected=[ops[i] for i in range(len(ops)) if mask>>i&1]
        if len(selected)>12:continue
        used=set();bad=False
        for t,h,d,vh in selected:
            if (t,h) in used or (t,d) in used:bad=True;break
            used|={(t,h),(t,d)}
        if bad:continue
        # Omit pure same-control echoes: retain a nonzero stabilizer action per independent variable.
        patterns={}
        for t,h,d,vh in selected:
            for b in range(vh.bit_length()):
                if vh>>b&1:patterns[b]=patterns.get(b,0)^(1<<D.index(d))
        if not any(patterns.values()):continue
        cc=copy.deepcopy(c)
        for t,h,d,vh in selected:cc.segs[t].append([f'cx q[{h}],q[{d}];'])
        name=f'borrow_{len(kept):03d}'
        save(cc,name,dict(family='borrowed controlled X stabilizer',gates=[o[:3] for o in selected],tmoves=[[10,38],[20,37]],patterns=patterns))
        kept.append(name)
    (HERE/'borrow_candidates.json').write_text(json.dumps(kept))
    print('built',len(kept),flush=True)

if __name__=='__main__':main()
