"""Release-aware A enumeration; old boundary weights are a documented ranking proxy only."""
import itertools,json,math,re,sys
from pathlib import Path
from r44 import base,AA,LAY,HERE

def syn(v):return sum(((v&m).bit_count()%2)<<i for i,m in enumerate([85,102,120]))
def cls(x,z):return syn(x)|(syn(z)<<3)|(((z&7).bit_count()%2)<<6)
def rep(c):
    x=1<<((c&7)-1) if c&7 else 0
    sz=c>>3&7;z=1<<(sz-1) if sz else 0
    if (z&7).bit_count()%2!=c>>6:z^=7
    return x,z

label=sys.argv[1] if len(sys.argv)>1 else 'r44'
if label.startswith('r44'):
    c,release,_=base('early' in label)
    if label!='r44':LAY=json.loads((HERE/'layouts'/f'{label}.json').read_text())
else:
    from rebuild import prefix
    c,LAY,release=prefix(label);AA=LAY['A']
ue=[(i,j) for i in range(7) for j in range(i+1,7) if abs(AA[i]//6-AA[j]//6)+abs(AA[i]%6-AA[j]%6)==1]
src=(HERE.parent/'AENC/asearch.cpp').read_text()
src=re.sub(r'static const int UE\[7\]\[2\] = .*?;',f'static const int NE={len(ue)}; static const int UE[NE][2] = '+'{'+','.join('{%d,%d}'%e for e in ue)+'};',src)
src=src.replace('(1<<7);m++','(1<<NE);m++').replace('e<7;e++','e<NE;e++')
(HERE/'enc'/f'{label}.cpp').write_text(src)
autos=[[((a if i&1 else 0)^(b if i&2 else 0)^(c if i&4 else 0))-1 for i in range(1,8)] for a,b,c in itertools.product(range(1,8),repeat=3) if len({a,b,c,a^b,a^c,b^c,a^b^c})==7]
perm=next(p for p in autos if {p[i] for i in LAY['flag'][0]['tri']}=={2,3,6})
tab=json.loads((HERE.parent/'AENC/table_v36c.json').read_text())['table']
aa=[tab[str(i)]['A'] for i in range(128)];nn=[(tab[str(i)]['A']-tab[str(i)]['O'])/2 for i in range(128)]
loss0=nn[0]/aa[0];kap=[(nn[i]-loss0*aa[i])/aa[0] for i in range(128)];alp=[a/aa[0]-1 for a in aa]
mapping=[]
for k in range(128):
    x,z=rep(k)
    xp=sum(((x>>i)&1)<<perm[i] for i in range(7));zp=sum(((z>>i)&1)<<perm[i] for i in range(7))
    mapping.append(cls(xp,zp))
tmin=min(max(release[AA[i]][0],release[AA[j]][0])+1 for i,j in ue)
rows=[' '.join(str(kap[mapping[i]]) for i in range(128)),' '.join(str(alp[mapping[i]]) for i in range(128)), f'14 12 -1 {tmin} {LAY["R"]-1}']
for i,q in enumerate(AA):
    rel,basis=release[q];rows.append(f'{rel} {LAY["R"]-1 if i in LAY["flagdata"] else LAY["R"]} {rel if basis=="Z" else -1} {int(basis=="X")}')
(HERE/'enc'/f'{label}.in').write_text('\n'.join(rows)+'\n')
(HERE/'enc'/f'{label}_proxy.json').write_text(json.dumps(dict(edges=ue,permutation=perm,source='AENC/table_v36c.json',scope='proxy ranking only; every built circuit receives a full all-orders price'),indent=2))
