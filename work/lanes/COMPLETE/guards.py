"""All deterministic identity-CX data guard slots in each rebuilt suffix.
Uses conservative T-aware stabilizers, not the T->I surrogate. Every saved
single is priced; improving singles are jointly repriced by finish_guards.
"""
import os,sys,json,hashlib,collections,copy
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
sys.dont_write_bytecode=True
from build import H,lib
from lifetime import nodes,Circ
import stabilizer as S
sys.path.insert(0,str(H.parent/'BUNDLE'))
import menu
def run(name):
    c=lib.read(H/'builds'/name);ns=nodes(Circ((H/'builds'/name).with_suffix('.qasm').read_text()))
    st=menu.status(c);occ=lib.busy(c);by=collections.defaultdict(list)
    for x in ns:by[x['t']].append(x)
    stab=[(0,1<<q,0) for q in range(36)];edits=[]
    for t in range(lib.depth(c)):
        if 23<=t<lib.depth(c)-1:
            for q in lib.D:
                if q in occ[t] or st[q][t]!='live':continue
                for h in range(36):
                    if h in occ[t] or st[h][t] in ('dead','pre') or abs(h//6-q//6)+abs(h%6-q%6)!=1:continue
                    for edge,p in [((h,q),(0,1<<h,0)),((q,h),(1<<h,0,0))]:
                        if S.member(stab,p):edits.append(dict(t=t,a=edge[0],b=edge[1]))
        for x in by[t]:stab=S.evolve(stab,x)
    names=[]
    for i,e in enumerate(edits):
        cc=lib.add_ops(c,[(e['t'],[f'cx q[{e["a"]}],q[{e["b"]}];'])]);cc['meta']=dict(data_qubits=lib.D,source=name+'; deterministic data guard',guard=e,guard_base=name)
        stem=lib.save(cc,f'{name}_g{i:03}');names.append(stem.name)
    print(name,len(names),flush=True);return names
if __name__=='__main__':
    out={n:run(n) for n in sys.argv[1:]};(H/'guards.json').write_text(json.dumps(out,indent=2))
