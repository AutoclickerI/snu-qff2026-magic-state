import sys,os,json
from pathlib import Path
sys.dont_write_bytecode=True
H=Path(__file__).resolve().parent;sys.path.insert(0,str(H.parent))
import prefixes as p
p.PD=[0,20,7,10,3,15,8]
d=p.extract('v30f')
from native import S,xtim
us=[S.Unit(o['lines'])for o in d['ops']];text=S.emit(d['head'],us,[o['asap']for o in d['ops']],d['detectors']);(H/'v30_prefix_only.qasm').write_text(text);(H/'v30_prefix_only.json').write_text(json.dumps(dict(data_qubits=d['data_qubits'])))
import tprep
r=tprep.check(text,d['data_qubits'],shots=1000,seed=0);(H/'v30_prefix_only.check.txt').write_text(str(r));assert r.passed,str(r)
for ext in ['qasm','json']:(H/('control_v30f.'+ext)).write_text((p.ROOT/'work/lanes/MAIN'/('v30f.'+ext)).read_text())
print(str(r))
