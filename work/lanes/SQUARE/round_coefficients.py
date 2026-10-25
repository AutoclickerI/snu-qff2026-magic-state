"""Exact order-two fault pair sum on saved perfect-resource round witnesses."""
import sys,json,itertools
from pathlib import Path
from collections import defaultdict
H=Path(__file__).resolve().parent
name=sys.argv[1]
sys.path.insert(0,str(H/('sparseframe' if name.endswith('eraser') else 'sparse')))
import sparse_walsh as sw
m,e,groups,*_=sw.prepare(H/'builds'/name,True)
fs=[f for f in m.faults if m.labels[f['ins']].time>=7 and f['p']]
assert all(f['s']==0 for f in fs)
# The ideal projector accepts every round measurement branch. An individual
# nonzero detector flip is rejected; pairs survive exactly when d_i == d_j.
for d in {f['d'] for f in fs}:
    a,_=e.ntable(0,d)
    assert abs(a-(d==0))<1e-12
_,n=e.ntable(0,0)
by=defaultdict(list)
for f in fs:by[f['d']].append(f)
n1=sum(f['p']*n[f['e']] for f in by[0])
n2=sum(a['p']*b['p']*n[a['e']^b['e']] for rows in by.values() for a,b in itertools.combinations(rows,2) if a['chan']!=b['chan'])
result=dict(stem=name,single_fault_loss=n1,second_order_loss=float(n2),second_order_p2=float(n2/1e-6),faults=len(fs),
            method='all pairs of distinct noise channels, exact ideal-kernel numerator; N1=0 so normalization adds zero at order two')
(H/'logs'/f'{name}.coefficients.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
