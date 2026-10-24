"""Exact cyclotomic certificate: a harmful physical D2 Pauli need not cost p/30.

The full v31s+A circuit with all DETECTOR declarations removed still prepares
the ideal target and always accepts. It is deliberately uncompetitive. One
physical fault has decoded loss exactly1/4, so its first-order contribution is
p/60. Arithmetic below is exact in Q[w]/(w^4+1), w=exp(i*pi/4).
"""
from pathlib import Path
from fractions import Fraction as F
import sys,json,hashlib
HERE=Path(__file__).resolve().parent;ROOT=HERE
sys.path.insert(0,str(HERE.parent/'sparse'))
import frontend as fa
ZERO=(F(0),)*4;ONE=(F(1),F(0),F(0),F(0));W=(F(0),F(1),F(0),F(0))
WI=(F(0),F(0),F(0),F(-1));ISQ2=(F(0),F(1,2),F(0),F(-1,2))
def add(a,b):return tuple(x+y for x,y in zip(a,b))
def scale(a,v):return tuple(x*v for x in a)
def mul(a,b):
    out=[F(0)]*4
    for i,x in enumerate(a):
        for j,y in enumerate(b):
            k=i+j;out[k%4]+=x*y*(-1 if k>=4 else 1)
    return tuple(out)
def conj(a):return (a[0],-a[3],-a[2],-a[1])
def coeff(z):
    vals={1:ONE,-1:scale(ONE,-1),1j:(F(0),F(0),F(1),F(0)),-1j:(F(0),F(0),F(-1),F(0))}
    return vals[z]
def expectation(phi,pm):
    x,z,c=pm;out=ZERO
    for b,a in enumerate(phi):
        term=mul(mul(conj(phi[b^x]),coeff(c)),a)
        out=add(out,scale(term,(-1)**((b&z).bit_count())))
    return out
src=HERE/'v31s_a_decode'
original=src.with_suffix('.qasm').read_text()
text='\n'.join(l for l in original.splitlines() if not l.startswith('// DETECTOR'))+'\n'
stem=HERE/'v31s_a_decode_no_detectors'
stem.with_suffix('.qasm').write_text(text)
md=json.loads(src.with_suffix('.json').read_text());fa.DATA=md['data_qubits']
stem.with_suffix('.json').write_text(json.dumps(dict(data_qubits=fa.DATA,scope=__doc__),indent=2)+'\n')
ops,ds=fa.parse_current(text);m=fa.make_model(ops,ds);e=fa.Engine(m)
fault=next(x for x in m.faults if x['ins']==23 and x['pauli']=='XI' and x['qs']==[13,7])
def loss(s,signature,engine=None,d=0):
    e=engine or globals()['e']
    phi=[ZERO]*e.N;phi[0]=ONE
    for j,(x,z,c,theta) in enumerate(e.rot):
        theta=(-theta if s>>j&1 else theta)
        w=W if theta<0 else WI
        a=scale(add(ONE,w),F(1,2));b=scale(add(ONE,scale(w,-1)),F(1,2))
        b=mul(b,coeff(c));out=[ZERO]*e.N
        for index,v in enumerate(phi):
            out[index]=add(out[index],mul(a,v))
            out[index^x]=add(out[index^x],scale(mul(b,v),(-1)**((index&z).bit_count())))
        phi=out
    for k,(x,z,c) in enumerate(e.projs):
        sign=(-1)**(int(e.v[k])^((d>>k)&1))
        out=[scale(v,F(1,2)) for v in phi]
        for index,v in enumerate(phi):
            term=scale(mul(coeff(c),v),F(sign*(-1)**((index&z).bit_count()),2))
            out[index^x]=add(out[index^x],term)
        phi=out
    norm=expectation(phi,(0,0,1))
    obs=ZERO
    for key,weight in zip(e.keys,e.W):
        T,a,b=key;mask=a|(b<<3)|(1<<6)|((1<<8) if T=='X' else (1<<7)|(1<<9))
        sign=(-1)**((mask&signature).bit_count())*(1 if T=='X' else -1)
        obs=add(obs,scale(mul(ISQ2,expectation(phi,e.Qs[key])),F(float(weight)).limit_denominator()*sign))
    return norm,scale(add(norm,scale(obs,-1)),F(1,2))
idealA,ideal=loss(0,0);faultA,fault_loss=loss(fault['s'],fault['e'])
assert idealA==faultA==ONE and ideal==ZERO and fault_loss==(F(1,4),F(0),F(0),F(0))
out=dict(scope=__doc__,qasm_sha256=hashlib.sha256(text.encode()).hexdigest(),
         fault=fault,basis_dimension=e.N,ideal_decoded_loss='0',fault_acceptance='1',
         conditional_decoded_loss='1/4',first_order_location_probability='p/15',
         first_order_contribution='p/60',value_at_p_1e_3=str(F(1,60000)),
         arithmetic='exact Fraction coefficients in Q[w]/(w^4+1)',
         implication='Refutes only the universal p/30 per harmful Pauli assertion; no performance gain or small total c1 is claimed.')
_,original_dets=fa.parse_current(original)
retained=[ds for k,ds in enumerate(original_dets)if k not in [2,15]]
m2=fa.make_model(ops,retained);e2=fa.Engine(m2)
fault2=next(x for x in m2.faults if x['ins']==108 and x['pauli']=='XI'and x['qs']==[7,6])
a2,n2=loss(fault2['s'],fault2['e'],engine=e2,d=fault2['d'])
assert a2==(F(1,4),F(0),F(0),F(0)) and n2==(F(1,8),F(0),F(0),F(0))
assert loss(0,0,engine=e2)==(ONE,ZERO)
text2=text+'\n'.join('// DETECTOR '+' '.join(f'c[{b}]'for b in sorted(row))for row in retained)+'\n'
stem2=HERE/'v31s_a_decode_drop2_15'
stem2.with_suffix('.qasm').write_text(text2)
stem2.with_suffix('.json').write_text(json.dumps(dict(data_qubits=fa.DATA,scope=__doc__,dropped_detectors=[2,15]),indent=2)+'\n')
out['two_detector_release_witness']=dict(dropped_detectors=[2,15],fault=fault2,
    qasm_sha256=hashlib.sha256(text2.encode()).hexdigest(),ideal_acceptance='1',ideal_loss='0',
    fault_acceptance='1/4',accepted_fault_loss='1/2',unnormalized_loss='1/8',
    first_order_contribution='p/120',value_at_p_1e_3='1/120000',
    total_first_order_loss_at_p_1e_3=.0003,
    implication='Branch acceptance alone invalidates a fixed p/30 quantum, even when conditional accepted loss is1/2. Not competitive as a full circuit.')
(HERE/'c1_exact_witness.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
