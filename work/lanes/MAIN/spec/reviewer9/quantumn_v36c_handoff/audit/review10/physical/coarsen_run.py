import sys,json,contextlib,hashlib,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'evaluator'))
import sparse_walsh as sw
from frontend import parse_current
BASE=ROOT.parents[2]/'quantumn_review10/work/lanes/MAIN/v36c'
qasm=BASE.with_suffix('.qasm').read_text()
meta=json.loads(BASE.with_suffix('.json').read_text())
ops,dets=parse_current(qasm)
physical='\n'.join(l for l in qasm.splitlines() if not l.startswith('// DETECTOR'))+'\n'
specs={'b_pair_17_19':[17,19],'source_b_8_19':[8,19],'c_history_21_22_23_55':[21,22,23,55],'control_c43':[25]}
if len(sys.argv)>1:specs={k:v for k,v in specs.items() if k in sys.argv[1:]}
out=[]
baseline=json.loads((BASE.parent/'sparse/v36c_canonical_sparse_result.json').read_text())
for name,inds in specs.items():
 stem=ROOT/('v36c_coarse_'+name)
 delta=sum(1<<i for i in inds);pivot=inds[0]
 new=[dets[i]^(dets[pivot] if delta>>i&1 else set()) for i in range(len(dets)) if i!=pivot]
 text=physical+''.join('// DETECTOR '+' '.join('c[%d]'%j for j in sorted(r))+'\n' for r in new)
 stem.with_suffix('.qasm').write_text(text)
 stem.with_suffix('.json').write_text(json.dumps({'data_qubits':meta['data_qubits'],'review_probe':'syndrome-subspace coarsening; no physical gates changed; not promoted'}))
 record={'name':name,'delta_indices':inds,'delta_decimal':str(delta),'original_detector_rows':[sorted(dets[i]) for i in inds],'pivot':pivot,'new_constraint_rows':len(new),'qasm_sha256':hashlib.sha256(text.encode()).hexdigest()}
 try:
  with stem.with_suffix('.log').open('w') as f,contextlib.redirect_stdout(f):
   r=sw.run(stem,72,True,8)
  record.update({k:r[k] for k in ['loss','acceptance','channels','seconds','conditional_loss_kernel_omission_bound']})
  a,l=record['acceptance'],record['loss'];a0,l0=baseline['acceptance'],baseline['loss']
  record.update(delta_acceptance=a-a0,delta_loss=l-l0,added_sector_conditional_loss=(a*l-a0*l0)/(a-a0))
 except Exception as e:record.update(error=str(e),traceback=traceback.format_exc())
 out.append(record)
 (ROOT/'coarsen_results.json').write_text(json.dumps({'baseline':{k:baseline[k] for k in ['loss','acceptance','channels']},'results':out},indent=2))
 print(json.dumps(record),flush=True)
