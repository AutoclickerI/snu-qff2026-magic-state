"""A bipartite grid star gives a triangle graph state after Y measurement.
Endpoint identity only; no full7-qubit target or performance improvement.
"""
from pathlib import Path
import json,hashlib,sys
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector,Pauli

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'audit/review6_validation/official'))
from tprep.qasm import to_stim
from tprep.noise import schedule,apply_noise
import xtim

def main():
    # Compact simulation indexing: center0, leaves1/2/3.
    star=QuantumCircuit(4);star.h(range(4))
    for leaf in[1,2,3]:star.cz(0,leaf)
    star.sdg(0);star.h(0) # Z measurement now is originalY.
    psi=Statevector.from_instruction(star).data
    triangle=QuantumCircuit(3);triangle.h(range(3))
    for a,b in[(0,1),(0,2),(1,2)]:triangle.cz(a,b)
    target=Statevector.from_instruction(triangle)
    rows=[]
    for outcome in[0,1]:
        branch=psi[outcome::2];prob=float(np.vdot(branch,branch).real)
        branch=Statevector(branch/np.sqrt(prob))
        correction=QuantumCircuit(3);correction.sdg(range(3))
        if outcome:correction.z(range(3))
        fixed=branch.evolve(correction)
        fidelity=float(abs(np.vdot(target.data,fixed.data))**2)
        stabilizers=[float(fixed.expectation_value(Pauli(p)).real)for p in['ZZX','ZXZ','XZZ']]
        assert abs(prob-.5)<1e-12 and fidelity>1-1e-12
        assert all(abs(v-1)<1e-12 for v in stabilizers)
        rows.append(dict(measurement_bit=outcome,probability=prob,
            raw_leaf_state='S^tensor3 * (Z1 Z6 Z8)^m |triangle>, up to global phase',
            fixed_leaf_Clifford='Sdg on1,6,8',pauli_byproduct='Z on1,6,8'if outcome else'identity',
            recovered_triangle_fidelity=fidelity,triangle_stabilizer_expectations=stabilizers))
    qasm='OPENQASM 2.0;\ninclude "qelib1.inc";\nqreg q[36];\ncreg c[1];\n'
    for q in[7,1,6,8]:qasm+=f'reset q[{q}];\nh q[{q}];\n'
    for q in[1,6,8]:qasm+=f'h q[{q}];\ncx q[7],q[{q}];\nh q[{q}];\n'
    qasm+='sdg q[7];\nh q[7];\nmeasure q[7] -> c[0];\n'
    for q in[1,6,8]:qasm+=f'sdg q[{q}];\n'
    qasm+='// Endpoint on [1,6,8]: (Z1 Z6 Z8)^c[0] |triangle>.\n'
    qasm+='// This is an endpoint certificate, not a7-qubit competition submission.\n'
    path=HERE/'grid_star_to_triangle.qasm';path.write_text(qasm)
    native,errors=to_stim(qasm);assert not errors,errors
    prog,steps,gaps=schedule(native)
    diagnose=xtim.diagnose(xtim.Circuit(apply_noise(native,0)))
    out=dict(scope=__doc__,official_commit='76fe47c0324f1c1f8b72a7d55af200e88043b522',
      center=7,leaves=[1,6,8],physical_graph_edges=[[7,1],[7,6],[7,8]],
      effective_graph_edges=[[1,6],[1,8],[6,8]],
      input_graph_bipartite=True,effective_triangle_bipartite=False,
      format_errors=errors,xtim_class_passed=True,
      qasm_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
      native_depth=max(t for ss in steps for _,t in ss)+1,
      native_CX=sum(i.name=='CX'for i in prog),branch_certificates=rows,
      limitations=['All physical gate,preparation,readout andidle noise must be priced in a real candidate.',
        'The fixed localSdg may be compiled into downstream operations; it is not an uncharged gate.',
        'The measurement-dependentZ byproduct must be propagated into legal record/frame handling; no conditional quantum gate is emitted.',
        'A direct interaction-graph embedding no-go remains valid for the direct model; this uses a different measurement-based construction.',
        'No claim of seven-qubit target correctness, single-fault safety or lower finite-noise loss.'])
    (HERE/'grid_star_to_triangle.json').write_text(json.dumps(out,indent=2)+'\n')
    (HERE/'grid_star_to_triangle.native.stim').write_text(native)
    print(json.dumps(out,indent=2))

if __name__=='__main__':main()
