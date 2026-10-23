"""Real-grid verification for all retained L2 circuits."""
import json, sys, time
from pathlib import Path
ROOT=Path('/home/jihoon/competitions/quantumn/work')
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
import tprep
import fast_check
for qasm in map(Path, sys.argv[1:]):
    if not qasm.is_absolute(): qasm=HERE/qasm
    meta=qasm.with_suffix('.json')
    old=json.loads(meta.read_text()) if meta.exists() else {}
    data=old.get('data_qubits')
    if data is None: raise SystemExit(f'{meta}: missing data_qubits')
    start=time.time(); rep=fast_check.check(qasm.read_text(),data,shots=10**8,seed=0,procs=8)
    scan=tprep.fault_scan(qasm.read_text(),data,processes=8) if rep.passed else None
    out={**old,'data_qubits':data,'score':rep.score,'sem':rep.sem,'acceptance':rep.acceptance,
         'n_2q':rep.n_2q,'shots':10**8,'seed':0,'passed':rep.passed,
         'c1':None if scan is None else scan.c1,'fault_scan_pass':None if scan is None else scan.c1==0,
         'seconds':time.time()-start,'report':str(rep)}
    meta.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'qasm':qasm.name,'score':rep.score,'sem':rep.sem,'acceptance':rep.acceptance,
                      'n_2q':rep.n_2q,'passed':rep.passed,'c1':out['c1'],'seconds':out['seconds']}),flush=True)
