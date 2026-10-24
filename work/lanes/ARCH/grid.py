"""Real-grid realization of the winning readout-coding mechanism on v17a."""
import json
import re
from pathlib import Path
from build import HERE,ROOT
from ortools.sat.python import cp_model

L={'d':[0,20,7,10,3,22,21], 'a':[1,14,8,9,2,16,15],
   'b':[6,26,13,11,4,23,27], 'c':[12,25,19,17,5,29,28]}
def near(a,b): return abs(a//6-b//6)+abs(a%6-b%6)==1

def build(name,pairs):
    original=(ROOT/'work/lanes/MAIN/spec/v17a.qasm').read_text()
    prefix,suffix=original.split('// region round\n')
    ls=suffix.splitlines(); firstbar=next(i for i,l in enumerate(ls) if l.startswith('barrier'))
    head=ls[:firstbar+1]; bar=head[-1]
    bits={q:14+i for i,q in enumerate(L['a'])}|{q:21+i for i,q in enumerate(L['c'])}|{q:28+i for i,q in enumerate(L['b'])}
    dets=[l for l in ls if l.startswith('// DETECTOR')]
    # Invert v17a's two classical readout transforms, then apply new matching.
    old={bits[16]:bits[17],bits[25]:bits[19]}
    new={bits[v]:bits[u] for u,v in pairs}
    cooked=[]
    for line in dets:
        bs=set(map(int,re.findall(r'c\[(\d+)\]',line)))
        for mapping in (old,new):
            before=set(bs)
            for v,u in mapping.items():
                if v in before: bs^={u}
        cooked.append('// DETECTOR '+' '.join(f'c[{i}]' for i in sorted(bs)))
    occupied=[q for p in pairs for q in p]
    assert len(occupied)==len(set(occupied)) and all(near(u,v) for u,v in pairs)
    r1=[f'cx q[{u}],q[{v}];' for u,v in pairs]
    r1 += [f'cx q[{u}],q[{v}];' for u,v in zip(L['b'],L['d'])]
    r1 += [f'measure q[{q}] -> c[{bits[q]}];' for q in L['a']+L['c'] if q not in occupied]
    r2=[f'measure q[{q}] -> c[{bits[q]}];' for q in occupied]
    for q in L['b']: r2 += [f'h q[{q}];',f'measure q[{q}] -> c[{bits[q]}];']
    text=prefix+'// region round\n'+'\n'.join(head+r1+[bar]+r2+cooked)+'\n'
    (HERE/(name+'.qasm')).write_text(text)
    meta=json.loads((ROOT/'work/lanes/MAIN/spec/v17a.json').read_text())
    meta.update(name=name,grid_free=False,readout_pairs=pairs,source='v17a prefix and preparation unchanged; ARCH late readout matching',cx=text.count('cx '),round_ops=[])
    import tprep.qasm as tq
    from tprep.noise import schedule
    native,_,errors=tq.convert(text)
    assert not errors,errors
    prog,steps,_=schedule(native)
    R=max(t for ins,ss in zip(prog,steps) if ins.name=='CX' and ins.qubits==[L['d'][0],L['a'][0]] for _,t in ss)
    meta.update(R=R,A_coupling_first=R,A_coupling_last=R,B_check_step=R,
                B_data_coupling_last=R+1,last_round_cx=R+1,end=R+2)
    # Native time labels for the three round layers; used by exact ablations.
    for t,lines in [(R,head[:-1]),(R+1,r1),(R+2,r2)]:
        for l in lines:
            qs=sorted(map(int,re.findall(r'q\[(\d+)\]',l)))
            meta['round_ops'].append(str(t)+':'+','.join(map(str,qs)))
    (HERE/(name+'.json')).write_text(json.dumps(meta,indent=2)+'\n')
    return meta

def square_fit(data):
    # Every direct D-A-C-B cycle must be a unit grid square. Proves the
    # obstruction without imposing any encoder connectivity restrictions.
    m=cp_model.CpModel(); choices={}; cells={q:[] for q in range(36)}
    for i,d in enumerate(data):
        choices[i]=[]
        for r in range(5):
            for c in range(5):
                sq={6*r+c,6*r+c+1,6*r+c+6,6*r+c+7}
                if d not in sq or (sq&set(data))!={d}: continue
                x=m.NewBoolVar(f'{i}_{r}_{c}');choices[i].append((x,sorted(sq)))
                for q in sq: cells[q].append(x)
        m.AddExactlyOne([v for v,_ in choices[i]])
    for vs in cells.values():
        if vs: m.AddAtMostOne(vs)
    solver=cp_model.CpSolver();solver.parameters.num_workers=1; status=solver.Solve(m)
    return {'data':data,'status':solver.StatusName(status),'options':{i:[sq for _,sq in v] for i,v in choices.items()}}

if __name__=='__main__':
    rows=[build('grid_v17a',[(17,16),(19,25)]),build('grid_ac',[(16,17),(19,25)]),
          build('grid_ac_only',[(16,17)]),build('grid_ac_aa',[(16,17),(19,25),(14,8),(9,15),(1,2)])]
    (HERE/'grid_manifest.json').write_text(json.dumps(rows,indent=2)+'\n')
    out={'full_transversal_fixed_prefix':square_fit([0,20,7,4,3,15,8]),'full_transversal_v17a_layout':square_fit(L['d']),
         'v17a_A_C_edges':[(u,v) for u in L['a'] for v in L['c'] if near(u,v)],'layout':L}
    (HERE/'grid_fit.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out))
