"""Hash-bound first-order acceptance audit for every full all-orders price."""
from core35 import *
from oracle_queue35 import capacity
import concurrent.futures,math

def one(stem):
    stem=Path(stem);sha=hashlib.sha256(stem.with_suffix('.qasm').read_bytes()).hexdigest();a=json.loads(stem.with_suffix('.allorders.json').read_text());assert a['qasm_sha256']==sha
    out=stem.with_suffix('.singles.json')
    if out.exists() and json.loads(out.read_text()).get('qasm_sha256')==sha:return json.loads(out.read_text())
    md=json.loads(stem.with_suffix('.json').read_text());ev=exact2.Eval(stem.with_suffix('.qasm').read_text(),md['data_qubits']);a0,n0=ev.e.ntable(0,0);assert abs(a0-1)<1e-10 and abs(n0[0])<1e-10
    A1=float(ev.fp@(1-ev.a_single));r=dict(stem=stem.name,qasm_sha256=sha,c1=float(ev.fp@ev.n_single),A1=A1,exp_minus_A1=math.exp(-A1),noise_channels=len(ev.m.chans),detectors=len(ev.m.proj_m),ideal_acceptance=a0,ideal_loss=float(n0[0]));out.write_text(json.dumps(r,indent=2));return r

if __name__=='__main__':
    capacity(4);stems=[Path(str(p).removesuffix('.allorders.json')) for p in (V/'finalists').glob('*.allorders.json')]
    with concurrent.futures.ProcessPoolExecutor(max_workers=4) as ex:rows=list(ex.map(one,stems))
    (V/'singles.audit.json').write_text(json.dumps(dict(status='PASS',rows=rows),indent=2));print('AUDITED',len(rows),flush=True)
