"""Enumerate native two-layer A readouts and rank complete noisy circuits.

The readout may measure any factorized X observable of the encoded-plus
ancilla, including logical and stabilizer representatives. The remaining
Z reads retain the data bit-syndrome information. Full raw checks are used.
"""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='1'
import argparse,contextlib,copy,io,itertools,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'work/tools'))
sys.path.insert(0,str(ROOT/'work/lanes/NATIVE2_20261027'))
sys.path.insert(0,str(ROOT/'work/lanes/PREFIX2_20261027'))
from measured_assemble import assemble
from pairs import audit
from relaxed_a import span

A=[7,14,13,9,8,21,15]
D=[6,20,19,10,2,22,16]
B=[12,26,25,11,3,28,17]
TARGET=span([85,102,120,7])


def transform(state,gates):
    for a,b in gates:
        state=span(r^(1<<b) if r>>a&1 else r for r in state)
    return state


def choices(per_space):
    edges=[(i,j) for i,a in enumerate(A) for j,b in enumerate(A) if i<j and abs(a//6-b//6)+abs(a%6-b%6)==1]
    layers=[()]
    for n in range(1,4):
        for ee in itertools.combinations(edges,n):
            if len({q for e in ee for q in e})!=2*n:continue
            for flips in itertools.product((False,True),repeat=n):
                layers.append(tuple(e[::-1] if flip else e for e,flip in zip(ee,flips)))
    groups={};total=0
    for one,two in itertools.product(layers,repeat=2):
        if not one and not two:continue
        gates=one+two
        state=transform(TARGET,gates)
        plus=[q for q in range(7) if len(span([*state,1<<q]))==4]
        if not plus:continue
        seen=[]
        for q in plus:
            row=1<<q
            for a,b in reversed(gates):
                if row>>a&1:row^=1<<b
            assert len(span([*TARGET,row]))==4
            seen.append(row)
        space=span(seen);early=sorted({q for e in one for q in e})
        row=dict(layers=[[list(e) for e in one],[list(e) for e in two]],
                 x_measure_indices=plus,x_space=list(space),early_data_indices=early,
                 decoder_cx=len(gates),early_data_count=len(early))
        score=(len(gates),len(early),sum(q in {0,4} for q in early))
        groups.setdefault(space,[]).append((score,row));total+=1
    selected=[]
    for space,rr in sorted(groups.items()):
        rr.sort(key=lambda v:v[0]);seen=set()
        for score,row in rr:
            # Retain distinct physical readout/early-data assignments.
            key=tuple(row['x_measure_indices']),tuple(row['early_data_indices'])
            if key in seen:continue
            seen.add(key);selected.append(row)
            if len(seen)>=per_space:break
    return selected,dict(layer_count=len(layers),qualifying_decoders=total,distinct_x_spaces=len(groups))


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--per-space',type=int,default=3)
    ap.add_argument('--start',type=int,default=0);ap.add_argument('--stop',type=int)
    args=ap.parse_args()
    selected,summary=choices(args.per_space)
    folder=HERE/'logical_readout';folder.mkdir(exist_ok=True)
    (folder/'choices.json').write_text(json.dumps(dict(**summary,choices=selected),indent=2)+'\n')
    native=ROOT/'work/lanes/NATIVE2_20261027'
    bc=json.loads((native/'old_b_module.json').read_text())
    apath=ROOT/'work/lanes/END2_20261027/sol/a_plus_R45.json'
    results=[]
    print(json.dumps(dict(**summary,selected=len(selected))),flush=True)
    for index,row in enumerate(selected):
        if index<args.start or (args.stop is not None and index>=args.stop):continue
        bdoc=copy.deepcopy(bc);term=[];last={}
        early=set(row['early_data_indices'])
        for i,(d,a) in enumerate(zip(D,A)):
            t=0 if i in early else 1
            term.append(['CX',[d,a],t,None]);last[a]=t
        for layer,edges in enumerate(row['layers'],start=1):
            for i,j in edges:
                term.append(['CX',[A[i],A[j]],layer,None]);last[A[i]]=last[A[j]]=layer
        term += [['CX',[b,d],2,None] for b,d in zip(B,D)]
        term += [['MX' if i in row['x_measure_indices'] else 'M',[a],last[a]+1,None] for i,a in enumerate(A)]
        term += [['MX',[b],3,None] for b in B]
        bdoc['terminal_operations']=term
        bpath=folder/f'readout_{index}.json';bpath.write_text(json.dumps(bdoc,indent=2)+'\n')
        with contextlib.redirect_stdout(io.StringIO()):
            r=assemble(apath,bpath,0,0,f'logical_readout_{index}',terminal_start=45,do_singles=True)
        result=dict(index=index,**row,stem=r['stem'],raw=r['raw'],cx=r['cx'],ticks=r['ticks'],c1=r.get('singles',{}).get('c1'))
        if r['raw']['ok'] and result['c1']<1e-10:
            with contextlib.redirect_stdout(io.StringIO()):
                pairs=audit(r['stem'],folder/f'pairs_{index}.json')
            result['c2']=pairs['c2']
        results.append(result)
        (folder/f'results_{args.start}.json').write_text(json.dumps(results,indent=2)+'\n')
        print(json.dumps(result),flush=True)


if __name__=='__main__':main()
