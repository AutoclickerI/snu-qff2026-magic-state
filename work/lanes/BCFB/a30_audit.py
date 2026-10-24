from a30_common import *
import hashlib,subprocess
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ver=json.loads((D/'verified_finalists.json').read_text());win=min(ver,key=lambda r:r['allorders']['loss']);stem=D/'finalists'/win['stem']
assert sha(H/'best.qasm')==sha(stem.with_suffix('.qasm'));assert (D/'inputs/v30f.qasm').read_bytes()==(ROOT/'work/lanes/MAIN/v30f.qasm').read_bytes()
expected={'exact2.py':'2837a969410737639c9e49b932b0ea35c7536acab2c0a2423c211c36e71bf6c2','engine.py':'cad06c4c097b433a48a2dc173ac8490b25166c6585d617f437f3217f7b7e627a','model.py':'8600b40c6c19f74b0040509a93db077070a96645ec1a79f2ff3c49d14dd0ae79'}
assert all(sha(ROOT/'work/lanes/EVAL'/name)==digest for name,digest in expected.items())
assert sha(H/'xtim_speed_snapshot.py')==sha(ROOT/'work/lanes/XTIM/speed_predict.py');assert sha(H/'inputs/mc3.py')==sha(ROOT/'work/lanes/MAIN/spec/mc3.py')
diff=json.loads(Path(str(stem)+'.diff.json').read_text());assert diff['outside_A_native_units_and_times_equal'] and diff['other_detector_rows_equal']
rows=json.loads((D/'search_summary.json').read_text());receipts=[json.loads(p.read_text()) for p in (D/'runs').glob('feedback_81*.receipt.json')];assert len(receipts)==8 and all(r['status']=='BUDGET_FINISHED' and r['seconds']>=1200 for r in receipts)
run=subprocess.run(['ssh','-q','-o','ControlMaster=no','-o','ControlPath=none','owl','docker ps --format "{{.Names}}"'],capture_output=True,text=True,check=True);assert not any(x.startswith('bcfb_') for x in run.stdout.splitlines()),run.stdout
(D/'process_exit_audit.json').write_text(json.dumps(dict(status='PASS',all_launched_jobs_observed_exited=True,owl_bcfb_containers=[],intentional_stop=dict(stem='a30_fbn_08352',reason='XTIM SLOW',mc_exit=-15,zebra_speed_exit=143,exact_cli_exit=0,verification_wrapper_exit=1),failed_fastpick_probe='missing XTIM source on owl; copied byte-identical snapshot into BCFB and completed retry'),indent=2))
(D/'search_budget_summary.json').write_text(json.dumps(dict(feedback=receipts,formulations=sum(r['rows'] for r in rows.values()),valid_cubic_prices=sum(r['valid'] for r in rows.values()),acceptance_floor_passes=sum(r['eligible'] for r in rows.values())),indent=2))
r=dict(status='PASS',winner=win['stem'],qasm_sha256=sha(H/'best.qasm'),metadata_sha256=sha(H/'best.json'),base_qasm_sha256=sha(D/'inputs/v30f.qasm'),unchanged_exact_sources=expected,xtim_predictor_sha256=sha(H/'xtim_speed_snapshot.py'),mc3_sha256=sha(H/'inputs/mc3.py'),outside_A_native_units_and_times_equal=True,other_detector_rows_equal=True,all_compute_jobs_exited=True,allorders_delta=win['allorders']['loss']-5.8937742042181006e-5)
(D/'delivery_audit.json').write_text(json.dumps(r,indent=2));print(json.dumps(r),flush=True)
