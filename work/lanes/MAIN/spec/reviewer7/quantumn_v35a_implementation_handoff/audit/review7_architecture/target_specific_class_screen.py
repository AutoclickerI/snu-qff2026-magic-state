"""Necessary commuting-axis screen for a logical-W target check.

Not a grid gadget, exact hardware class verdict, or performance result.
"""
from pathlib import Path
import json,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'audit/reaudit_evaluation/portable'))
import frontend as f
p=HERE/'v32p_a_decode'
f.DATA=json.loads(p.with_suffix('.json').read_text())['data_qubits']
ops,ds=f.parse_current(p.with_suffix('.qasm').read_text());m=f.make_model(ops,ds)
# Physical Y^7 has the opposite sign to logical Y. i X^7 Y^7 = Z^7.
Z=f.mul(m.Q['X',0,0],m.Q['Y',0,0]);Z=(Z[0],Z[1],1j*Z[2])
rows=[dict(index=i,native_instruction=ii,time=m.labels[ii].time,kind=m.labels[ii].kind,
           qubit=m.labels[ii].qs[0],anticommutes=bool(f.comm(Z,(x,z))))
      for i,(x,z,co,theta,ii)in enumerate(m.rots)]
r=dict(scope=__doc__,source='v32p_a_decode',pulled_ZL=[str(Z[0]),str(Z[1]),str(Z[2])],
       rotation_count=len(m.rots),anticommuting_rotations=[row for row in rows if row['anticommutes']],rows=rows)
representatives=[]
supports=[{0,2,4,6},{1,2,5,6},{3,4,5,6}]
for mask in range(8):
    z=Z; support=set(range(7))
    for j,g in enumerate(m.gen_m[3:6]):
        if mask>>j&1:
            z=f.mul(z,g); support.symmetric_difference_update(supports[j])
    representatives.append(dict(stabilizer_mask=mask,code_support=sorted(support),
        physical_support=[f.DATA[i] for i in sorted(support)],
        anticommuting_rotation_indices=[j for j,r in enumerate(m.rots)if f.comm(z,r)]))
r['logical_Z_representatives']=representatives
Path(__file__).with_suffix('.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r,indent=2))
