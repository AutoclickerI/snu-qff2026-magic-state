"""Final coverage and provenance audit; all outputs remain in this lane."""
import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import csv,hashlib,json,re,collections
from pathlib import Path
from synth import verify
H=Path(__file__).resolve().parent

def main():
 groups=json.loads((H/'lns_unique.json').read_text());rows=[];missing=[]
 for i,files in enumerate(groups):
  pf=H/'full'/f'lns_{i:04d}_release_alap.price.json'
  if not pf.exists() or 'check' not in json.loads(pf.read_text()):missing.append(i);continue
  price=json.loads(pf.read_text())
  for name in files:
   f=H/'runs'/Path(name).name;d=json.loads(f.read_text());v=verify(d);assert v['stim_target_pass'] and v['clean_pass'],f
   rows.append(dict(prep=str(f.relative_to(H)),representative=i,cx=v['cx'],depth=v['depth'],stim=True,BC2_clean=True,in_situ_exact=price.get('total'),c1=price.get('c1'),judge=price['check']['passed'],qasm=f'full/lns_{i:04d}_release_alap.qasm'))
 # Add feedback, cancellation, helper and fixed-model validation witnesses.
 covered={r['prep'] for r in rows};bytrace={}
 def trace(d):
  cells=sorted(set(d.get('cells',[]))|set(d['pivots'])|{q for l in d['ops'] for e in l for q in e})
  return repr((sorted(d['pivots']),bool(d.get('helper_x')),[(q,[tuple(e) for l in d['ops'] for e in l if q in e]) for q in cells]))
 for pf in (H/'full').glob('*.price.json'):
  jf=pf.with_name(pf.name.replace('.price.json','.json'))
  if not jf.exists():continue
  md=json.loads(jf.read_text());pr=json.loads(pf.read_text())
  if 'prep' not in md or 'check' not in pr or 'total' not in pr:continue
  key=trace(md['prep'])
  if key not in bytrace or pr['total']<bytrace[key]['total']:bytrace[key]=pr
 extras_missing=[]
 for pf in sorted((H/'runs').glob('*.prep.json')):
  if str(pf.relative_to(H)) in covered:continue
  d=json.loads(pf.read_text());v=verify(d);assert v['stim_target_pass'] and v['clean_pass'],pf
  pr=bytrace.get(trace(d))
  if pr is None:extras_missing.append(pf.name);continue
  rows.append(dict(prep=str(pf.relative_to(H)),representative=pr['tag'],cx=v['cx'],depth=v['depth'],stim=True,BC2_clean=True,in_situ_exact=pr['total'],c1=pr['c1'],judge=pr['check']['passed'],qasm='full/'+pr['tag']+'.qasm'))
 with (H/'synthesis_all.csv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=['prep','representative','cx','depth','stim','BC2_clean','in_situ_exact','c1','judge','qasm']);w.writeheader();w.writerows(rows)
 # Full QASM companions and completed receipts.
 missing_json=[];no_check=[];bad=[]
 for q in sorted((H/'full').glob('*.qasm')):
  jf=q.with_suffix('.json')
  if not jf.exists() or 'data_qubits' not in json.loads(jf.read_text()):missing_json.append(q.name)
  p=q.with_suffix('.price.json')
  if not p.exists() or 'check' not in json.loads(p.read_text()):no_check.append(q.name)
  elif not json.loads(p.read_text())['check']['passed']:bad.append(q.name)
 # Actual CLI totals compared against the aggregate evaluator for finalists.
 ref=[]
 for f in (H/'full').glob('*.exact.log'):
  txt=f.read_text();mt=re.search(r'1-F \(to 3rd order\) = (\S+)',txt);p=f.with_name(f.name.replace('.exact.log','.price.json'))
  if mt and p.exists():
   row=json.loads(p.read_text());ref.append(dict(tag=row['tag'],CLI_total=float(mt[1]),moment_total=row.get('total'),absolute_error=abs(float(mt[1])-row.get('total',float('nan')))))
 out=dict(clean_prep_aliases_priced=len(rows),unpriced_extra_preps=extras_missing,unique_wire_sequences=len(groups),missing_representative_prices=missing,missing_qasm_json=missing_json,full_without_check=no_check,judge_failed=bad,reference_comparisons=ref)
 (H/'FINAL_AUDIT.json').write_text(json.dumps(out,indent=2));print(json.dumps(out),flush=True)
if __name__=='__main__':main()
