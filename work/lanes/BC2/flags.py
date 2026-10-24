"""Enumerate deterministic two-CX Z flags on free cells, then merge fully."""
import hashlib
import itertools
import json
from pathlib import Path
import re
import subprocess
import sys

import ft
import merge
from steane_full import LAYOUTS, MOVES

ROOT=Path('/home/jihoon/competitions/quantumn')
P=str(ROOT/'.venv/bin/python')
BASE=json.loads(Path('baseline_prep.json').read_text())
A=json.loads((ROOT/'work/lanes/DR/prepA_L5_s7307.json').read_text())
NEIGHBORS={18:[12,19],24:[25],32:[26],33:[27],34:[28],35:[29]}
original=merge.suffix_jobs


def emit(flags, name):
    # flag=(helper, start boundary, start cell, end boundary, end cell)
    helpers=[f[0] for f in flags]
    assert len(set(helpers))==len(helpers)
    def suffix(preps,order,lay,moves):
        units=original({'a':A},['a'],lay,moves)
        cells=ft.B+ft.C
        for q in cells+helpers:
            units.append(([f'reset q[{q}];']+([f'h q[{q}];'] if q in BASE['pivots'] else []),[q]))
        for t in range(len(BASE['ops'])+1):
            for k,(h,t0,q0,t1,q1) in enumerate(flags):
                if t==t0: units.append(([f'cx q[{q0}],q[{h}];'],[q0,h]))
                if t==t1:
                    units.append(([f'cx q[{q1}],q[{h}];'],[q1,h]))
                    units.append(([f'measure q[{h}] -> c[{35+k}];'],[h]))
            if t<len(BASE['ops']):
                for u,v in BASE['ops'][t]: units.append(([f'cx q[{u}],q[{v}];'],[u,v]))
        return units
    merge.suffix_jobs=suffix
    try: text,data,R,pre_end=merge.build({'a':A,'bc':BASE},['a','bc'],LAYOUTS['L5'],MOVES['L5'])
    finally: merge.suffix_jobs=original
    text=text.replace('creg c[35];',f'creg c[{35+len(flags)}];')
    text+=''.join(f'// DETECTOR c[{35+k}]\n' for k in range(len(flags)))
    # The MAIN/minit transform, performed by its actual script below.
    Path(name+'.qasm').write_text(text)
    Path(name+'.json').write_text(json.dumps(dict(data_qubits=data,rule='extra Z flags',flags=flags,
        depth=R-36,prep_cx=82+2*len(flags),round_start=R,pre_end=pre_end),indent=2))
    subprocess.run([P,str(ROOT/'work/lanes/MAIN/minit.py'),name,'.','27,29'],check=True,stdout=subprocess.DEVNULL)
    measured=name+'_m27_29'
    meta=json.loads(Path(name+'.json').read_text())
    meta['first_use_measured']=[27,29]
    Path(measured+'.json').write_text(json.dumps(meta,indent=2))
    return measured,R


def proposals():
    ops=BASE['ops']; cells=ft.B+ft.C
    state={q:0 for q in cells}
    for k,q in enumerate(BASE['pivots']): state[q]=1<<k
    values=[state.copy()]
    for layer in ops:
        for u,v in layer: state[v]^=state[u]
        values.append(state.copy())
    sources=ft.sources(BASE,cells)
    paths=[]; final=[]
    for t,qs in sources:
        e=set(); path=[]
        for k in range(len(ops)+1):
            if k==t: e^=set(qs)
            path.append(e.copy())
            if k<len(ops):
                for u,v in ops[k]:
                    if u in e: e^={v}
        paths.append(path); final.append(e)
    out=[]
    for h,neighbors in NEIGHBORS.items():
        slots=[(t,q) for t in range(len(ops)+1) for q in neighbors]
        for (t0,q0),(t1,q1) in itertools.combinations(slots,2):
            if t0>=t1 or values[t0][q0]!=values[t1][q1]: continue
            # Surrogate used only to order full-circuit evaluations.
            caught=[i for i,path in enumerate(paths) if (q0 in path[t0]) != (q1 in path[t1])]
            clean=sum(ft.violates(final[i],'clean') for i in caught)
            robust=sum(ft.violates(final[i],'robust') for i in caught)
            dangerous=sum(ft.dangerous(ft.sig(final[i],ft.B)) for i in caught)
            value=3*clean+2*robust+dangerous
            if value: out.append((value,(h,t0,q0,t1,q1),clean,robust,dangerous))
    return sorted(out,reverse=True)


if __name__=='__main__':
    candidates=[]; hashes=set(); counts={}
    for rank,(value,flag,clean,robust,dangerous) in enumerate(proposals()):
        h=flag[0]
        if counts.get(h,0)>=5: continue
        name=f'flag_{h}_{flag[1]}q{flag[2]}_{flag[3]}q{flag[4]}'
        stem,R=emit([flag],name)
        digest=hashlib.sha256(Path(stem+'.qasm').read_bytes()).hexdigest()
        if digest in hashes:
            for s in (name,stem):
                Path(s+'.qasm').unlink(); Path(s+'.json').unlink()
            continue
        hashes.add(digest); counts[h]=counts.get(h,0)+1
        candidates.append(dict(stem=stem,round=R,surrogate=value,clean_caught=clean,robust_caught=robust,
                               dangerous_caught=dangerous,flag=flag))
    Path('flags_manifest.json').write_text(json.dumps(candidates,indent=2))
    print(json.dumps(candidates,indent=2))
