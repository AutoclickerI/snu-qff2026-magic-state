"""Independent dense-matrix verification of the proposed terminal bound.

Build the physical seven-qubit decoder fidelity observable from CSS codewords,
apply Pauli channels by matrix conjugation, and diagonalize 128x128 matrices.
Does not import the certificate generator or use its convolution/moment code.
"""
import os
os.environ.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
import json,time
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
cert=json.loads((HERE/'penultimate_bound_certificate.json').read_text())
t0=time.perf_counter()
ix=np.arange(128)
par=np.array([int(i).bit_count()%2 for i in ix])

# Steane CSS basis from the [7,3,4] simplex code.
words={0}
for check in [0b1010101,0b1100110,0b1111000]:
 words|={w^check for w in tuple(words)}
assert len(words)==8
zero=np.zeros(128,dtype=complex);zero[list(words)]=1/np.sqrt(8)
one=zero[ix^127]
target=(zero+np.exp(1j*np.pi/4)*one)/np.sqrt(2)

def apply_pauli_state(v,x,z):
 # A global Pauli phase is irrelevant to every projector below.
 signs=np.array([1 if (int(i)&z).bit_count()%2==0 else -1 for i in ix])
 return (signs*v)[ix^x]

basis=[];projector=np.zeros((128,128),dtype=complex)
for sx in range(8):
 for sz in range(8):
  x=0 if sx==0 else 1<<(sx-1)
  z=0 if sz==0 else 1<<(sz-1)
  v=apply_pauli_state(target,x,z)
  projector+=np.outer(v,v.conj())
  basis.extend([apply_pauli_state(zero,x,z),apply_pauli_state(one,x,z)])
basis=np.stack(basis,axis=1)
assert np.max(np.abs(basis.conj().T@basis-np.eye(128)))<1e-14
assert np.max(np.abs(projector@projector-projector))<1e-14

perms=[ix^(1<<q) for q in range(7)]
signs=[np.outer(1-2*((ix>>q)&1),1-2*((ix>>q)&1)) for q in range(7)]

def local_noise(mat,q,weights):
 pi,px,py,pz=weights
 xx=mat[np.ix_(perms[q],perms[q])]
 return pi*mat+px*xx+py*signs[q]*xx+pz*signs[q]*mat

def pauli_conjugate(mat,x,z):
 pp=ix^x
 ss=np.array([1 if (int(i)&z).bit_count()%2==0 else -1 for i in ix])
 return np.outer(ss,ss)*mat[np.ix_(pp,pp)]

# Independent channel construction from Pauli-transfer eigenvalues.
p=1/1000;q=2*p/5;r=4*p/15
local_base=(1-16*p/15)*(1-4*q/3)
lambda_types={
 'L':np.array([(1-4*p/3)*(1-4*q/3)]*3),
 'P':np.array([(1-16*p/15)**2]*3),
 'X':np.array([local_base,local_base*(1-2*r),local_base*(1-2*r)]),
 'Z':np.array([local_base*(1-2*r),local_base*(1-2*r),local_base]),
}
weights={}
for name,(lx,ly,lz) in lambda_types.items():
 weights[name]=np.array([1+lx+ly+lz,1+lx-ly-lz,1-lx+ly-lz,1-lx-ly+lz])/4
 expected=np.array(cert['channels_probability_numerators_I_X_Y_Z'][name])/cert['channels_probability_denominator']
 assert np.max(np.abs(weights[name]-expected))<1e-15

def expected_spectrum(case,den):
 vals=[]
 for _,_,vx,vy in case['sectors_x_z_vx_vy']:
  radius=np.hypot(vx/den,vy/den)/np.sqrt(2)
  vals.extend([(1-radius)/2,(1+radius)/2])
 return np.sort(vals)

max_spectral_error=0.;best=(float('inf'),None);rows=[]
for case in cert['cases']:
 rep=case['representative'];mat=projector.copy()
 for qi,name in enumerate(rep):mat=local_noise(mat,qi,weights[name])
 eig=np.linalg.eigvalsh(mat)
 expected=expected_spectrum(case,cert['moment_denominator'])
 err=float(np.max(np.abs(eig-expected)));max_spectral_error=max(max_spectral_error,err)
 loss=float(1-eig[-1])
 if loss<best[0]:best=(loss,rep)
 rows.append(dict(representative=rep,minimum_loss=loss,max_spectral_error=err))

# Excluded channels are rebuilt directly from the physical two-wire Pauli map.
paulis=[(0,0),(1,0),(1,1),(0,1)]
def mapped(a,b,kind):
 xa,za=paulis[a];xb,zb=paulis[b]
 if kind=='output_output':return xa|(xb<<1),za|(zb<<1)
 if kind=='output_other_helper_X':return xa|(xb<<1),za
 if kind=='output_other_helper_Z':return xa,za|(zb<<1)
 if kind=='helper_helper_XX':return xa|(xb<<1),0
 if kind=='helper_helper_ZZ':return 0,za|(zb<<1)
 if kind=='helper_helper_XZ':return xa,zb<<1
 raise ValueError(kind)

excluded=[]
for case in cert['excluded_channel_certificates']+[cert['opposite_axis_channel_certificate']]:
 mat=np.zeros_like(projector)
 for a in range(4):
  for b in range(4):
   x,z=mapped(a,b,case['name'])
   mass=1-p if a==b==0 else p/15
   mat+=mass*pauli_conjugate(projector,x,z)
 eig=np.linalg.eigvalsh(mat)
 err=float(np.max(np.abs(eig-expected_spectrum(case,case['denominator']))))
 max_spectral_error=max(max_spectral_error,err)
 excluded.append(dict(name=case['name'],minimum_loss=float(1-eig[-1]),max_spectral_error=err))

result=dict(method=__doc__,orbit_representatives=len(rows),spectra_checked=len(rows)+len(excluded),eigenvalues_checked=128*(len(rows)+len(excluded)),max_absolute_spectral_disagreement=max_spectral_error,best_assignment=best[1],dense_minimum_loss=best[0],certificate_minimum_loss=cert['minimum_loss'],minimum_loss_disagreement=abs(best[0]-float(cert['minimum_loss'])),excluded=excluded,seconds=time.perf_counter()-t0,precision='IEEE754 complex128; independent numerical arithmetic, not a second exact rational certificate',physical_universality='Requires the separately reviewed schedule and instrument reduction')
assert max_spectral_error<3e-14
assert best[1]=='XXXXXXX'
(HERE/'penultimate_bound_dense_verification.json').write_text(json.dumps(result,indent=2)+'\n')
(HERE/'penultimate_bound_dense_cases.json').write_text(json.dumps(rows,indent=2)+'\n')
print(json.dumps(result,indent=2))
