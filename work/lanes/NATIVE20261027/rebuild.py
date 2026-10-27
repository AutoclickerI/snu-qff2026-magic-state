"""Construct and price a fresh logical-check architecture (no copied circuits).

Abstract control first; native placement is an explicit subsequent experiment.
Every emitted candidate has full barriers and all deterministic check rows.
"""
from __future__ import annotations
import os
for _k in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[_k] = '1'
import argparse, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT/'work/tools'))
from qtools import write_stem, price

GENS = [{0,2,4,6}, {1,2,5,6}, {3,4,5,6}]
ENC = [[(0,2),(1,5),(3,6)],[(0,4),(1,6),(3,5)],[(0,6),(1,2),(3,4)]]
PIV = {0,1,3}

class Circuit:
    def __init__(self):
        self.ops = {}; self.dets=[]; self.bit=0; self.roles={}
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
        b=self.bit;self.bit+=1;self.add(t,f'measure q[{q}] -> c[{b}];');return b
    def readblock(self,t,block,x=False,logical=False):
        bits=[self.read(t,q,x) for q in block]
        for s in GENS+([set(range(7))] if logical else []):self.dets.append([bits[i] for i in sorted(s)])
        return bits
    def magic(self,block,t=0):
        for i,q in enumerate(block):self.reset(t,q,i in PIV or i==2)
        self.add(t+1,f't q[{block[2]}];')
        self.cx(t+2,block[2],block[4]);self.cx(t+3,block[2],block[5])
        for k,layer in enumerate(ENC):
            for a,b in layer:self.cx(t+4+k,block[a],block[b])
    def cat(self,block,t,tree=0):
        for i,q in enumerate(block):self.reset(t,q,i==0)
        layers=[[(0,1)],[(0,2),(1,3)],[(0,4),(1,5),(2,6)]] if tree==0 else [[(0,1),(2,3),(4,5)],[(1,2),(3,4),(5,6)]]
        for k,layer in enumerate(layers):
            for a,b in layer:self.cx(t+1+k,block[a],block[b])
    def text(self):
        lines=['OPENQASM 2.0;','include "qelib1.inc";','qreg q[36];',f'creg c[{max(1,self.bit)}];']
        barrier='barrier '+','.join(f'q[{q}]' for q in range(36))+';'
        for t in range(max(self.ops)+1):
            if t:lines.append(barrier)
            lines.extend(self.ops.get(t,[]))
        lines += ['// DETECTOR '+' '.join(f'c[{b}]' for b in row) for row in self.dets]
        return '\n'.join(lines)+'\n'

def build(precheck=True,cats=2,verify_b=True,kind='square',cat_order=None,
          reuse_a=False,reuse_b=False,R=None,verify_before=False,cat_gap=0):
    c=Circuit()
    D,A,B,C,K=[list(range(s,s+7)) for s in (0,7,14,21,28)]
    c.magic(D)
    if precheck:
        c.prep(A,3,True);c.prep(B,3,False)
        for d,a,b in zip(D,A,B):c.cx(7,d,a);c.cx(8,b,d)
        if not reuse_a:c.readblock(8,A)
        if not reuse_b:c.readblock(9,B,True)
        t=9
    else:t=7
    for i,cat in enumerate((C,K)[:cats]):
        c.cat(cat,t-3+i+cat_gap*i)
    for d in D:c.add(t,f't q[{d}];')
    for i,cat in enumerate((C,K)[:cats]):
        for j,d in enumerate(D):c.cx(t+1+i+cat_gap*i,cat[(cat_order or list(range(7)))[j]],d)
        c.dets.append([c.read(t+2+i+cat_gap*i,q,True) for q in cat])
    for d in D:c.add(t+1+cats+cat_gap*(cats-1),f'tdg q[{d}];')
    # Source B starts soon after the precheck. Terminal A/C wait until needed.
    R=t+8 if R is None else R
    if not reuse_b:c.prep(B,R-7 if verify_b else R-4,False)
    if verify_b:
        c.reset(R-4,35)
        for j,i in enumerate((0,1,2)):c.cx(R-3+j,B[i],35)
        c.dets.append([c.read(R,35)])
    if not reuse_a:c.prep(A,R-4,True)
    c.prep(C,R-4,kind!='standard')
    for d,a,b,cc in zip(D,A,B,C):
        c.cx(R,d,a);c.cx(R,b,cc);c.cx(R+1,b,d)
        if kind!='standard':c.cx(R+1,cc,a)
    c.readblock(R+1 if kind=='standard' else R+2,A)
    c.readblock(R+2,B,True)
    c.readblock(R+1 if kind=='standard' else R+2,C,kind!='standard',True)
    c.roles=dict(D=D,A=A,B=B,C=C,K=K)
    return c,D

