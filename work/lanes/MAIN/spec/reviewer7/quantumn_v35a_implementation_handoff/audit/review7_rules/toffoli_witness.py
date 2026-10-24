"""Legal noisy quantum computation of a nonlinear acceptance predicate.

Not an optimization candidate. No ccx/ccz/custom gate is submitted. A full
CCX is emitted as CX/H/T/TDG on the line33--34--35, followed by a single
affine POSTSELECT on its output. Two measured fair control bits give3/4
ideal acceptance. Official target preparation is on disjoint physical sites.
"""
from pathlib import Path
import dataclasses,hashlib,json,math,sys,time
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'audit/review6_validation/official'))
import tprep
from tprep.qasm import to_stim
from tprep.noise import schedule

DATA=[0,6,13,2,7,8,1]
PHYS=[33,34,35]

def ccz_gates():
    # 4abc = a+b+c-(a^b)-(a^c)-(b^c)+(a^b^c) modulo8.
    gates=[('t',(0,)),('t',(1,)),('t',(2,))]
    for c,t in [(0,1),(1,2)]:
        gates += [('cx',(c,t)),('tdg',(t,)),('cx',(c,t))]
    bridge=[('cx',(0,1)),('cx',(1,2)),('cx',(0,1)),('cx',(1,2))]
    gates += bridge+[('tdg',(2,))]+list(reversed(bridge))
    gates += [('cx',(0,1)),('cx',(1,2)),('t',(2,)),('cx',(1,2)),('cx',(0,1))]
    return gates

def main(suffix=''):
    gates=[('h',(2,))]+ccz_gates()+[('h',(2,))]
    qc=QuantumCircuit(3)
    for g,qs in gates:getattr(qc,g)(*qs)
    ref=QuantumCircuit(3);ref.ccx(0,1,2)
    difference=float(np.max(np.abs(Operator(qc).data-Operator(ref).data)))
    assert difference<1e-12

    base=(HERE/'official/examples/injection.qasm').read_text()
    base=base.replace('qreg q[36];','qreg q[36];\ncreg c[3];')
    helpers='h q[33];\nmeasure q[33] -> c[0];\nh q[34];\nmeasure q[34] -> c[1];\n'
    for g,qs in gates:
        helpers+=g+' '+','.join(f'q[{PHYS[q]}]'for q in qs)+';\n'
    helpers+='measure q[35] -> c[2];\n'
    text=base.replace('creg c[3];','creg c[3];\n'+helpers)
    text+='// POSTSELECT(0) c[2]\n// FRAME_X(0)\n// FRAME_Z(0)\n'
    path=HERE/f'nonlinear_AND_postselection{suffix}.qasm';path.write_text(text)
    native,errors=to_stim(text)
    assert not errors,errors
    prog,steps,gaps=schedule(native)
    start=time.perf_counter();report=tprep.check(text,DATA,shots=10000,seed=0)
    gates_report={k:getattr(report,k)for k in ['format_ok','class_ok','correct_ok','acceptance_ok','passed']}
    out=dict(scope=__doc__,official_commit='76fe47c0324f1c1f8b72a7d55af200e88043b522',
      qasm_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),data_qubits=DATA,
      helper_physical_sites=PHYS,decomposed_CCX_CX=sum(g=='cx'for g,_ in gates),
      decomposed_CCX_T_TDG=sum(g in ['t','tdg']for g,_ in gates),
      ccx_operator_max_absolute_difference=difference,
      ideal_selected_control_assignments=[[0,0],[0,1],[1,0]],
      ideal_acceptance=0.75,
      gates=gates_report,seconds=time.perf_counter()-start,
      native_depth=max(t for group in steps for _,t in group)+1,
      report=dataclasses.asdict(report),
      limitations=['No loss-improvement claim: this computes an unrelated toy predicate.',
      'Real syndrome bits must be physically retained/recreated and routed; ordinary classical if is still prohibited.',
      'All emitted gates and idles are noisy in the official check.',
      'This disjoint witness does not prove class compatibility for a predicate entangled with an existing magic-state circuit.',
      'Nonlinear acceptance can be physically realized; the declarations themselves remain affine XOR.'])
    (HERE/f'nonlinear_AND_postselection{suffix}.json').write_text(json.dumps(out,indent=2,default=str)+'\n')
    (HERE/f'nonlinear_AND_postselection{suffix}.native.stim').write_text(native)
    print(json.dumps({k:out[k]for k in ['gates','decomposed_CCX_CX','decomposed_CCX_T_TDG','native_depth','ccx_operator_max_absolute_difference','seconds']},indent=2))
    print(json.dumps({k:out['report'][k]for k in ['class_error','correctness_errors','ideal_acceptance','acceptance','score','frame']},indent=2))
    assert report.passed
    assert abs(report.ideal_acceptance-.75)<1e-12

if __name__=='__main__':main()
