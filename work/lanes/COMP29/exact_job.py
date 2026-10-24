"""Run the unchanged reference CLI, recording its printed precision.

No tracing or evaluator modifications. Cache and outputs remain in COMP29.
"""
import os,sys,json,runpy,time,re,io,contextlib,fcntl,hashlib
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
os.environ['XTIM_TWIRL_CACHE_DIR']=str(H/'.xtim_cache')
os.environ.pop('COMP29_PRIORITY_RESUME',None)
if os.environ.pop('COMP29_PRIORITY_INNER',None) is None:
    from priority30 import run_one
    run_one(sys.argv[1:])
import xtim
xtim.cache_dir=str(H/'.xtim_cache')
stem=H/sys.argv[1];procs=sys.argv[2] if len(sys.argv)>2 else '1'
assignment=H/'reference_owners.json'
if assignment.exists():
    owner=json.loads(assignment.read_text()).get(stem.name)
    host=os.environ.get('COMP29_HOST',os.uname().nodename)
    if owner and owner!=host:
        print('Reference assigned to',owner,stem,flush=True);sys.exit(0)
lock=stem.with_suffix('.exact.lock').open('a+')
try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
except BlockingIOError:
    print('Already running:',stem,flush=True);sys.exit(0)
source_hash=hashlib.sha256(stem.with_suffix('.qasm').read_bytes()).hexdigest()
receipt=stem.with_suffix('.exact.json')
if receipt.exists():
    old=json.loads(receipt.read_text())
    if old.get('unchanged_cli') and old.get('source_sha256')==source_hash:
        print('Verified cached reference:',stem,flush=True);sys.exit(0)
eq_receipt=stem.with_suffix('.exact_equivalent.json')
if eq_receipt.exists():
    eq=json.loads(eq_receipt.read_text())
    if eq.get('reference_unchanged_cli') and eq.get('source_sha256')==source_hash:
        print('Verified conditional-equivalence cache:',stem,flush=True);sys.exit(0)
equivalence=H/'q19_equivalence.json'
if equivalence.exists():
    cert=json.loads(equivalence.read_text())
    pair=next((p for p in cert['cases'] if p['stem']==stem.name),None)
    if pair:
        from tprep.noise import STANDARD
        assert all(getattr(STANDARD,k)==v for k,v in cert['noise_parameters'].items())
        assert json.loads(stem.with_suffix('.json').read_text())['data_qubits']==cert['data_qubits']
        assert source_hash==pair['sha256']
        assert hashlib.sha256((H/(pair['representative']+'.qasm')).read_bytes()).hexdigest()==pair['representative_sha256']
        if receipt.exists():
            print('Preserving existing direct reference:',stem,flush=True);sys.exit(0)
        s=json.loads(stem.with_suffix('.screen.json').read_text())
        alias=dict(kind='proved conditional equivalence',representative=pair['representative'],certificate='q19_equivalence.json',source_sha256=source_hash,representative_sha256=pair['representative_sha256'],exp_minus_A1=s['exp_minus_A1'],c1=s['c1'],alpha_at_p001=cert['alpha_at_p001'],pending_representative=True)
        stem.with_suffix('.exact_equivalent.json').write_text(json.dumps(alias,indent=2)+'\n')
        print('Proved conditional-equivalence reference:',stem,'->',pair['representative'],flush=True);sys.exit(0)
path=ROOT/'work/lanes/EVAL/exact2.py'
software={name:hashlib.sha256((path.parent/name).read_bytes()).hexdigest() for name in ('exact2.py','engine.py','model.py')}
start=time.monotonic()
from canonical_detectors import canonical
try:input_stem,detorder=canonical(stem)
except Exception as err:
    stem.with_suffix('.exact_error.json').write_text(json.dumps(dict(error=repr(err),stage='detector representation guard'),indent=2)+'\n')
    raise
sys.argv=[str(path),str(input_stem.with_suffix('.qasm')),'--third','--procs',procs,'--top','0']
buf=io.StringIO()
with contextlib.redirect_stdout(buf):runpy.run_path(str(path),run_name='__main__')
text=buf.getvalue();print(text,flush=True)
patterns={'loss1':r'c1 p = ([\deE+.-]+)','loss2':r'second order: ([\deE+.-]+)','loss3':r'third order: ([\deE+.-]+)','total':r'1-F \(to 3rd order\) = ([\deE+.-]+)','exp_minus_A1':r'exp\(-A1\) = ([\deE+.-]+)'}
out={k:float(re.search(p,text)[1]) for k,p in patterns.items()}
out.update(seconds=time.monotonic()-start,unchanged_cli=True,precision='unchanged CLI printed digits',input_stem=str(input_stem),detector_permutation=detorder,source_sha256=source_hash,evaluator_sha256=software)
stem.with_suffix('.exact.json').write_text(json.dumps(out,indent=2)+'\n')
