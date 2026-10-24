"""Concrete grid-free final-round alternatives; no files outside ARCH are written."""
import os
import sys
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT/'work/lanes/MAIN/gf'), str(ROOT/'work/lanes/EARLY')]
import gf33
import early_merge

D = gf33.PRE_DATA
A, B, C = (gf33.FREE[k:k+7] for k in (0, 7, 14))
GENS = gf33.GENS

class Circuit:
    def __init__(self):
        self.head, pre = early_merge.prefix_steps()
        self.ops = [(t,s,'pre') for s,t in pre]
        self.dets = list(gf33.PRE_DETECTORS)
        self.n = 14
        self.regions = {}
        self.notes = []
    def add(self,t,s,reg='round'):
        self.ops.append((t,s,reg))
    def cx(self,t,c,d,reg='round'):
        self.add(t,f'cx q[{c}],q[{d}];',reg)
    def prep(self,cells,plus,end):
        self.ops += [(t,s,'prep') for t,s in gf33.enc(cells,plus,end-2)]
    def read(self,t,q,basis='Z',reg='round',reuse=False):
        n=self.n; self.n+=1
        if basis=='X': self.add(t,f'h q[{q}];',reg)
        self.add(t,f'measure q[{q}] -> c[{n}];',reg)
        if basis=='X' and reuse: self.add(t,f'h q[{q}];',reg)
        return n
    def readblock(self,t,cells,basis,logical=False,reuse=False):
        bs=[self.read(t,q,basis,reuse=reuse) for q in cells]
        for S in GENS+([list(range(7))] if logical else []):
            self.dets.append(' '.join(f'c[{bs[i]}]' for i in S))
        return bs
    def save(self,name,meta=None):
        by={}
        busy={}
        for t,s,r in self.ops:
            qs=tuple(map(int,re.findall(r'q\[(\d+)\]',s)))
            # h paired with reset/readout is folded into a native operation.
            if not s.startswith('h '):
                for q in qs:
                    assert (t,q) not in busy, (name,t,q,s,busy.get((t,q)))
                    busy[t,q]=s
            by.setdefault(t,[]).append(s)
            if r=='round':
                self.regions[f'{t}:'+','.join(map(str,sorted(qs)))]=r
        bar='barrier '+','.join(f'q[{q}]' for q in range(36))+';'
        out=self.head+[f'creg c[{self.n}];']
        for t in range(max(by)+1):
            out+=by.get(t,[]) or ['id q[35];']
            out.append(bar)
        out=out[:-1]+[f'// DETECTOR {d}' for d in self.dets]
        text='\n'.join(out)+'\n'
        obj=dict(data_qubits=D,grid_free=True,name=name,round_ops=list(self.regions),
                 R=33,end=max(by),notes=self.notes,cx=text.count('cx '),
                 used_qubits=len({int(q) for q in re.findall(r'q\[(\d+)\]', '\n'.join(s for _,s,_ in self.ops))}))
        if meta: obj.update(meta)
        (HERE/(name+'.qasm')).write_text(text)
        (HERE/(name+'.json')).write_text(json.dumps(obj,indent=2)+'\n')
        return obj

def standard(name='base',a=33,b=34,ar=None,cr=None,br=None,tail=None,verify_after=False,omit=None):
    c=Circuit()
    ar=a+1 if ar is None else ar
    br=b+1 if br is None else br
    vc=b+1 if verify_after else b-1
    cr=vc+1 if cr is None else cr
    c.prep(A,True,a-1)
    c.prep(B,False,min(vc,b)-1)
    c.prep(C,False,vc-1)
    if a==32:
        c.ops=[(33 if t==32 and s.startswith('tdg ') else t,s,r) for t,s,r in c.ops]
    for i in range(7):
        if omit!='A': c.cx(a,D[i],A[i])
        if omit!='B': c.cx(b,B[i],D[i])
        c.cx(vc,B[i],C[i])
    if omit!='A': ab=c.readblock(ar,A,'Z')
    else: c.ops=[o for o in c.ops if not(o[2]=='prep' and set(map(int,re.findall(r'q\[(\d+)\]',o[1])))<=set(A))]
    cb=c.readblock(cr,C,'Z',True,reuse=tail=='reuseC')
    if omit!='B': c.readblock(br,B,'X')
    if tail=='reuseC':
        for i in range(7): c.cx(br,C[i],D[i])
    if tail and tail.startswith('dummy'):
        # A has been measured and can be reused; final partner is a known |0>.
        # Fresh one-step reset or a measured initialization (postselected zero).
        for i in range(7):
            if tail=='dummyR': c.add(br-1,f'reset q[{A[i]}];')
            elif tail=='dummyM':
                j=c.read(br-1,A[i]); c.dets.append(f'c[{j}]')
            c.cx(br,A[i],D[i])
    if tail=='keepC':
        # Replaces C's destructive check by a fresh verifier V; C is the
        # checked encoded |0_L> partner, then remains unmeasured at the end.
        raise NotImplementedError
    return c.save(name,dict(mechanism=name))

