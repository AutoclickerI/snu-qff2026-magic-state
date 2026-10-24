"""Basis-independent direct-sum test for detector-noise factorization.

Build the binary vector matroid on every channel's detector signatures, then
join every vector belonging to the same physical channel. Add the active
ideal-detector axes to the core and merge all channels affecting a rotation
or a scored-observable sign into that core. Remaining components are direct
summands of detector space, so their all-zero event is independent of the
accepted quantum output. This is stronger than graph disconnection in one
arbitrary detector basis, but is still a sufficient, not necessary, test.
"""
from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'quantumn_review10/work/lanes/MAIN/sparse'))
import sparse_walsh as sw
HERE=Path(__file__).parent
stem=ROOT/'quantumn_review10/work/lanes/MAIN/v36c'
m,eng,groups,nd,ks,psi,where,elim=sw.prepare(stem,True)
ids=list(groups); labels={c:i for i,c in enumerate(ids)}; core=len(ids)
parent=list(range(core+1))
def find(i):
    while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
    return i
def join(a,b):
    a,b=find(a),find(b)
    if a!=b:parent[b]=a
def bitids(v):
    while v:
        b=v&-v;yield b.bit_length()-1;v^=b
emasks=[sw.emask_for(k) for k in eng.keys]
def relevant_e(e):return any((e&mask).bit_count()&1 for mask in emasks)
basis={}; originals=[]; owners=[]; circuits=[]
def add(v,owner):
    original=v;expr=0
    while v:
        p=v.bit_length()-1
        if p not in basis:
            j=len(originals);originals.append(original);owners.append(owner)
            basis[p]=(v,expr^(1<<j));return
        bv,bexpr=basis[p];v^=bv;expr^=bexpr
    for j in bitids(expr):join(owner,owners[j])
    if expr:circuits.append((owner,[owners[j] for j in bitids(expr)]))
for i,p in enumerate(eng.projs):
    if p[:2]!=(0,0):add(1<<i,core)
zero=[]
for c,fs in groups.items():
    owner=labels[c]
    if any(f['s'] or relevant_e(f['e']) for f in fs):join(owner,core)
    ds=set(f['d'] for f in fs)
    for d in sorted(ds):add(d,owner)
    if ds=={0} and find(owner)!=find(core):zero.append(c)
components={}
for c in ids:
    components.setdefault(find(labels[c]),[]).append(c)
out={'source_commit':'42afa8ff01c3999444336f5bb2fe473c1475d6f4',
     'detector_bits':nd,'rank_with_active_axes':len(basis),'channels':len(ids),
     'core_channels':components.get(find(core),[]),
     'auxiliary_channel_components':[cs for k,cs in components.items() if k!=find(core) and not set(cs).issubset(zero)],
     'completely_unobservable_channels':zero,
     'original_basis_vectors':originals,'basis_owners':owners,
     'note':'All atoms in a channel are joined, active ideal-detector axes core-tagged; this certifies direct-sum independence, not mere small finite differences.'}
(HERE/'matroid_census.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k not in ('original_basis_vectors','basis_owners','core_channels')},indent=2))
print('core_channels',len(out['core_channels']))
