import json, os, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1] / 'LAYOUT2'))
import merge

def suffix_jobs(preps, order, lay, moves):
    units=[]
    for path in moves:
        for s,d in zip(path,path[1:]):
            units += [([f'reset q[{d}];'],[d]),([f'cx q[{s}],q[{d}];'],[s,d]),([f'cx q[{d}],q[{s}];'],[s,d])]
    for k in order:
        if k not in preps: continue
        p=preps[k]; ops,piv=p['ops'],p['pivots']
        if k=='bc':
            cells=sorted(set(lay['b']+lay['c']) | {q for L in ops for e in L for q in e})
        else:
            cells=list(lay[k])
        first={}
        for t,L in enumerate(ops):
            for u,v in L:
                first.setdefault(u,t); first.setdefault(v,t)
        for q in cells: first.setdefault(q,0)
        for q in sorted(first,key=first.get):
            units.append(([f'reset q[{q}];']+([f'h q[{q}];'] if q in piv else []),[q]))
        for L in ops:
            for u,v in L: units.append(([f'cx q[{u}],q[{v}];'],[u,v]))
    return units
merge.suffix_jobs=suffix_jobs

def run(layout_file,a_file,bc_file,out,early=False):
    lay=json.loads(Path(layout_file).read_text()); A=json.loads(Path(a_file).read_text()); BC=json.loads(Path(bc_file).read_text())
    if isinstance(A,list): A=A[0]
    assert all(A['danger_vector_units'][j+1]==0 for j in lay['M'])
    anc=lay['cat']; seen={anc[0]}; tree=[]
    while len(seen)<len(anc):
        e=next((u,v) for u in seen for v in anc if v not in seen and abs(u//6-v//6)+abs(u%6-v%6)==1)
        tree.append(e); seen.add(e[1])
    gad=dict(timing='late',M=lay['M'],anc=anc,tree=tree,checks=[(u,lay['a'][j],1) for u,j in zip(anc,lay['M'])],mx=2,early_other=early)
    txt,data,R,pre=merge.build({'a':A,'bc':BC},['a','bc'],lay,lay['moves'],gad)
    out=Path(out); out.with_suffix('.qasm').write_text(txt)
    out.with_suffix('.json').write_text(json.dumps({'data_qubits':data,'layout':str(layout_file),'A':str(a_file),'BC':str(bc_file),'R':R,'pre_end':pre,'M':lay['M'],'cat':anc,'cx':txt.count('cx ')},indent=2)+'\n')
    print(out,'R',R,'pre_end',pre,'CX',txt.count('cx '),flush=True)

if __name__=='__main__':
    run(*sys.argv[1:5], early=bool(int(sys.argv[5])) if len(sys.argv)>5 else False)
