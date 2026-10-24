#!/usr/bin/env python3
"""Build PRE3 prefix release variants and grid-free Steane suffixes."""
from __future__ import annotations
import json, re
from pathlib import Path
ROOT=Path('/home/jihoon/competitions/quantumn'); OUT=ROOT/'work/lanes/PRE3'; SRC=ROOT/'work/lanes/MAIN/spec/v16e.qasm'
DATA=[0,20,7,4,3,15,8]; FREE=[5,11,12,16,17,18,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35]
PIV=[0,1,3]; LAYERS0=[[(0,2),(1,6),(3,5)],[(0,4),(1,2),(3,6)],[(0,6),(1,5),(3,4)]]
PRE_DET=['c[0]','c[1]','c[2]','c[3]','c[4]','c[5]','c[6]','c[7]','c[8]','c[9]','c[10] c[7]','c[11]','c[12]','c[13]']
QRE=re.compile(r'q\[(\d+)\]')
def read_prefix():
    lines=SRC.read_text().splitlines(); b=[i for i,l in enumerate(lines) if l.startswith('barrier')]; end=b[32]
    raw=lines[:end+1]; assert sum(l.startswith('barrier') for l in raw)==33; return raw
def layerize(raw):
    head=[]; layers=[]; cur=[]
    for l in raw:
        if l.startswith(('OPENQASM','include','qreg','creg')): head.append(l); continue
        if l.startswith('barrier'): layers.append(cur); cur=[]
        elif l.strip() and not l.startswith('//'): cur.append(l)
    assert not cur and len(layers)==33; return head,layers
def qs(op): return sorted(set(map(int,QRE.findall(op))))
def barrier(qubits): return 'barrier '+','.join(f'q[{q}]' for q in sorted(set(qubits)))+';'
def touched(ops):
    out=set()
    for op in ops: out.update(qs(op))
    return sorted(out)
def prefix_layers(kind='base'):
    head,layers=layerize(read_prefix())
    move19=kind in ('q19_11','q19_15','q19_13_earliest','q19_13_prompt','active_q19_13')
    move13=kind in ('q13_19','q19_13_earliest','q19_13_prompt','active_q19_13')
    if move19:
        old='measure q[19] -> c[3];'; assert old in layers[32]; layers[32].remove(old)
        layers[11 if kind!='q19_13_prompt' else 15].append(old)
    if move13:
        assert 'h q[13];' in layers[32] and 'measure q[13] -> c[6];' in layers[32]
        layers[32].remove('h q[13];'); layers[32].remove('measure q[13] -> c[6];')
        layers[19].extend(['h q[13];','measure q[13] -> c[6];'])
    masks=[]
    for i,ops in enumerate(layers):
        if kind in ('active','active_q19_13'): mask=set(touched(ops))
        else:
            mask=set(range(36))-{18,24,30,31,32,33,34,35}
            if move19 and i>=(11 if kind!='q19_13_prompt' else 15)+1: mask.discard(19)
            if move13 and i>=20: mask.discard(13)
        masks.append(mask)
    return head,layers,masks

def build_prefix(kind='base'):
    head,layers,masks=prefix_layers(kind); out=list(head)
    for ops,mask in zip(layers,masks): out.extend(ops); out.append(barrier(mask))
    return '\n'.join(out)+'\n'
def enc(cells,plus,t0):
    out=[]
    for i,q in enumerate(cells):
        out.append((t0-1,f'reset q[{q}];'))
        if (i in PIV)!=plus: out.append((t0-1,f'h q[{q}];'))
    for k,layer in enumerate(LAYERS0):
        for c,t in layer:
            a,b=(cells[t],cells[c]) if plus else (cells[c],cells[t]); out.append((t0+k,f'cx q[{a}],q[{b}];'))
    return out
def build_full(kind,R=33):
    head,layers,masks=prefix_layers(kind)
    A,B,C=FREE[:7],FREE[7:14],FREE[14:21]
    by={}
    # Prepare all three blocks ALAP in nominal steps 29..32, as gf33.py does.
    for t,st in enc(B,False,R-3)+enc(C,False,R-3)+enc(A,True,R-3): by.setdefault(t,[]).append(st)
    for t,ops in by.items():
        assert 0<=t<33
        layers[t].extend(ops); masks[t].update(touched(ops))
    n=14; bits={}; r0=[]; r1=[]; r2=[]
    for i in range(7): r0 += [f'cx q[{DATA[i]}],q[{A[i]}];',f'cx q[{B[i]}],q[{C[i]}];']
    for k,cells in [('a',A),('c',C)]:
        for i,q in enumerate(cells): bits[k,i]=n; r1.append(f'measure q[{q}] -> c[{n}];'); n+=1
    r1 += [f'cx q[{B[i]}],q[{DATA[i]}];' for i in range(7)]
    for i,q in enumerate(B): bits['b',i]=n; r2 += [f'h q[{q}];',f'measure q[{q}] -> c[{n}];']; n+=1
    suffix={R:r0,R+1:r1,R+2:r2}
    # Prefix + ALAP block prep preserve the variant's release masks.  Round layers
    # start at the requested boundary; all round participants are synchronized.
    lines=list(head)
    for t,(ops,mask) in enumerate(zip(layers,masks)):
        lines.extend(ops); lines.append(barrier(mask))
    gbar=set(range(36))
    for t in range(R,R+3):
        lines.extend(suffix[t])
        if t<R+2: lines.append(barrier(gbar))
    # Preserve the v16 creg (it contains the four diagnostic records c39..42).
    lines=[('creg c[47];' if l.startswith('creg ') else l) for l in lines]
    gens=[[0,2,4,6],[1,2,5,6],[3,4,5,6]]; dets=list(PRE_DET)
    for k in ['a','b','c']:
        for S in gens: dets.append(' '.join(f'c[{bits[k,i]}]' for i in S))
    dets.append(' '.join(f'c[{bits["c",i]}]' for i in range(7)))
    lines += [f'// DETECTOR {x}' for x in dets]
    return '\n'.join(lines)+'\n'
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    kinds=['base','q19_11','q19_15','q13_19','q19_13_earliest','q19_13_prompt','active','active_q19_13']
    for k in kinds:
        (OUT/f'{k}.qasm').write_text(build_full(k,33)); (OUT/f'{k}.json').write_text(json.dumps({'data_qubits':DATA,'variant':k,'grid_free':True,'R':33},indent=2)+'\n'); print(k)
if __name__=='__main__': main()
