"""Native noise identity plus classical label wiring; ignores gate text order only."""
import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
import json,hashlib,re,collections
H=Path(__file__).resolve().parent;ROOT=H.parents[2];sys.path.insert(0,str(ROOT/'work'))
import reorder
from build import S,native_times
D=H/'blue'
def key(text,md):
 _,raw,tail=S.qasm_ops(text);us=S.fold_units(raw);ts=native_times(text,us)
 measures=sorted((u.qs,t,tuple(l for l in u.lines if l.startswith('measure'))) for u,t in zip(us,ts) if u.name in ('MEASURE','MX'))
 obj=[reorder.signature(text),measures,sorted(tail),md['data_qubits']]
 return hashlib.sha256(json.dumps(obj,sort_keys=True).encode()).hexdigest()
def main():
 groups=collections.defaultdict(list)
 for f in sorted((D/'finalists').glob('*.qasm')):
  md=json.loads(f.with_suffix('.json').read_text());groups[key(f.read_text(),md)].append(f.stem)
 (D/'identity_groups.json').write_text(json.dumps(groups,indent=2));print('circuits',sum(map(len,groups.values())),'unique native noise/wiring keys',len(groups))
 for k,v in groups.items():
  if any(n in v for n in ['blue_d15_c105_s706_00405','blue_d15_c90_s704_00057']):print(v)
if __name__=='__main__':main()
