import dataclasses
import hashlib
import json
from pathlib import Path
import sys
import tprep
import ft
import early_merge
import merge

best=json.loads(Path('BEST.json').read_text());stem=best['stem']
text=Path('best.qasm').read_text();meta=json.loads(Path('best.json').read_text())
assert text==Path(stem+'.qasm').read_text()
rep=tprep.check(text,meta['data_qubits'],shots=10**6,seed=0)
assert rep.passed,str(rep)
saved=json.loads(Path(stem+'.score.json').read_text())['check_1e6']
assert abs(rep.score-saved['score'])<1e-15
prep_stem=stem.split('_m27_29')[0]
prep=json.loads(Path(prep_stem+'.prep.json').read_text())
rules={r:len(ft.faults(prep,rule=r)) for r in ('base','clean','robust','pairs')}
if meta['rule']=='clean':assert rules['clean']==0
sys.path.insert(0,'../ST_BC');import check
assert check.verify(prep)
raw,_,R,end,status,wall=early_merge.build({'a':json.load(open('../DR/prepA_L5_s7307.json')),'bc':prep},
       early_merge.LAYOUTS['L5'],early_merge.MOVES['L5'],workers=1)
rebuilt,*_=merge.build({'a':json.load(open('../DR/prepA_L5_s7307.json')),'bc':prep},
       ['a','bc'],early_merge.LAYOUTS['L5'],early_merge.MOVES['L5'])
assert raw==rebuilt
out=dict(best=best,check_1e6=dataclasses.asdict(rep),passed=rep.passed,rule_audit=rules,
         early=dict(round_start=R,status=status,byte_identical=True),
         qasm_sha256=hashlib.sha256(text.encode()).hexdigest())
Path('FINAL_VERIFICATION.json').write_text(json.dumps(out,indent=2))
print('FINAL',rep.passed,'mean',best['mean'],'acceptance',best['seed0_acceptance'],'rules',rules,'EARLY',R,flush=True)
