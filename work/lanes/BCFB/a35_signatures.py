import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
import json,math,hashlib,collections
H=Path(__file__).resolve().parent;D=H/'a35';sys.path.insert(0,str(D/'sparse'));import frontend as f
A={1,14,8,9,2,16,15}
def run(stem):
 text=stem.with_suffix('.qasm').read_text();f.DATA=json.loads(stem.with_suffix('.json').read_text())['data_qubits'];ops,dets=f.parse_current(text)
 old=f.noise_blocks;f.noise_blocks=lambda txt,p,first_order=True:old(txt,p,first_order=False)
 try:m=f.make_model(ops,dets)
 finally:f.noise_blocks=old
 e=f.Engine(m);flag=next(i for i,ds in enumerate(dets) if ds=={16});P0=math.prod(1-c['p'] for c in m.chans);P1=A1=N1=0.;cache={};out=[]
 for fault in m.faults:
  key=fault['s'],fault['d']
  if key not in cache:cache[key]=e.ntable(*key)
  aa,nn=cache[key];w=P0*fault['p']/(1-m.chans[fault['chan']]['p']);P1+=w;A1+=w*e.A0*aa
  if nn is not None:N1+=w*e.A0*float(nn[fault['e']])
  op=ops[fault['ins']]
  if op.time>=35 and A.intersection(fault['qs']):
   out.append(dict(channel=fault['chan'],time=op.time,instruction=op.kind,qubits=fault['qs'],pauli=fault['pauli'],probability=fault['p'],rotation_signs=fault['s'],detector_mask=fault['d'],output_mask=fault['e'],A_flag_flip=bool(fault['d']>>flag&1),single_event_acceptance=aa*e.A0,single_event_accepted_loss=0. if nn is None else float(nn[fault['e']])*e.A0))
 au=P0*e.A0+A1+1-P0-P1
 result=dict(stem=str(stem.relative_to(H)),qasm_sha256=hashlib.sha256(text.encode()).hexdigest(),detector_rows=[sorted(ds) for ds in dets],A_flag_detector=flag,A_fault_signatures=out,P0=P0,P1=P1,A0=e.A0,A1=A1,N1=N1,A_upper=au,finite_p_loss_lower_bound_numerical=N1/au,scope='Full-current-instrument propagated signatures, exact finite-p channel probabilities; floating numerical bound, no c1/p30 pruning.')
 Path(str(stem)+'.signatures.json').write_text(json.dumps(result,indent=2));print(stem.name,'signatures',len(out),'bound',N1/au,flush=True)
if __name__=='__main__':
 for s in sys.argv[1:]:run(Path(s).resolve())
