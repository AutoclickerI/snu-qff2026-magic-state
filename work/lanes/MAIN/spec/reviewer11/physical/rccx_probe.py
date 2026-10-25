"""Verify a measured-classical-record AND and build one v36g placement.

The 4-T core is a relative-phase Toffoli, NOT a coherent Toffoli replacement.
It is suitable here only for already Z-dephased controls, followed by target
measurement; the input-dependent phases disappear in the classical instrument.
The full candidate has not been assumed to improve physical loss.
"""
from pathlib import Path
from math import sqrt, pi
from cmath import exp
from collections import Counter
import sys
import json
import hashlib

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path.insert(0,str(HERE/'source/work/lanes/T14'))
from qcirc import parse,emit,adjacent

core=[('H',2),('T',2),('CX',(1,2)),('TDG',2),('CX',(0,2)),
      ('T',2),('CX',(1,2)),('TDG',2),('H',2)]

def evolve(index):
    vector=[0j]*8;vector[index]=1
    for gate,arg in core:
        out=[0j]*8
        if gate=='H':
            for i,z in enumerate(vector):
                out[i&~(1<<arg)]+=z/sqrt(2)
                out[i|(1<<arg)]+=z/sqrt(2)*(-1 if i>>arg&1 else 1)
        elif gate=='CX':
            a,b=arg
            for i,z in enumerate(vector):
                out[i^((1<<b) if i>>a&1 else 0)]+=z
        else:
            for i,z in enumerate(vector):
                out[i]=z*(exp((1 if gate=='T'else-1)*1j*pi/4) if i>>arg&1 else 1)
        vector=out
    return vector

truth=[]
for x in range(8):
    vector=evolve(x)
    expected=x^(((x&1)*((x>>1)&1))<<2)
    leaked=sum(abs(z)**2 for i,z in enumerate(vector) if i!=expected)
    assert leaked<1e-28 and abs(abs(vector[expected])-1)<1e-12
    truth.append(dict(input_bits=[x&1,(x>>1)&1,(x>>2)&1],
                      output_bits=[expected&1,(expected>>1)&1,(expected>>2)&1],
                      phase=[round(vector[expected].real,12),round(vector[expected].imag,12)],
                      probability_outside_correct_bits=leaked))

base=ROOT/'quantumn_review11/work/lanes/MAIN/v36g.qasm'
units,dets=parse(base.read_text())
assert dets[3]==[3] and dets[75]==[310]
a,b,target=12,19,18
assert adjacent(a,target) and adjacent(b,target)
record=max(u['b'] for u in units if u['b'] is not None)+1
new=[(9,'RX',(target,)),(10,'T',(target,)),(11,'CX',(b,target)),
     (12,'TDG',(target,)),(13,'CX',(a,target)),(14,'T',(target,)),
     (15,'CX',(b,target)),(16,'TDG',(target,)),(17,'MX',(target,))]
for tick,gate,qs in new:
    assert not any(u['t']==tick and set(qs)&set(u['q']) for u in units),(tick,qs)
    units.append(dict(k=gate,q=qs,t=tick,b=record if gate=='MX' else None))
new_dets=[d for i,d in enumerate(dets) if i not in (3,75)]+[[record]]
output=HERE/'rccx_drop3_75'
text=emit(units,new_dets)
output.with_suffix('.qasm').write_text(text)
base_meta=json.loads(base.with_suffix('.json').read_text())
output.with_suffix('.json').write_text(json.dumps({
    'data_qubits':base_meta['data_qubits'],
    'base':'v36g',
    'modification':'Replace detector c3=0 and c310=0 with measured-classical RCCX AND=0 on q18.',
    'scope':'Gated research candidate; no physical performance gain is claimed.',
},indent=2)+'\n')
certificate={
    'phase_exact':False,'computational_basis_map_exact':True,
    'scope':'Identical output-bit instrument for Z-dephased controls and measured target; not a coherent uncompute identity.',
    'core':core,'core_counts':dict(Counter(g for g,_ in core)),
    'truth_table':truth,
    'placement':{'a':{'qubit':a,'record':310,'measured_tick':11},
                 'b':{'qubit':b,'record':3,'measured_tick':10},
                 'target':target,'target_record':record,
                 'operations':new,'removed_detector_rows':[3,75],
                 'acceptance_predicate':'not(c3 and c310)',
                 'target_next_original_operation':'RX q18 at tick19',
                 'original_depth':47,'intended_depth':47},
    'source_pin':'0ff9423a8e69c13998ab1baf7bf09c8e97558a60',
    'base_qasm_sha256':hashlib.sha256(base.read_bytes()).hexdigest(),
    'candidate_qasm_sha256':hashlib.sha256(text.encode()).hexdigest(),
    'T_count':sum(u['k'] in ('T','TDG') for u in units),
    'CX_count':sum(u['k']=='CX' for u in units),
}
(HERE/'rccx_certificate.json').write_text(json.dumps(certificate,indent=2)+'\n')
print(json.dumps({k:certificate[k] for k in ['phase_exact','computational_basis_map_exact','T_count','CX_count','candidate_qasm_sha256']},indent=2))
