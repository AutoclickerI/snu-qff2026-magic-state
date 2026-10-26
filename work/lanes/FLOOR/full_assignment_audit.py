"""Independent exhaustive 4^7 channel assignments; no symmetry or reviewer imports."""
import itertools, json, time
from pathlib import Path
import numpy as np
from independent_spectrum import signature, spectrum, distribution

OUT=Path(__file__).resolve().parent
def main():
    start=time.perf_counter();p=.001;q=2*p/5;r=4*p/15
    # Independent Pauli transfer construction; invert the 4-point transform.
    h=np.array([[1,1,1,1],[1,1,-1,-1],[1,-1,1,-1],[1,-1,-1,1]])
    a=1-4*q/3; b=1-16*p/15; c=1-2*r
    transfer=np.array([[1,(1-4*p/3)*a,(1-4*p/3)*a,(1-4*p/3)*a],
                       [1,b*a,b*a*c,b*a*c], [1,b*b,b*b,b*b], [1,b*a*c,b*a*c,b*a]])
    weights=transfer@h/4
    assert np.min(weights)>=0
    v=np.zeros((1,256));v[0,0]=1
    ix=np.arange(256)
    for qi in range(7):
        shifted=np.stack([v[:,ix^signature(qi,pa)] for pa in 'IXYZ'],axis=1)
        v=np.einsum('ap,bpe->bae',weights,shifted).reshape(-1,256)
    labels=[''.join(x) for x in itertools.product('LXPZ',repeat=7)]
    sx,sz=ix&7,(ix>>3)&7;px,pz=(ix>>6)&1,(ix>>7)&1
    kx=[];ky=[]
    for syn in range(64):
        xx,zz=syn&7,syn>>3
        kx.append(1-2*(pz^((sz^zz)!=0)).astype(int))
        ky.append(1-2*(px^pz^((sx^xx)!=0)^((sz^zz)!=0)).astype(int))
    vx=v@np.array(kx).T;vy=v@np.array(ky).T
    loss=(1-np.sqrt((vx*vx+vy*vy)/2))/2
    best_idx,syn=np.unravel_index(np.argmin(loss),loss.shape)
    # Every orbit representative's full spectrum compared, after converting sector indexing.
    cert=json.loads((OUT/'reviewer18_copy/penultimate_bound_certificate.json').read_text())
    lookup={l:i for i,l in enumerate(labels)};max_error=0
    den=cert['moment_denominator']
    for case in cert['cases']:
        i=lookup[case['representative']]
        for x,z,ex,ey in case['sectors_x_z_vx_vy']:
            j=x+8*z
            expected=(1-np.hypot(ex/den,ey/den)/np.sqrt(2))/2
            max_error=max(max_error,abs(loss[i,j]-expected))
    # Rebuild excluded channels by physical Pauli projection, for all output label pairs.
    excluded={}
    for name in ('DD','DH_X','DH_Z','HH_XX','HH_ZZ','HH_XZ'):
        vals=[]
        for a,b in itertools.combinations(range(7),2):
            ch=[]
            for pa,pb in itertools.product('IXYZ',repeat=2):
                aa=pa if name.startswith('D') else ('X' if name[3]=='X' and pa in 'XY' else 'Z' if name[3]=='Z' and pa in 'ZY' else 'I')
                bb=pb if name=='DD' else ('X' if name[-1]=='X' and pb in 'XY' else 'Z' if name[-1]=='Z' and pb in 'ZY' else 'I')
                ch.append((signature(a,aa)^signature(b,bb),1-p if pa==pb=='I' else p/15))
            vals.append(spectrum(distribution([ch]))['minimum_loss'])
        excluded[name]=dict(min=min(vals),max=max(vals),pairs=len(vals))
    out=dict(assignments=len(labels),sectors=64,total_inequalities=loss.size,
             best_assignment=labels[best_idx],best_syndrome=int(syn),minimum_loss=float(loss[best_idx,syn]),
             exact_certificate_minimum=cert['minimum_loss'],max_orbit_sector_disagreement=float(max_error),
             second_assignment_loss=float(np.partition(loss[:,0],1)[1]),
             excluded=excluded,seconds=time.perf_counter()-start,
             limitation='IEEE754 computation; exact proof supplied by isolated rational certificate',
             no_symmetry_reduction=True)
    assert labels[best_idx]=='XXXXXXX' and syn==0 and max_error<2e-14
    (OUT/'experiments/full_assignment_audit.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2),flush=True)
if __name__=='__main__':main()
