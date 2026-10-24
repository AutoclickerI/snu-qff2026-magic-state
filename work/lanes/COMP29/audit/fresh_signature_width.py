"""Current v22 metadata and a dual-signature factor-graph width experiment."""
import re,json,sys,os
from pathlib import Path
from collections import Counter,defaultdict
import full_single_audit as fa
from dataclasses import dataclass
@dataclass
class Op:
    kind: str
    qs: tuple
    time: int
    bit: int | None = None
    line: int = 0
from tprep.qasm import _x_readouts,_x_preparations

ROOT=Path(__file__).resolve().parents[1]
STEM=Path(os.environ['QUANTUMN_REPO'])/'work/submissions/v22_r155'

def parse_current(src):
    if re.search(r'//\s*(FRAME_[XZ]|POSTSELECT)',src):
        raise ValueError('This prototype supports the unframed v22/v23 family only.')
    ops=[];dets=[];time=0
    for li,raw in enumerate(src.splitlines(),1):
        if raw.startswith('barrier'):time+=1;continue
        if raw.startswith('// DETECTOR'):
            dets.append(set(map(int,re.findall(r'c\[(\d+)\]',raw))))
        if not raw or raw.startswith(('//','OPENQASM','include','qreg','creg')):continue
        qs=tuple(map(int,re.findall(r'q\[(\d+)\]',raw)))
        bits=list(map(int,re.findall(r'c\[(\d+)\]',raw)))
        kind={'reset':'R','measure':'M','tdg':'T_DAG'}.get(raw.split()[0],raw.split()[0].upper())
        ops.append(Op(kind,qs,time,bits[0] if bits else None,li))
    lines=[op.kind+' '+' '.join(map(str,op.qs)) for op in ops]
    _x_readouts(lines,drop_h=True);_x_preparations(lines)
    ans=[]
    for op,line in zip(ops,lines):
        if line is None:continue
        op.kind={'T_DAG':'TDG'}.get(line.split()[0],line.split()[0]);ans.append(op)
    return ans,dets

def minfill(scopes):
    graph=defaultdict(set)
    for ss in scopes:
        for v in ss:graph[v].update(ss-{v})
    width=0;cost=0;order=[];sizes=[]
    while graph:
        def key(v):
            n=graph[v];fill=sum(len(n-{u}-graph[u]) for u in n)//2
            return fill,len(n),v
        v=min(graph,key=key);n=graph.pop(v);width=max(width,len(n));cost+=2**len(n)
        order.append(v);sizes.append(len(n))
        for u in n:graph[u].discard(v);graph[u].update(n-{u})
    return dict(width=width,work_entries=cost,order=order,bucket_sizes=sizes)
