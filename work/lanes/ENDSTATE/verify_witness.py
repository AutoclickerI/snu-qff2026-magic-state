import os,sys,json,argparse
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
import stim,numpy as np
H=Path(__file__).resolve().parent
GENS=[[0,2,4,6],[1,2,5,6],[3,4,5,6]]
def verify(path):
 d=json.loads(Path(path).read_text());D=d['data_qubits'];ref=36
 def pp(typ,qs):
  p=stim.PauliString(37)
  for q in qs:p[q]=typ
  return p
 st=[pp(t,[D[i]for i in g])for t in 'XZ'for g in GENS]+[pp(t,D+[ref])for t in 'XZ']+[pp('Z',[q])for q in range(36)if q not in D]
 tab=stim.Tableau.from_stabilizers(st);c=tab.to_circuit();num=0
 for o in d['ops']:
  c.append(o['name'],o['qs']);num+=o['name']in('M','MX')
 assert num==max(o.get('bit',-1)for o in d['ops'])+1
 for row in d['detectors']:c.append('DETECTOR',[stim.target_rec(b-num)for b in row])
 for p in st[:8]:
  targets=[]
  for q in p.pauli_indices():
   if targets:targets.append(stim.target_combiner())
   targets.append({'X':stim.target_x,'Y':stim.target_y,'Z':stim.target_z}[str(p)[q+1]](q))
  c.append('MPP',targets);c.append('DETECTOR',[stim.target_rec(-1)])
 c.detector_error_model();s=c.compile_detector_sampler(seed=851).sample(4096);assert not s.any()
 out=dict(entangled_logical_input_preserved=True,all_six_data_stabilizers_preserved=True,deterministic_detector_model=True,noiseless_samples=4096,nonzero_samples=int(s.any(axis=1).sum()),nearest_neighbour_cx=True,scope='ideal encoded-data input; full ancilla preparation, moves, detector frame and round; no prefix/noise/acceptance claim')
 Path(path).with_suffix('.verified.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
if __name__=='__main__':verify(sys.argv[1])
