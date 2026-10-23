from qiskit import QuantumCircuit, transpile
from qiskit.transpiler import CouplingMap
import tprep, json, os

OUT='/home/jihoon/competitions/quantumn/work/codex'
N=36
# physical grid coupling directed both ways
edges=[]
for r in range(6):
    for c in range(6):
        q=6*r+c
        if c<5: edges += [(q,q+1),(q+1,q)]
        if r<5: edges += [(q,q+6),(q+6,q)]
cm=CouplingMap(edges)
# qreg full chip, c bits for checks / logical outcomes
nclass=32
qc=QuantumCircuit(N,nclass)
data=list(range(7))
cat1=list(range(7,14))
cat2=list(range(14,21))
anc=list(range(21,34))
# logical |+_L> encoder (example's Clifford network, T removed)
for q in range(4): qc.h(q)
ops=[(0,4),(4,0),(0,4),(1,0),(1,5),(5,1),(1,5),(2,1),(4,5),(5,2),(2,4),(5,6),(4,3),(3,5),(5,4),(4,6),(6,3),(3,6),(6,3)]
for a,b in ops: qc.cx(a,b)
# verify data stabilizers, X checks via H conjugation, same anc q21 repeatedly
cidx=0
for kind in 'XZ':
    for support in tprep.grid.SUPPORTS:
        a=33
        qc.reset(a)
        if kind=='X':
            for i in support: qc.h(data[i])
        for i in support: qc.cx(data[i],a)
        qc.measure(a,cidx); cidx+=1
        if kind=='X':
            for i in support: qc.h(data[i])
# cat preparation + adjacent ZZ verification, one block helper
def prep_cat(cat, start_c):
    qc.reset(cat[0]); qc.h(cat[0])
    for q in cat[1:]: qc.reset(q)
    for a,b in zip(cat[:-1],cat[1:]): qc.cx(a,b)
    ci=start_c
    for a,b in zip(cat[:-1],cat[1:]):
        v=21+(ci-start_c) # distinct anc q21..q26 (reuse across blocks)
        qc.reset(v); qc.cx(a,v); qc.cx(b,v); qc.measure(v,ci); ci+=1
    return ci
# First cat, checks records 6..11
cidx=prep_cat(cat1,cidx)
# logical measurement block helper, using 7 X readouts; parity will frame Z
for q in data: qc.t(q)
for a,d in zip(cat1,data): qc.cx(a,d)
for q in data: qc.tdg(q)
for a in cat1:
    qc.h(a); qc.measure(a,cidx); cidx+=1
# Second cat checks records 19..24, then second logical measurement records 25..31
cidx=prep_cat(cat2,cidx)
for q in data: qc.t(q)
for a,d in zip(cat2,data): qc.cx(a,d)
for q in data: qc.tdg(q)
for a in cat2:
    qc.h(a); qc.measure(a,cidx); cidx+=1
assert cidx==nclass, cidx
# transpile to nearest-neighbor. Keep full physical qreg and identity initial layout.
tr=transpile(qc, basis_gates=['id','x','y','z','h','s','sdg','sx','sxdg','t','tdg','cx','reset','measure'], coupling_map=cm, initial_layout=list(range(N)), routing_method='sabre', optimization_level=3, seed_transpiler=11)
# final positions of original virtual data q0..q6
layout=tr.layout.final_index_layout()
data_phys=[layout[i] for i in data]
# classical directives: all stabilizer/cat verification outcomes deterministic 0. Their c bits correspond records in measurement order,
# but transpiler may reorder only qubits not classical bits.
detectors=[[tr.clbits[i]] for i in list(range(12)) + list(range(19,25))]
# logical parity records: first block c12..18, second c25..31
detectors.append([tr.clbits[i] for i in range(12,19)] + [tr.clbits[i] for i in range(25,32)])
frame={'X':(0,[]),'Z':(0,[tr.clbits[i] for i in range(12,19)])}
text=tprep.submission_text(tr,detectors=detectors,frame=frame)
open(os.path.join(OUT,'measurement.qasm'),'w').write(text)
# quick metadata
print('data_phys',data_phys,'ops',tr.count_ops(),'cidx',cidx,'layout',layout)
if __name__=='__main__':
    rep=tprep.check(text,data_phys,p=1e-3,shots=100000,seed=0)
    print(rep)
