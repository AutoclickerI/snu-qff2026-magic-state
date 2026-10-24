"""Exact finite-p storage-channel screen for a Fano-line repetition gadget.

Seven-qubit Steane T storage; three data positions on a Fano line each acquire
an X-repetition helper during a W-tick wait. Encoding and decoding consume two
of those ticks. Helpers have native RX preparation and final MX flips, both p.
The helper MX happens alongside the next operation on data. Output stabilizer
checks are IDEAL AND POSTSELECTED in this toy. This is not the contest circuit.
All two-qubit depolarizing Pauli patterns and all 4^7 data patterns are included.
"""
import json,itertools,math
from pathlib import Path
import numpy as np

P=.001
# Pair bits are x_data,z_data,x_helper,z_helper.
def conv(a,b):
    out=np.zeros(16)
    for i,x in enumerate(a):
        for j,y in enumerate(b):out[i^j]+=x*y
    return out
def cx_h_d(a):
    out=np.zeros(16)
    for k,v in enumerate(a):
        xd,zd,xh,zh=[(k>>i)&1 for i in range(4)]
        kk=(xd^xh)|(zd<<1)|(xh<<2)|((zh^zd)<<3)
        out[kk]+=v
    return out
def d1(q,helper=False):
    out=np.zeros(16);out[0]=1-q
    for k in (1,2,3):out[k<<(2 if helper else 0)]=q/3
    return out
def repeated(p,n):return .75*(1-(1-4*p/3)**n)
def protected_channel(wait,p=P):
    assert wait>=2
    zerr=np.zeros(16);zerr[0]=1-p;zerr[8]=p
    dep2=np.full(16,p/15);dep2[0]=1-p
    a=zerr.copy()                       # RX preparation flip
    a=cx_h_d(a);a=conv(a,dep2)          # encode
    a=conv(a,d1(repeated(p,wait-2)))
    a=conv(a,d1(repeated(p,wait-2),True))
    a=cx_h_d(a);a=conv(a,dep2)          # decode
    a=conv(a,zerr)                     # MX result flip before ideal MX
    out=np.zeros(4)
    for k,v in enumerate(a):
        if not k&8:out[k&3]+=v         # accept +X helper result
    acceptance=out.sum()
    return out/acceptance,acceptance

patterns=np.array(list(itertools.product(range(4),repeat=7)),dtype=np.int64)
sx=np.zeros(len(patterns),dtype=np.int64);sz=sx.copy();px=sx.copy();pz=sx.copy()
for i in range(7):
    x=patterns[:,i]&1;z=(patterns[:,i]>>1)&1
    sx^=x*(i+1);sz^=z*(i+1);px^=x;pz^=z
keep=(sx==0)&(sz==0)
loss=np.where(px,.5,np.where(pz,1.,0.))
def ideal_postselected_readout(channels):
    prob=np.ones(len(patterns))
    for i,ch in enumerate(channels):prob*=ch[patterns[:,i]]
    A=prob[keep].sum()
    return float((prob[keep]*loss[keep]).sum()/A),float(A)

lines=[x for x in itertools.combinations(range(7),3) if (x[0]+1)^(x[1]+1)^(x[2]+1)==0]
protected=lines[0]
assert len(lines)==7 and sorted(len(set(x)&set(protected))for x in lines)==[1]*6+[3]
rows=[]
for wait in [2,3,4,6,8,10,12,16,20,24,32]:
    q=repeated(P,wait);bare=np.array([1-q,q/3,q/3,q/3])
    protected_ch,Ahelper=protected_channel(wait)
    L0,A0=ideal_postselected_readout([bare]*7)
    L1,A1=ideal_postselected_readout([protected_ch if i in protected else bare for i in range(7)])
    rows.append(dict(wait_ticks=wait,bare_loss=L0,protected_loss=L1,
                     relative_loss_change=L1/L0-1,bare_acceptance=A0,
                     protected_acceptance=A1*Ahelper**3,
                     protected_channel=dict(zip(['I','X','Z','Y'],map(float,protected_ch))),
                     helper_flag_acceptance=Ahelper))
out=dict(scope=__doc__,p=P,protected_data_indices=list(protected),fano_lines=[list(x)for x in lines],
         perfect_wrapper_leading_coefficients={'bare':14,'protected':10},results=rows)
Path(__file__).with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