def reverse():
    c=Circuit()
    c.prep(B,False,32); c.prep(A,True,32); c.prep(C,True,32)
    for i in range(7):
        c.cx(33,B[i],D[i]); c.cx(33,C[i],A[i]); c.cx(34,D[i],A[i])
    c.readblock(34,B,'X'); c.readblock(34,C,'X',True); c.readblock(35,A,'Z')
    return c.save('reverse')

def repeat(kind):
    # Reuse measured A for an extra partial round, with a fresh encoded block.
    c=Circuit()
    c.prep(A,True,32); c.prep(B,False,32); c.prep(C,False,32)
    for i in range(7):
        c.cx(33,D[i],A[i]); c.cx(33,B[i],C[i]); c.cx(34,B[i],D[i])
    c.readblock(34,A,'Z'); c.readblock(34,C,'Z',True); c.readblock(35,B,'X')
    if kind=='Z':
        c.prep(A,True,38)
        for i in range(7): c.cx(39,D[i],A[i])
        c.readblock(40,A,'Z')
    elif kind=='X':
        c.prep(A,False,38); c.prep(C,False,38)
        for i in range(7): c.cx(39,A[i],C[i]); c.cx(40,A[i],D[i])
        c.readblock(40,C,'Z',True); c.readblock(41,A,'X')
    return c.save('repeat'+kind)

def hybrid(typ):
    """One Steane basis and three conventional two-ancilla flagged weight-4 checks."""
    c=Circuit()
    # A/B use 14 never-used cells; six flag/check ancillas use the remaining 7.
    checks=C[:3]; flags=C[3:6]
    if typ=='Z':
        # Flagged Z checks first, verified Steane X check last.
        c.prep(A,False,40); c.prep(B,False,40)
        last=42
        for i in range(7): c.cx(41,A[i],B[i]); c.cx(42,A[i],D[i])
        c.readblock(42,B,'Z',True); c.readblock(43,A,'X')
        start=33
    else:
        c.prep(A,True,32)
        for i in range(7): c.cx(33,D[i],A[i])
        c.readblock(34,A,'Z'); start=34
    # Stagger whole flagged checks to avoid common data, only intra-check order
    # matters. Sequential generator checks give a conservative exact reference.
    for k,S in enumerate(GENS):
        s=start+6*k; q=checks[k]; f=flags[k]
        plus=typ=='X'
        c.add(s-1,f'reset q[{q}];','prep')
        c.add(s-1,f'reset q[{f}];','prep')
        c.add(s-1,f'h q[{q if plus else f}];','prep')
        def edge(t,u,v): c.cx(t,u,v) if plus else c.cx(t,v,u)
        edge(s,q,D[S[0]]); edge(s+1,q,f)
        edge(s+2,q,D[S[1]]); edge(s+3,q,D[S[2]])
        edge(s+4,q,f); edge(s+5,q,D[S[3]])
        x=c.read(s+6,q,'X' if plus else 'Z'); y=c.read(s+5,f,'Z' if plus else 'X')
        c.dets += [f'c[{x}]',f'c[{y}]']
    if typ=='Z':
        # Move the Steane tail after the sequential flags without touching pre.
        c.ops=[(t+10 if ((r=='prep' and set(map(int,re.findall(r'q\[(\d+)\]',s))) <= set(A+B)) or (t>=41 and set(map(int,re.findall(r'q\[(\d+)\]',s))) & set(A+B))) else t,s,r) for t,s,r in c.ops]
    return c.save('hybrid'+typ)

def generate():
    rows=[]
    rows.append(standard())
    rows.append(standard('sync_read',ar=35,cr=35))
    rows.append(standard('earlyA',a=32,ar=34))
    rows.append(standard('earlyA_sync',a=32,ar=35,cr=35))
    rows.append(reverse())
    rows.append(standard('C_after',verify_after=True,br=36))
    rows.append(standard('reuseC',tail='reuseC'))
    # Dummy reuse needs room for initialization after measuring A: move only
    # A's measurement earlier to 33 by coupling at32, tdg33; B remains34.
    rows.append(standard('dummyR',a=32,ar=33,tail='dummyR'))
    rows.append(standard('dummyM',a=32,ar=33,tail='dummyM'))
    rows.append(standard('onlyX',omit='A'))
    rows.append(standard('onlyZ',omit='B'))
    rows.extend(repeat(k) for k in 'XZ')
    rows.extend(hybrid(k) for k in 'XZ')
    (HERE/'manifest.json').write_text(json.dumps(rows,indent=2)+'\n')

if __name__=='__main__': generate()
