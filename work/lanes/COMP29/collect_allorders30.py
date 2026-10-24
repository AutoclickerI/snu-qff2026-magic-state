"""Assemble independent decoder-character shards with full receipt checks."""
import os,sys,json,hashlib,math
from pathlib import Path
H=Path(__file__).resolve().parent
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
sys.dont_write_bytecode=True
import allorders_general as a
for name in sys.argv[1:]:
    tasks=[t for t in json.loads((H/'priority30.json').read_text()) if t['kind']=='allorders' and t['stem']==name]
    receipts=[H/(t['id']+'.priority.json') for t in tasks]
    if not tasks or not all(p.exists() for p in receipts):
        print(name,'pending',sum(p.exists() for p in receipts),'/',len(tasks));continue
    rs=[json.loads(p.read_text()) for p in receipts];sha=hashlib.sha256((H/(name+'.qasm')).read_bytes()).hexdigest()
    assert all(r['passed'] and r['source_sha256']==sha for r in rs),name
    prep=a.prepare(H/name);e=prep[1];keys=[None]+e.keys
    rows={}
    for r in rs:
        assert r['keys']==len(keys)
        assert r['validation']['channel_multiset_match'] and r['validation']['rotation_and_decoder_match']
        for row in r['rows']:
            index=row['index'];assert index not in rows
            assert json.dumps(row['key'])==json.dumps(keys[index]);rows[index]=row
    assert set(rows)==set(range(len(keys)))
    A=rows[0]['value'];N=.5*(A-sum(w*b*rows[i+1]['value'] for i,(w,b) in enumerate(zip(e.W,e.beta))))
    result=dict(loss=N/A,acceptance=A,numerator=N,width=prep[-1]['width'],active_projectors=rs[0]['validation']['active_projectors'],seconds=sum(r['seconds'] for r in rs),procs=len(rs),validated=True,source='BCPOL unchanged prepare/validate/one; decoder-character shards',source_sha256=sha,shard_receipts=[p.name for p in receipts])
    (H/(name+'.allorders.json')).write_text(json.dumps(result,indent=2)+'\n')
    (H/(name+'.allorders_general.validation.json')).write_text(json.dumps(rs[0]['validation'],indent=2)+'\n')
    print(name,result)
