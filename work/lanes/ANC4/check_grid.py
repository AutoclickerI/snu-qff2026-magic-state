import os,sys,json,dataclasses
sys.dont_write_bytecode=True
from pathlib import Path
ROOT=Path('/home/jihoon/competitions/quantumn');HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'upstream/snu-qff2026-problem'));import tprep
assert os.getloadavg()[0]<os.cpu_count()-2
for arg in sys.argv[1:]:
 p=Path(arg);j=json.loads(p.with_suffix('.json').read_text());r=tprep.check(p.read_text(),j['data_qubits'],shots=10**6,seed=0)
 print(p.name,r,flush=True)
 d=dataclasses.asdict(r) if dataclasses.is_dataclass(r) else vars(r)
 p.with_suffix('.check.json').write_text(json.dumps(d,indent=2,default=str)+'\n')
