"""Exact-state guard for a proposed late target-specific logical check.

Shows why a raw W_L projector appended after the final syndrome checks is
not safe. One otherwise correctable physical X or Y fault is converted
into accepted decoded loss. This is a 128-amplitude calculation, not a
physical circuit or a performance prediction.
"""
from pathlib import Path
import json,math,numpy as np
N=128
checks=[sum(1<<i for i in s)for s in[{0,2,4,6},{1,2,5,6},{3,4,5,6}]]
code=[]
for v in range(8):
 b=0
 for i,g in enumerate(checks):
  if v>>i&1:b^=g
 code.append(b)
target=np.zeros(N,complex)
for b in code:
 target[b]=.25;target[b^127]=np.exp(1j*math.pi/4)*.25

def pauli(state,x,z,coef=1):
 out=np.zeros_like(state)
 for i,a in enumerate(state):out[i^x]=coef*(-1)**((i&z).bit_count())*a
 return out

def W(state,support):
 # The same odd weight-three Fano line represents X_L and Z_L.
 # Y_L=i X_L Z_L, so use coefficient i for its binary XZ form.
 return (pauli(state,support,0)+pauli(state,support,support,1j))/math.sqrt(2)

rows=[]
for name,support in [('full_weight7',127),('weight3_line',1|32|64)]:
 assert np.linalg.norm(W(target,support)-target)<1e-12
 for P,x,z,coef in [('I',0,0,1),('X0',1,0,1),('Y0',1,1,1j),('Z0',0,1,1)]:
  error=pauli(target,x,z,coef)
  projected=(error+W(error,support))/2
  acceptance=float(np.vdot(projected,projected).real)
  corrected=pauli(projected,x,z,coef)
  target_mass=float(abs(np.vdot(target,corrected))**2)
  loss_mass=acceptance-target_mass
  rows.append(dict(logical_representative=name,physical_error=P,acceptance=acceptance,
                   decoded_conditional_loss=loss_mass/acceptance if acceptance>1e-14 else None,
                   unnormalized_accepted_loss=loss_mass))
  if P in['X0','Y0']:
   assert abs(acceptance-.5)<1e-12 and abs(loss_mass-.25)<1e-12
out=dict(scope=__doc__,results=rows,
         consequence='Use a syndrome-dressed target instrument, or place/flag the target check so the subsequent syndrome checks reject its non-code branches. A raw late W_L projector creates first-order decoded loss.',
         availability_note='No rule forbids a target-specific instrument, but a complete gadget must pass the official commuting-rotation class, exact ideal target, full physical-noise and runtime gates.')
Path(__file__).with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
