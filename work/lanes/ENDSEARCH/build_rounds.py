"""Saved grid-free witnesses for reviewer 14's square-round claim."""
import json
from pathlib import Path

H = Path(__file__).resolve().parent
GENS = [{0,2,4,6}, {1,2,5,6}, {3,4,5,6}]
ENC = [[(0,2),(1,5),(3,6)],[(0,4),(1,6),(3,5)],[(0,6),(1,2),(3,4)]]
PIV = {0,1,3}
D,A,B,C = [list(range(j,j+7)) for j in (0,7,14,21)]

class Circuit:
    def __init__(self):
        self.ops = {}; self.dets=[]; self.bit=0; self.frames=[]
    def add(self,t,line): self.ops.setdefault(t,[]).append(line)
    def cx(self,t,a,b): self.add(t,f'cx q[{a}],q[{b}];')
    def reset(self,t,q,plus=False):
        self.add(t,f'reset q[{q}];')
        if plus:self.add(t,f'h q[{q}];')
    def prep(self,block,t,plus):
        for i,q in enumerate(block):self.reset(t,q,(i not in PIV) if plus else (i in PIV))
        for k,layer in enumerate(ENC):
            for a,b in layer:self.cx(t+1+k,block[b] if plus else block[a],block[a] if plus else block[b])
    def read(self,t,q,x=False):
        if x:self.add(t,f'h q[{q}];')
        b=self.bit; self.bit+=1; self.add(t,f'measure q[{q}] -> c[{b}];'); return b
    def readblock(self,t,block,x=False,logical=False):
        bits=[self.read(t,q,x) for q in block]
        for s in GENS+([set(range(7))] if logical else []):self.dets.append([bits[i] for i in sorted(s)])
        return bits
    def magic(self):
        # |T> on position 2, fanout to the logical representative {2,4,5},
        # then the CSS encoder. This preparation is perfect in round tests.
        for q in D:self.reset(0,q,q in PIV or q==2)
        self.add(1,'t q[2];'); self.cx(2,2,4); self.cx(3,2,5)
        for k,layer in enumerate(ENC):
            for a,b in layer:self.cx(4+k,a,b)
    def save(self,name,**meta):
        lines=['OPENQASM 2.0;','include "qelib1.inc";','qreg q[36];',f'creg c[{max(1,self.bit)}];']
        barrier='barrier '+','.join(f'q[{q}]' for q in range(36))+';'
        for t in range(max(self.ops)+1):
            if t:lines.append(barrier)
            lines.extend(self.ops.get(t,[]))
        lines += ['// DETECTOR '+' '.join(f'c[{b}]' for b in row) for row in self.dets]
        lines += self.frames
        stem=H/'builds'/name
        stem.with_suffix('.qasm').write_text('\n'.join(lines)+'\n')
        stem.with_suffix('.json').write_text(json.dumps(dict(data_qubits=D,grid_free=True,**meta),indent=2)+'\n')

def build(kind):
    c=Circuit(); c.magic()
    c.prep(A,3,kind!='eraser');c.prep(B,3,False);c.prep(C,3,kind!='standard')
    for d,a,b,cc in zip(D,A,B,C):
        c.cx(7,d,a);c.cx(7,b,cc);c.cx(8,b,d)
        if kind!='standard':c.cx(8,cc,a)
    c.readblock(8 if kind=='standard' else 9,A)
    c.readblock(9,B,True)
    cb=c.readblock(8 if kind=='standard' else 9,C,kind!='standard',kind!='eraser')
    if kind=='eraser':c.frames=['// FRAME_Z(0) '+' '.join(f'c[{b}]' for b in cb)]
    c.save('round_'+kind,round_start=7,noise_start=7,change=f'{kind}: perfect input/preparations, full round noise')

if __name__=='__main__':
    for kind in ('standard','square','eraser'):build(kind)
