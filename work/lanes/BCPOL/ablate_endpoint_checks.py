"""Exact all-orders check ablation by summing disjoint detector sectors."""
import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
H=Path(__file__).resolve().parent
from cache import setup
from boundary import audit,unpack
from cache_allorders import exact_prep
from synth import C,ROWS
from moments_batch import exact2,evaluate
import numpy as np,json,re,math
stem=H/'inputs/cache_rank4_3_after_check';ev,b,classes,prep,ext,hh=setup(stem);_,_,rec=audit(stem)
z=np.load(stem.with_suffix('.boundary_allorders.npz'),allow_pickle=False);assert hh==str(z['exterior_hash']);N,A=z['N'],z['A'];P=exact_prep(ev,prep,len(N));gens={(g['q'],g['pauli']):g['packed'] for g in rec['generators']};shifts={}
for cell,row in [(19,ROWS[0]),(17,ROWS[2])]:
 v=0
 for i in row:v^=gens[C[i],'X']
 s,d,e=unpack(v,rec['nd']);assert s==0 and e==0 and d.bit_count()==1,(s,d,e)
 shifts[cell]=b.express(v)
assert shifts[19]!=shifts[17]
md=json.loads(stem.with_suffix('.json').read_text());text=stem.with_suffix('.qasm').read_text();bits={x['zero_cell']:set(x['readout_bits']) for x in md['endpoint_parity']};results=[]
for dropped in [[],[19],[17],[19,17]]:
 offsets=[0]
 for cell in dropped:offsets += [v^shifts[cell] for v in offsets[:]]
 n=sum(N[np.arange(len(N))^k] for k in offsets);a=sum(A[np.arange(len(A))^k] for k in offsets);r=dict(dropped=dropped,loss=float(P@n/(P@a)),acceptance=float(P@a),numerator=float(P@n))
 lines=[];removed=0
 for line in text.splitlines():
  if line.startswith('// DETECTOR') and any(set(map(int,re.findall(r'c\[(\d+)\]',line)))==bits[cell] for cell in dropped):removed+=1
  else:lines.append(line)
 assert removed==len(dropped)
 ablated='\n'.join(lines)+'\n';ee=exact2.Eval(ablated,md['data_qubits']);r['c1']=float(ee.fp@ee.n_single);r['A1']=float(ee.fp@(1-ee.a_single));r['exp_minus_A1']=math.exp(-r['A1'])
 if abs(r['c1'])<1e-12:r['cubic']=evaluate(ee)['total']
 else:r['cubic_status']='INVALID_C1'
 out=H/'inputs'/('ablate_flags_'+('_'.join(map(str,dropped)) or 'none'));out.with_suffix('.qasm').write_text(ablated);out.with_suffix('.json').write_text(json.dumps(dict(data_qubits=md['data_qubits']),indent=2));results.append(r);print(json.dumps(r),flush=True)
(H/'endpoint_check_ablation.json').write_text(json.dumps(dict(shift_classes=shifts,rows=results),indent=2))
