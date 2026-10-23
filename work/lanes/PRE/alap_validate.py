"""Promote and validate the fixed-suffix scheduling search shortlist."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', PYTHONDONTWRITEBYTECODE='1')
import sys
sys.dont_write_bytecode=True
import alap_search as a
import json, math, shutil, subprocess

rows=[]
for p in (a.HERE/'alap_search').glob('*.json'):
    r=json.loads(p.read_text())
    if math.isfinite(r.get('loss',math.inf)):
        rows.append((p,r))
groups=[('alap_ordered',lambda p,r:p.stem.startswith('alap_r_c0_')),
        ('alap_commuting',lambda p,r:p.stem.startswith('alap_r_c1_')),
        ('alap_best',lambda p,r:p.stem.startswith('alap_lns_'))]
out=[]
for label,pred in groups:
    if sys.argv[1:] and label not in sys.argv[1:]:continue
    choices=[(p,r) for p,r in rows if pred(p,r)]
    best=min(r['loss'] for p,r in choices)
    # Differences below 1e-15 are floating-point roundoff in this ~1e-4
    # objective; favor lower rejection among those physical-loss ties.
    src,row=min(((p,r) for p,r in choices if r['loss']<=best+1e-15),key=lambda x:x[1]['A1'])
    qp=a.HERE/(label+'.qasm');jp=qp.with_suffix('.json')
    qp.write_text(src.with_suffix('.qasm').read_text())
    row['promoted_from']=str(src.relative_to(a.HERE))
    jp.write_text(json.dumps(row,indent=2)+'\n')
    cmd=[sys.executable,str(a.ROOT/'work/lanes/EVAL/exact2.py'),str(qp),'--procs','3','--top','0','--json',str(a.HERE/(label+'.exact.json'))]
    run=subprocess.run(cmd,text=True,capture_output=True,check=True)
    (a.HERE/(label+'_exact2.log')).write_text(run.stdout+run.stderr)
    rep=a.tprep.check(qp.read_text(),a.DATA,shots=10**6,seed=0)
    row['check_1e6']=dict(passed=rep.passed,format=rep.format_ok,class_ok=rep.class_ok,correctness=rep.correct_ok,acceptance_ok=rep.acceptance_ok,acceptance=rep.acceptance,score=rep.score,report=str(rep))
    jp.write_text(json.dumps(row,indent=2)+'\n')
    print(label,src.stem,row['loss'],row['A1'],rep.passed,rep.acceptance,flush=True)
    assert rep.passed
    out.append(dict(label=label,source=src.stem,loss=row['loss'],loss1=row['loss1'],A1=row['A1'],check_1e6=row['check_1e6']))
dest=a.HERE/'alap_validated.json'
if sys.argv[1:] and dest.exists():
    out=[r for r in json.loads(dest.read_text()) if r['label'] not in sys.argv[1:]]+out
dest.write_text(json.dumps(out,indent=2)+'\n')
