from pathlib import Path
import sys
sys.path[:0]=[str(Path(__file__).resolve().parents[1]),str(Path(__file__).resolve().parents[1]/'v31')]
from common import *
from build import fix,bit,parity
import wide_moments
V=H/'v36'
def base():return json.loads((V/'base.plan.json').read_text())
def write(c,name,description):
 st=save(c,'v36/'+name);ev=exact2.Eval(st.with_suffix('.qasm').read_text(),c['meta']['data_qubits']);c1=float(ev.fp@ev.n_single)
 r=wide_moments.evaluate(ev)if abs(c1)<1e-12 else dict(c1=c1,invalid_cubic=True)
 r.update(description=description,sha256=hashlib.sha256(st.with_suffix('.qasm').read_bytes()).hexdigest());st.with_suffix('.screen.json').write_text(json.dumps(r,indent=2));print(name,json.dumps(r),flush=True);return st,r
if __name__=='__main__':write(base(),'base','Frozen v36a, exact QASM bytes and operation provenance from its SEPBC construction.')
