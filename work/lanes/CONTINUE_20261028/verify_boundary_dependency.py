"""Compare actual continuation import paths with local and published helper.

Fetch the known prior Git blob into a mirrored temporary work/lanes path and
pass that path as --published-helper. No old checkout files are modified.
"""
import argparse, hashlib, importlib.util, json, os, subprocess, sys
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
PRIOR_BLOB='5c9dd0b0a730b4c7f7db6883476453a1da959ec6'

def blob(path):
    b=Path(path).read_bytes();return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()

def probe(helper):
    sys.path[:0]=[str(ROOT/'work/lanes/NATIVE2_20261027'),str(ROOT/'work/lanes/REBUILD20261027'),str(ROOT/'work/tools')]
    if helper:
        spec=importlib.util.spec_from_file_location('boundary_product',helper)
        module=importlib.util.module_from_spec(spec);sys.modules['boundary_product']=module;spec.loader.exec_module(module)
    from incumbent_a_sx import f,emit
    from b_phase_symmetries import feature,solve_binary
    from qtools.validity import raw_check
    p=ROOT/'work/lanes/JOINT_A_ISOMETRY_20261028/candidate_trim_64d6c05e108c8e8a_d6_20_19_10_2_22_16.qasm'
    text=p.read_text();ops,ds=f.parse_current(text)
    encoded=emit(ops,ds);raw=raw_check(encoded,[6,20,19,10,2,22,16])
    vectors=[1,2,4,7,16,21,31]
    return dict(imports=['incumbent_a_sx.f','incumbent_a_sx.emit','b_phase_symmetries.feature','b_phase_symmetries.solve_binary'],
        op_count=len(ops),detector_rows=len(ds),emitted_sha256=hashlib.sha256(encoded.encode()).hexdigest(),
        raw=raw,features=[feature(i,5) for i in range(32)],
        linear_solutions=[solve_binary(vectors,i) for i in range(32)])

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--published-helper');ap.add_argument('--child',choices=('local','published'));args=ap.parse_args()
    if args.child:
        print(json.dumps(probe(args.published_helper if args.child=='published' else None),sort_keys=True));return
    if not args.published_helper:ap.error('--published-helper is required')
    assert blob(args.published_helper)==PRIOR_BLOB,'temporary helper is not the published Git blob'
    out=[]
    for mode in ('local','published'):
        raw=subprocess.check_output([sys.executable,str(Path(__file__).resolve()),'--child',mode,'--published-helper',args.published_helper],cwd=ROOT,text=True)
        out.append(json.loads(raw))
    assert out[0]==out[1],'relevant observed import path differs'
    result=dict(published_head='7cb6d35a735df2630582f7f90efe31105ccc298d',published_helper_git_blob=PRIOR_BLOB,
      local_helper_git_blob=blob(ROOT/'work/lanes/NATIVE2_20261027/boundary_product.py'),
      compared_call_paths='incumbent_a_sx imports f and emit; b_phase_symmetries feature and solve_binary; parse/emit and raw check on full trimmed candidate',
      identical=True,observed=out[0],limitation='Not a proof of equivalence for other callers of certify or byproduct_candidates.')
    (HERE/'dependency_audit.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'identical':True,'emitted_sha256':out[0]['emitted_sha256'],'raw_ok':out[0]['raw']['ok'],'op_count':out[0]['op_count']}))
if __name__=='__main__':main()
