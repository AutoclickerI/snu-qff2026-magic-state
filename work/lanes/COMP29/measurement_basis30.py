"""Joint cat readout/Z-preparation instrument on q4, at the same two steps."""
from build30 import *
def unfold(c):
    c=C.clone(c);i=next(i for i,u in enumerate(c['u']) if 'measure q[4] -> c[8];' in u.lines);j=next(j for j,u in enumerate(c['u']) if u.lines==['reset q[4];'] and c['t'][j]>c['t'][i]);t=c['t'][i]
    assert c['u'][i].name=='MX' and c['t'][j]==t+1
    # |0><0| H = |0><+|, equal to accepted MX followed by ideal R0.
    # Explicit H and Z measurement preserve the actual two-step noise model.
    c['u'][i]=C.Unit(['h q[4];']);c['u'][j]=C.Unit(['measure q[4] -> c[8];'])
    return finish(c)
if __name__=='__main__':
    rows=[]
    for source,name in [('f_timing_mz_5_12','f_unfold4'),('f_frame_group','f_frame_group_unfold4')]:
        try:
            r=save(unfold(C.read(H/source)),name,[source,'joint q4 X-cat readout and Z initialization']);r.update(screen(name));rows.append(r);print(name,r['total'],r['exp_minus_A1'],flush=True)
        except Exception as e:rows.append(dict(stem=name,error=repr(e)));print(name,repr(e),flush=True)
    (H/'v30_measurement_basis.json').write_text(json.dumps(rows,indent=2)+'\n')
