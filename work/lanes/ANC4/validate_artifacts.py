import sys,json,re,hashlib
sys.dont_write_bytecode=True
from pathlib import Path
HERE=Path(__file__).resolve().parent
qasm=list(HERE.rglob('*.qasm'))
for p in qasm:
 j=json.loads(p.with_suffix('.json').read_text());assert len(j['data_qubits'])==len(set(j['data_qubits']))==7,p
for p in HERE.glob('grid_*.qasm'):
 x=p.with_suffix('.exact.log').read_text();assert 'first order : c1 p =' in x,p
 c=json.loads(p.with_suffix('.check.json').read_text());assert not c['format_errors'] and not c['class_error'] and not c['correctness_errors'],p
 if p.stem!='grid_routed':assert c['acceptance']>=0.5,p
for p in (HERE/'gf').glob('*.qasm'):
 x=p.with_suffix('.exact.log').read_text();assert '1-F (to 3rd order)' in x,p
 assert abs(float(re.search(r'c1 p = (\S+)',x)[1]))<1e-12,p
selected=json.loads((HERE/'mc_selection.json').read_text())['selected']
receipts=[]
for _,name in selected:
 p=HERE/(name+'.qasm');m=json.loads(p.with_suffix('.mc.json').read_text());assert [v['seed'] for v in m['seeds']]==[0,1000,2000];assert m['shots']==10**8;assert all(v['passed'] and v['acceptance']>=0.5 for v in m['seeds']);assert abs(m['mean']-sum(v['score'] for v in m['seeds'])/3)<1e-15
 receipts.append(dict(name=name,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),mean=m['mean'],seed0_acceptance=m['seeds'][0]['acceptance']))
out=dict(qasm_metadata_pairs=len(qasm),grid_screens=13,grid_free_screens=33,mc_finalists=receipts,validated=True)
(HERE/'artifact_validation.json').write_text(json.dumps(out,indent=2)+'\n');print(out)
