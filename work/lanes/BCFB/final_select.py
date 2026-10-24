"""Choose from completed official re-draw means; certify exact artifact identity."""
import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import json,hashlib,shutil
from pathlib import Path
from evaluate import H,judge
from synth import verify

def main():
 assert json.loads((H/'RUN_SUMMARY.json').read_text())['status']=='ALL_REQUESTED_BUDGETS_COMPLETE'
 rd=json.loads((H/'redraw_summary.json').read_text());manifest=json.loads((H/'redraw_manifest.json').read_text())
 assert set(rd)==set(manifest),(set(manifest)-set(rd))
 assert all(r['complete100'] and r['min_acceptance']>=.505 for r in rd.values())
 ordered=sorted(rd,key=lambda k:rd[k]['mean']);tag=ordered[0];p=H/'finalists'/tag;text=p.with_suffix('.qasm').read_text();md=json.loads(p.with_suffix('.json').read_text());r=json.loads(p.with_suffix('.screen.json').read_text())
 assert abs(r['c1'])<1e-12 and r['check']['passed'] and p.with_suffix('.exact.log').exists() and p.with_suffix('.mc.log').exists()
 v=verify(md['prep']);assert v['clean_pass'] and v['stim_target_pass']
 # Keep exact emitted text and data-qubit ordering used by the measured runs.
 (H/'best.qasm').write_text(text);(H/'best.json').write_text(json.dumps(md,indent=2))
 assert (H/'best.qasm').read_bytes()==p.with_suffix('.qasm').read_bytes()
 assert json.loads((H/'best.json').read_text())==md
 ck=judge((H/'best.qasm').read_text(),json.loads((H/'best.json').read_text()));assert ck['passed'] and ck['acceptance']>=.505
 assert ck['n_2q']==md['CX']
 base=json.loads((H/'base_redraw_reference.json').read_text());out=dict(selected=tag,criterion='minimum completed >=100 seed-0 re-draw mean; no CX/depth objective',ranked=[dict(stem=k,**rd[k]) for k in ordered],selected_exact={k:r[k] for k in ('c1','second','third','total','exp_minus_A1')},baseline=base,relative_gain=1-rd[tag]['mean']/base['mean'],sha256=hashlib.sha256(text.encode()).hexdigest(),fresh_check_1e6=ck,prep_verification=v)
 (H/'FINAL_SELECTION.json').write_text(json.dumps(out,indent=2));print(json.dumps(out),flush=True)
if __name__=='__main__':main()
