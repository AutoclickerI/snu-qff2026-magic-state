"""Exact local C4 isometry, phase gadget and coherent logical-X gate audit."""
import json,math
from pathlib import Path
import numpy as np
H=Path(__file__).resolve().parent

def cx(s,c,t):
 out=np.zeros_like(s)
 for i in range(len(s)):out[i^(((i>>c)&1)<<t)]=s[i]
 return out
def phase(s,q,k):
 out=s.copy()
 for i in range(len(s)):
  if (i>>q)&1:out[i]*=np.exp(k*1j*np.pi/4)
 return out
def had(s,q):
 out=s.copy()
 for i in range(len(s)):
  if not (i>>q)&1:
   j=i|(1<<q);out[i]=(s[i]+s[j])/math.sqrt(2);out[j]=(s[i]-s[j])/math.sqrt(2)
 return out
def pauli(s,x,z):
 out=np.zeros_like(s)
 for i,v in enumerate(s):out[i^x]+=(-1)**((i&z).bit_count())*v
 return out

# H=bit0, D=bit1, L=bit2, K=bit3, cat control=bit4.
def encode(v):
 s=np.zeros(32,complex);s[0],s[2]=v;s=had(s,0)
 for c,t in [(0,1),(1,3),(0,2)]:s=cx(s,c,t)
 return s
zero=encode((1,0));one=encode((0,1));magic=(zero+np.exp(1j*np.pi/4)*one)/math.sqrt(2)
max_stab=max(float(np.max(np.abs(pauli(v,x,z)-v))) for v in (zero,one) for x,z in [(15,0),(0,10),(0,5)])
max_x=max(float(np.max(np.abs(pauli(v,10,0)-target))) for v,target in [(zero,one),(one,zero)])
max_z=max(float(np.max(np.abs(pauli(v,0,3)-sign*v))) for v,sign in [(zero,1),(one,-1)])
def logical_t(v,sgn=1):return cx(phase(cx(v,0,1),1,sgn),0,1)
t_error=max(float(np.max(np.abs(logical_t(v)-target))) for v,target in [(zero,zero),(one,np.exp(1j*np.pi/4)*one)])
cat0=magic;cat1=np.roll(magic,16)
ctrl_error=max(float(np.max(np.abs(cx(cx(v,4,1),4,3)-target))) for v,target in [(cat0,cat0),(cat1,np.roll(pauli(magic,10,0),16))])
bridge_error=0.
for i in range(32):
 basis=np.zeros(32,complex);basis[i]=1
 direct=cx(cx(basis,4,1),4,3)
 bridged=cx(cx(cx(basis,1,3),4,1),1,3)
 bridge_error=max(bridge_error,float(np.max(np.abs(direct-bridged))))
result=dict(tile_order=['H','D','L','K'],stabilizers=['XXXX','Z_D Z_K','Z_H Z_L'],
 logical_x='X_D X_K',logical_z='Z_H Z_D',phase_gate='CX H,D; T D; CX H,D',
 max_stabilizer_error=max_stab,max_logical_x_error=max_x,max_logical_z_error=max_z,
 max_logical_phase_gadget_error=t_error,max_controlled_x_error=ctrl_error,
 max_native_bridge_error=bridge_error,
 qubit_budget=dict(physical_tiles=28,cat_qubits=7,spare_during_cat=1,spare_without_cat=8,
                   simultaneous_cat_and_seven_extra_meters=42,device=36),
 bridge='CX D,K; CX cat,D; CX D,K implements CX cat,D; CX cat,K using two adjacent edges.',
 note='Ideal algebra only; simultaneous placement, physical flagging, faults, cat preparation and full-code schedule not tested.')
assert all(result[x]<1e-12 for x in ('max_stabilizer_error','max_logical_x_error','max_logical_z_error','max_logical_phase_gadget_error','max_controlled_x_error','max_native_bridge_error'))
(H/'c4_identity_audit.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
