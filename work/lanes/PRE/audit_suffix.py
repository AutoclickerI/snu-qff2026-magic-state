from common import *
import hashlib
base=json.loads((HERE/'v12_reference.json').read_text())
baseev=Eval((HERE/'v12_reference.qasm').read_text(),base['data_qubits'])
bt,_=native_mapping(base,baseev)
rows=[]
for split in sorted(HERE.glob('*.split.json')):
    name=split.name.removesuffix('.split.json');path=HERE/f'{name}.json';meta=json.loads(path.read_text())
    text=(HERE/f'{name}.qasm').read_text();ev=Eval(text,meta['data_qubits']);actual,_=native_mapping(meta,ev)
    s=meta['schedule'];npref=s['npre'];ops=s['ops']
    assert [(k,tuple(qs)) for k,qs,b in ops[npref:]]==[(k,qs) for k,qs,b in OPS[NPRE:]],name
    assert len({actual[npref+j]-bt[NPRE+j] for j in range(len(OPS)-NPRE)})==1,name
    meta.update(native_times=[actual[i] for i in range(len(ops))],suffix_native_timing_verified=True,
                sha256=hashlib.sha256(text.encode()).hexdigest())
    assert max(actual[i] for i in range(npref))==meta['pre_end_step']
    assert max(actual.values())+1==meta['depth']
    path.write_text(json.dumps(meta,indent=2)+'\n')
    rows.append(dict(name=name,sha256=meta['sha256'],suffix_ops=True,suffix_relative_native_timing=True))
(HERE/'suffix_audit.json').write_text(json.dumps(rows,indent=2)+'\n')
print(f'{len(rows)} exact native suffix comparisons passed',flush=True)
