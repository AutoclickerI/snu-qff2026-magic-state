"""Audit the delivered report against native schedules and saved judge inputs."""
import os,sys,json,hashlib,runpy
from pathlib import Path
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from co_design import S,native_times
state=runpy.run_path(str(HERE/'report.py'));rows=[]
for name,s,m,seeds,mean in state['full']:
 text=(HERE/(name+'.qasm')).read_text();assert hashlib.sha256(text.encode()).hexdigest()==s['sha256'];assert s['data_qubits']==m['data_qubits']
 check=(HERE/(name+'.check.log')).read_text()
 for gate in ('format','class','correctness'):assert any(line.strip().startswith(gate+':') and 'PASS' in line for line in check.splitlines()),(name,gate)
 h,raw,d=S.qasm_ops(text);units=S.fold_units(raw);ts=native_times(text,units);saved=json.loads((HERE/(name+'.units.json')).read_text())
 assert [u.lines for u in units]==[u['lines'] for u in saved],name
 assert ts==[u['t'] for u in saved],name
 assert m['cx']==sum(u.name=='CX' for u in units),name
 assert m['R_native']==min(u['t'] for u in saved if u['region']=='round'),name
 if 'R_A_native' in m:assert m['R_A_native']==min((u['t'] for u in saved if u['region']=='round_a'),default=m['R_native'])
 bd=[u for u in saved if u['region']=='round' and u.get('round_offset')==1 and u['name']=='CX']
 assert len(bd)==7 and all(u['t']==m['R_native']+1 for u in bd),name
 rows.append(dict(name=name,R_A=m.get('R_A_native',m['R_native']),R_BC=m['R_native'],CX=m['cx'],native_units=len(units),judge_format_class_correctness=True,acceptance=s['acceptance_1e6'],MC_mean=mean))
manifest=[]
for q in sorted(HERE.glob('*.qasm')):
 m=json.loads(q.with_suffix('.json').read_text());assert len(m['data_qubits'])==7 and len(set(m['data_qubits']))==7
 manifest.append(dict(file=q.name,sha256=hashlib.sha256(q.read_bytes()).hexdigest(),data_qubits=m['data_qubits'],judge_receipt=q.with_suffix('.check.log').exists()))
(HERE/'manifest.json').write_text(json.dumps(manifest,indent=1));(HERE/'audit.json').write_text(json.dumps(dict(reported_circuits=rows,qasm_files_with_valid_metadata=len(manifest),all_reported_native_times_verified=True),indent=1));print('AUDIT PASS:',len(rows),'reported circuits;',len(manifest),'QASM/JSON pairs')
