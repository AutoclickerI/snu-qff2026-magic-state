"""Audit selected file hashes, circuit companions and local cited artifacts."""
import glob,hashlib,json,re
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[2]
m=json.loads((H/'selected_manifest.json').read_text());rows=m['files'];selected={x['path'] for x in rows}
prior=json.loads((R/'work/lanes/SOTA_20261028/checkpoint_manifest.json').read_text())
previous={x['path'] for x in prior['files']};published_known=set(m['published_dependencies'][i]['path'] for i in range(len(m['published_dependencies'])))|previous
missing=[];mismatch=[];qasm=[];no_spec=[];omitted_citations=[];receipt_checked=[];receipt_mismatch=[]
virtual_files={};virtual_errors=[]
idx_path=R/'work/lanes/GAUGE_SCHEDULE_20261028/search_parts/index.json'
if idx_path.is_file() and str(idx_path.relative_to(R)) in selected:
 idx=json.loads(idx_path.read_text());entries=[]
 for part in idx['parts']:
  p=idx_path.parent/part['name'];rel=str(p.relative_to(R))
  if rel not in selected or not p.is_file():virtual_errors.append('missing part '+rel);continue
  raw=p.read_bytes()
  if len(raw)!=part['bytes'] or hashlib.sha256(raw).hexdigest()!=part['sha256']:virtual_errors.append('part mismatch '+rel);continue
  piece=json.loads(raw)
  if len(piece)!=part['records']:virtual_errors.append('record mismatch '+rel)
  entries.extend(piece)
 reconstructed=(json.dumps(entries,indent=2)+'\n').encode()
 if len(entries)!=idx['records'] or len(reconstructed)!=idx['original_bytes'] or hashlib.sha256(reconstructed).hexdigest()!=idx['original_sha256']:
  virtual_errors.append('reconstructed search ledger mismatch')
 else:virtual_files[idx['original_path']]=idx['original_sha256']
for name in ('work/lanes/GAUGE_SCHEDULE_20261028/shallow_parts/index.json',
             'work/lanes/MEASURED_BC_20261028/resource_ablations_parts/index.json',
             'work/lanes/EARLY_BOUNDARY_20261028/isometry_search_parts/index.json'):
 ip=R/name
 if name not in selected or not ip.is_file():virtual_errors.append('missing ledger index '+name);continue
 idx=json.loads(ip.read_text());combined=[] if idx['type'] in ('list','lines') else {}
 for part in idx['parts']:
  p=ip.parent/part['name'];rel=str(p.relative_to(R))
  if rel not in selected or not p.is_file():virtual_errors.append('missing part '+rel);continue
  raw=p.read_bytes()
  if len(raw)!=part['bytes'] or hashlib.sha256(raw).hexdigest()!=part['sha256']:virtual_errors.append('part mismatch '+rel);continue
  val=json.loads(raw)
  if len(val)!=part['records'] or not isinstance(val,type(combined)):virtual_errors.append('record mismatch '+rel);continue
  if isinstance(combined,list):combined.extend(val)
  else:
   if set(combined)&set(val):virtual_errors.append('duplicate keys '+rel)
   combined.update(val)
 reconstructed=(''.join(combined) if idx['type']=='lines' else json.dumps(combined,indent=2)+'\n').encode()
 if len(combined)!=idx['records'] or len(reconstructed)!=idx['original_bytes'] or hashlib.sha256(reconstructed).hexdigest()!=idx['original_sha256']:
  virtual_errors.append('reconstructed ledger mismatch '+idx['original_path'])
 else:virtual_files[idx['original_path']]=idx['original_sha256']
patterns=[re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),re.compile(rb'gh[pousr]_[A-Za-z0-9]{30,}'),re.compile(rb'AKIA[0-9A-Z]{16}'),re.compile(rb'(?i)(password|secret|api[_-]?key)\s*[=:]\s*["\'][^"\'\s]{12,}["\']')]
suspicious=[]
for row in rows:
 p=R/row['path']
 if not p.is_file():missing.append(row['path']);continue
 b=p.read_bytes()
 if len(b)!=row['bytes'] or hashlib.sha256(b).hexdigest()!=row['sha256']:mismatch.append(row['path'])
 if any(pat.search(b) for pat in patterns):suspicious.append(row['path'])
 if p.suffix=='.qasm':
  qasm.append(row['path']);spec=str(p.with_suffix('.json').relative_to(R))
  if spec not in selected and spec not in published_known:no_spec.append(row['path'])
 if row['path'].endswith(('.price.json','.result.json','.receipt.json','.integration.json')):
  try: data=json.loads(b)
  except (ValueError,UnicodeError):data={}
  if isinstance(data,dict):
   expected=data.get('sha256') or data.get('qasm_sha256')
   target=row['path'].rsplit('.',2)[0]+'.qasm'
   if isinstance(expected,str) and len(expected)==64 and target in selected and (R/target).is_file():
    receipt_checked.append(row['path'])
    if hashlib.sha256((R/target).read_bytes()).hexdigest()!=expected:receipt_mismatch.append(dict(receipt=row['path'],qasm=target))
 if p.name=='REPORT.md':
  for ref in re.findall(r'`([^`\n]+)`',b.decode('utf-8',errors='replace')):
   if any(c in ref for c in ' []()=|<>') or len(ref)>180 or not re.search(r'\.(json|qasm|py|log|md)$',ref):continue
   for target in glob.glob(str(p.parent/ref)):
    x=Path(target).resolve()
    if x.is_file() and str(x.relative_to(R)) not in selected and str(x.relative_to(R)) not in published_known and str(x.relative_to(R)) not in virtual_files:
     omitted_citations.append(dict(report=row['path'],path=str(x.relative_to(R))))
result=dict(scope='Integrity and locally resolvable citations only; no guarantee about dynamically constructed paths or external dependencies.',
 selected_count=len(rows),qasm_count=len(qasm),knill_lanes_requested=m['knill_lanes_requested'],
 final_lanes_requested=m['final_lanes_requested'],missing_required=m['missing_required'],pending_report_markers=m['pending_report_markers'],
 report_consistency_warnings=m['report_consistency_warnings'],
 virtual_reconstructions=virtual_files,virtual_reconstruction_errors=virtual_errors,
 receipt_hashes_checked=len(receipt_checked),receipt_hash_mismatches=receipt_mismatch,missing=missing,hash_mismatches=mismatch,
 missing_qasm_companions=no_spec,omitted_cited_local_files=omitted_citations,suspicious_pattern_paths=suspicious,
 prior_overlap=sorted(selected&previous),expected_status_overlap=['docs/PLAN.md','docs/SOTA.md'],
 unexpected_prior_overlap=sorted((selected&previous)-{'docs/PLAN.md','docs/SOTA.md'}),
 prior_local_mismatches=m['prior_inventory']['local_mismatches'],status_document_mismatches=m['prior_inventory']['status_mismatches'],
 dependency_mismatches=m['dependency_mismatches'])
(H/'selection_audit.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
