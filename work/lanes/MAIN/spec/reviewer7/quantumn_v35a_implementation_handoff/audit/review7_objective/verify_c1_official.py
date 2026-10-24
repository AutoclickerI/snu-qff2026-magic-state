"""Official admissibility and independent decoder check of the c1 counterexample.
Single injected error below is a diagnostic, not a submitted circuit/noise model.
"""
from pathlib import Path
import sys,json,hashlib,dataclasses,time
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'audit/review6_validation/official'))
import tprep
from tprep.qasm import to_stim
from tprep.exact import run
from tprep.grid import SUPPORTS
from tprep.parse import parse
src=HERE/'v31s_a_decode_no_detectors'
qasm=src.with_suffix('.qasm').read_text();data=json.loads(src.with_suffix('.json').read_text())['data_qubits']
t=time.perf_counter();report=tprep.check(qasm,data,shots=10000,seed=0)
out=dict(official_commit='76fe47c0324f1c1f8b72a7d55af200e88043b522',
         qasm_sha256=hashlib.sha256(qasm.encode()).hexdigest(),seconds=time.perf_counter()-t,
         report=dataclasses.asdict(report),gates={k:getattr(report,k)for k in ['format_ok','class_ok','correct_ok','acceptance_ok','passed']})
assert report.passed
native,errors=to_stim(qasm);assert not errors
prog=parse(native);assert prog[23].text=='CX 13 7',prog[23].text
lines=native.splitlines();line=prog[23].line_no
faulty='\n'.join(lines[:line]+['X 13']+lines[line:])+'\n'
state,inverse,records,detectors,wire=run(faulty,36)
def pauli(T,indices):
    p=state.stim.PauliString(state.n)
    for i in indices:p[wire[data[i]]]=T
    return p
gens=[pauli(P,sorted(s))for P in 'XZ' for s in SUPPORTS]
obs=0.0
for T in 'XY':
    L=pauli(T,range(7))
    for a in range(8):
        for b in range(8):
            w=sum(((-1)**(bool(s&7)+(bool(s>>3) if T=='Y' else 0))) *
                  (-1)**(((s&7)&a).bit_count()+((s>>3)&b).bit_count()) for s in range(64))/64
            if not w:continue
            P=L.copy()
            for j,g in enumerate(gens):
                if (a|(b<<3))>>j&1:P=P*g
            obs+=w*(1 if T=='X' else -1)*state.expectation(P,inverse)/2**.5
diagnostic_loss=(1-obs)/2
assert abs(diagnostic_loss-.25)<1e-12,diagnostic_loss
out['single_fault_diagnostic']=dict(injected_after='native CX13->7, index23',pauli='XI',
    decoded_loss=diagnostic_loss,method='Unmodified official exact.run; direct expansion of the actual decoder observable; no sampling.',
    scope='Single-location fault diagnostic, not a new official scoring noise model.')
(HERE/'c1_witness_official.json').write_text(json.dumps(out,indent=2,default=str)+'\n')
print(json.dumps(dict(gates=out['gates'],official_score=report.score,acceptance=report.acceptance,
                     diagnostic_loss=diagnostic_loss,seconds=out['seconds']),indent=2))
