"""Official exact replay of a native A-only resource integrated with source."""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[key]='1'
import argparse,copy,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'work/tools'));sys.path.insert(0,str(ROOT/'work/lanes/END2_20261027'));sys.path.insert(0,str(HERE))
from qtools import write_stem
from qtools.validity import raw_check
from qtools.evaluator import frontend as f
from joint import emit
from partial_contract import A,D
import prefix_boundary as pb
from tprep.qasm import to_stim
from tprep.exact import run

def verify(source,index=0):
    doc=json.loads(Path(source).read_text());seed=doc['candidates'][index]
    resource_A=seed.get('A',A)
    source_stem=Path(doc['prefix_stem'])
    if not source_stem.is_absolute():source_stem=ROOT/source_stem
    ops,dets=f.parse_current(source_stem.with_suffix('.qasm').read_text());ops=copy.deepcopy(ops);dets=copy.deepcopy(dets)
    bit=max(o.bit or 0 for o in ops)+1;byproducts={};helper_records={}
    for row in seed.get('source_x_byproducts',[]):byproducts.setdefault(row['source_bit'],[]).append(row['target'])
    for row in seed['operations']:
        record=bit if row['kind'] in ('M','MX') else None
        ops.append(f.Op(row['kind'],tuple(row['qs']),row['time'],record))
        if record is not None:
            if row.get('zero_flag'):dets.append({bit})
            if 'a_x_byproduct' in row:byproducts.setdefault(bit,[]).append(row['a_x_byproduct'])
            helper_records[row['qs'][0]]=(bit,row['kind'])
            bit+=1
    seen=set()
    for o in ops:
        for q in o.qs:assert (o.time,q) not in seen,(o.time,q);seen.add((o.time,q))
    ops.sort(key=lambda o:o.time);text=emit(ops,dets);raw=raw_check(text,D)
    native,errors=to_stim(text);assert not errors,errors
    state,inverse,records,detectors,wires=run(native,36)
    measured=[o for o in ops if o.bit is not None];record_wire={o.bit:records[i] for i,o in enumerate(measured)}
    checks=[]
    for axis,masks in [('X',[85,102,120,7]),('Z',[85,102,120])]:
        for mask in masks:
            p=state.stim.PauliString(state.n)
            for i,q in enumerate(resource_A):
                if mask>>i&1:p[wires[q]]=axis
            correction=[]
            if axis=='Z':
                support={q for i,q in enumerate(resource_A) if mask>>i&1}
                for b,targets in byproducts.items():
                    if sum(q in support for q in targets)%2:p[record_wire[b]]='Z';correction.append(b)
            checks.append(dict(axis=axis,mask=mask,phase_records=correction,value=float(state.expectation(p,inverse))))
    helper=[]
    for q in seed['helpers']:
        p=state.stim.PauliString(state.n);b,kind=helper_records[q]
        if kind=='MX':p[wires[q]]='X';p[record_wire[b]]='Z'
        else:p[wires[q]]='Z'
        helper.append(dict(q=q,kind=kind,phase_records=[b] if kind=='MX' else [],value=float(state.expectation(p,inverse))))
    out=dict(source=str(source),index=index,A=resource_A,orientation=seed.get('orientation',0),raw=raw,resource_stabilizers=checks,helper_zero_states=helper,
        resource_ok=all(abs(r['value']-1)<1e-9 for r in checks+helper),a_ready=seed['a_ready'],resource_cx=seed['cx'],
        x_byproduct_records=byproducts,
        scope='Exact ideal native source plus A-only factory, including any recorded A-X byproducts. No complete BC resource or full-score claim.')
    stem=write_stem(text,D,HERE/'boundary','a_factory_verified',source=out)
    out['stem']=str(stem);stem.with_suffix('.resource_check.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2),flush=True)
    return out

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('source');ap.add_argument('--index',type=int,default=0);a=ap.parse_args();verify(a.source,a.index)
