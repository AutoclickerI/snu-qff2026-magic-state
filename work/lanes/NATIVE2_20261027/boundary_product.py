"""Official exact-state evidence for every released source cell."""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import argparse,json,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'work/tools'))
from qtools.evaluator.frontend import parse_current
from tprep.qasm import to_stim
from tprep.exact import run

def certify(boundary_path=None,output_path=None):
    st=time.perf_counter();boundary=json.loads(Path(boundary_path or HERE/'prefix_release.json').read_text());stem=Path(boundary['stem'])
    if not stem.is_absolute():stem=ROOT/stem
    text=stem.with_suffix('.qasm').read_text();native,errors=to_stim(text);assert not errors
    state,inverse,records,detectors,wires=run(native,36)
    ops,dets=parse_current(text);measured=[o for o in ops if o.bit is not None]
    record_wire={o.bit:records[i] for i,o in enumerate(measured)}
    out=[]
    def expect(q,axis,bits=()):
        p=state.stim.PauliString(state.n);p[wires[q]]=axis
        for b in bits:p[record_wire[b]]='Z'
        return float(state.expectation(p,inverse))
    for qstr,release in boundary['release'].items():
        q=int(qstr);history=[o for o in ops if q in o.qs]
        values={axis:expect(q,axis) for axis in 'XYZ'}
        known=[axis for axis,v in values.items() if abs(abs(v)-1)<1e-9]
        row=dict(q=q,release=release,expectations=values,fresh=not history)
        if known:
            axis=known[0];row.update(product_axis=axis,phase_xor=[],phase_constant=int(values[axis]<0))
        else:
            last_measure=next((o for o in reversed(history) if o.bit is not None),None)
            if last_measure:
                axis='X' if last_measure.kind=='MX' else 'Z';value=expect(q,axis,[last_measure.bit])
                row['last_measurement_correlation']=dict(axis=axis,bit=last_measure.bit,expectation=value)
                if abs(abs(value)-1)<1e-9:row.update(product_axis=axis,phase_xor=[last_measure.bit],phase_constant=int(value<0))
        if history:
            o=history[-1];row['last_operation']=dict(time=o.time,kind=o.kind,qs=list(o.qs),bit=o.bit)
        out.append(row)
    result=dict(prefix_stem=str(stem),oracle='Official tprep.exact.run / state.expectation',
        all_cells_have_certified_product_axis=all('product_axis' in r for r in out),cells=out,
        noise_scope='Ideal product-state evidence only. Reuse retains original post-measurement/idle noise and must be audited in the completed circuit.',
        seconds=time.perf_counter()-st)
    Path(output_path or HERE/'prefix_product_states.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2),flush=True)
    return result

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--boundary');ap.add_argument('--output');a=ap.parse_args();certify(a.boundary,a.output)
