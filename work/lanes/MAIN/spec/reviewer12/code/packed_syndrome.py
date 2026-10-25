"""Read the judge's final syndrome bits without unpacking every measurement."""
import numpy as np

def decoded_syndrome_fixes(meas, keep, n_meas, n_syn=6):
    """Return z_fix,x_fix, matching the judge's little-endian unpackbits code.

    meas: [shots,ceil(n_meas/8)] uint8 packed measurement records.
    keep: Boolean row mask after detector/postselection decisions.
    The final n_syn records are X-type stabilizers, then Z-type stabilizers.
    This changes only postprocessing: sampler seeds and floating sums stay
    in their existing order in race.py / fast_check.py.
    """
    if n_syn % 2 or n_meas < n_syn:
        raise ValueError('Expected two equal syndrome groups at the record tail.')
    start=n_meas-n_syn
    mid=start+n_syn//2
    def masks(lo,hi):
        ans={}
        for bit in range(lo,hi):
            ans[bit>>3]=ans.get(bit>>3,0)|(1<<(bit&7))
        return ans
    zm,xm=masks(start,mid),masks(mid,n_meas)
    relevant={byte:meas[:,byte][keep] for byte in zm.keys()|xm.keys()}
    z_fix=np.zeros(int(np.count_nonzero(keep)),dtype=bool)
    x_fix=z_fix.copy()
    for byte,mask in zm.items():
        z_fix|=(relevant[byte]&mask)!=0
    for byte,mask in xm.items():
        x_fix|=(relevant[byte]&mask)!=0
    return z_fix,x_fix
