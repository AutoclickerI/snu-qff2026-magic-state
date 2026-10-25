"""Matching of every sub-gate survivor's simultaneous native contacts.
Allows checker-index permutations, fresh starts on any non-block cell, and
ignores every preparation/routing conflict. Infeasibility survives these relaxations.
"""
import json,itertools
from pathlib import Path
H=Path(__file__).resolve().parent
ROOT=H.parents[2]

def adj(a,b):return abs(a//6-b//6)+abs(a%6-b%6)==1

def match(cands):
    order=sorted(range(len(cands)),key=lambda i:len(cands[i]));chosen={}
    def dfs(k,used):
        if k==len(order):return dict(chosen)
        i=order[k]
        for q in cands[i]:
            if q not in used:
                chosen[i]=q;r=dfs(k+1,used|{q})
                if r is not None:return r
        return None
    return dfs(0,set())

def test(name,roles):
    occupied=set(sum([roles[k] for k in 'DABC'],[]));free=sorted(set(range(36))-occupied)
    rows=[]
    for checker in ('A','C'):
        options=[];checker_contacts=[]
        for d in roles['D']:
            per={f:[q for q in roles[checker] if adj(f,q)] for f in free if adj(d,f)}
            checker_contacts.append(per);options.append([f for f,cs in per.items() if cs])
        assignment=match(options)
        rows.append(dict(checker=checker,candidates=options,all_contacts=checker_contacts,
                         fresh_helper_matching=assignment,blocked_outputs=[roles['D'][i] for i,x in enumerate(options) if not x],
                         result='infeasible even before checker matching and preparation' if assignment is None else 'needs checker matching'))
    return dict(layout=name,roles=roles,free_cells=free,checks=rows,
                tick_contract={'T-2':'D->A, B->C, fresh-helper init','T-1':'B->D and helper->checker; helper and checker occupied',
                               'T':'helper->D and checker/B readout; helper unmeasured'},
                relaxation='permute checker partners arbitrarily; disregard prefix and preparation occupancy')

if __name__=='__main__':
    rows=[test('v37b',dict(D=[6,20,19,10,2,22,16],A=[7,14,13,9,8,21,15],B=[12,26,25,11,3,28,17],C=[18,27,24,5,4,29,23]))]
    for name in ('compact','joint'):
        p=ROOT/'work/lanes/SQUARE'/f'layout_{name}.json'
        if p.exists():
            z=json.loads(p.read_text())
            if all(k in z for k in 'DABC'):rows.append(test('SQUARE '+name,{k:z[k] for k in 'DABC'}))
    (H/'logs/grid_test.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows),flush=True)