def build_joint_flags(R=18,cat2_time=16,flag_pairs=((0,1),(1,2),(2,3))):
    """Extract GHZ hook flags through the already measured precheck blocks.

    A's Z records are direct parity meters after D->A. Transversal H turns
    B's pending X readout into Z records, allowing the second GHZ's flags to
    share the same readout. The final A/B resource roles are then exchanged
    so the B verification gets the earlier released block.
    """
    c=Circuit();D,PA,PB,C,K=[list(range(s,s+7)) for s in (0,7,14,21,28)]
    c.magic(D);c.prep(PA,3,True);c.prep(PB,3,False)
    for d,a,b in zip(D,PA,PB):c.cx(7,d,a);c.cx(8,b,d)
    c.cat(C,4);c.cat(K,6)
    pivots=(0,1,3)
    for j,(u,v) in enumerate(flag_pairs):
        c.cx(8,C[u],PA[pivots[j]]);c.cx(9,C[v],PA[pivots[j]])
        c.cx(10,K[u],PB[pivots[j]]);c.cx(11,K[v],PB[pivots[j]])
    c.readblock(10,PA)
    for b in PB:c.add(9,f'h q[{b}];')
    c.readblock(12,PB)
    for d in D:c.add(9,f't q[{d}];')
    for j,d in enumerate(D):c.cx(10,C[j],d);c.cx(cat2_time,K[j],d)
    c.dets.append([c.read(11,q,True) for q in C])
    c.dets.append([c.read(cat2_time+1,q,True) for q in K])
    for d in D:c.add(cat2_time+1,f'tdg q[{d}];')
    A,B=PB,PA
    c.prep(B,R-7,False)
    c.reset(R-4,35)
    for j,i in enumerate((0,1,2)):c.cx(R-3+j,B[i],35)
    c.dets.append([c.read(R,35)])
    c.prep(A,R-4,True);c.prep(C,R-4,True)
    for d,a,b,cc in zip(D,A,B,C):
        c.cx(R,d,a);c.cx(R,b,cc);c.cx(R+1,b,d);c.cx(R+1,cc,a)
    c.readblock(R+2,A);c.readblock(R+2,B,True);c.readblock(R+2,C,True,True)
    c.roles=dict(D=D,A=A,B=B,C=C,K=K,precheck_A=PA,precheck_B=PB)
    return c,D

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--no-precheck',action='store_true');ap.add_argument('--cats',type=int,default=2);ap.add_argument('--no-verify-b',action='store_true');ap.add_argument('--kind',default='square');ap.add_argument('--price',action='store_true');ap.add_argument('--joint-flags',action='store_true');ap.add_argument('--cat2-time',type=int,default=12);ap.add_argument('--round',type=int,default=18);ap.add_argument('--cat-gap',type=int,default=0);args=ap.parse_args()
    if args.joint_flags:
        c,D=build_joint_flags(args.round,args.cat2_time)
        name=f'abstract_joint_flags_R{args.round}_cat2time{args.cat2_time}'
    else:
        c,D=build(not args.no_precheck,args.cats,not args.no_verify_b,args.kind,cat_gap=args.cat_gap)
        name=f'abstract_{args.kind}_pc{int(not args.no_precheck)}_cats{args.cats}_vb{int(not args.no_verify_b)}_gap{args.cat_gap}'
    lane=Path(__file__).resolve().parent
    stem=write_stem(c.text(),D,lane/'builds',name,source=dict(grid_free=True,roles=c.roles))
    print(stem,flush=True)
    if args.price:
        # This experiment deliberately has ideal connectivity. Do not put its
        # values into qtools' grid-valid price cache or alter the judge sources.
        import tprep.qasm as judge_qasm
        from qtools.pricing import _calculate
        old_adjacent=judge_qasm.adjacent
        try:
            judge_qasm.adjacent=lambda a,b: a!=b
            result=_calculate(c.text().encode(),D,1,save_basis=False)
        finally:
            judge_qasm.adjacent=old_adjacent
        result['grid_free']=True
        stem.with_suffix('.price.json').write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps(result,indent=2),flush=True)

if __name__=='__main__':main()
