"""Check the last-arriving v36b reorder against the pinned physical schedule."""
from pathlib import Path
from collections import Counter, defaultdict
import json
import re
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'official'))
from tprep.qasm import to_stim
from tprep.noise import schedule

BASE='quantumn_review10/work/lanes/MAIN/v36b.qasm'
CAND='latest_update/work/submissions/v36b_r580.qasm'

def partial_order(path):
    wires=defaultdict(list);directives=[];other=[]
    for raw in path.read_text().splitlines():
        line=re.sub(r'\s+','',raw)
        if not line:continue
        if line.startswith('//'):
            if any(k in line for k in ['DETECTOR','POSTSELECT','FRAME','OBSERVABLE']):
                directives.append(line)
            continue
        if line.startswith(('OPENQASM','include','qreg','creg')):
            other.append(line);continue
        qs=[int(q) for q in re.findall(r'q\[(\d+)\]',line)]
        if not qs:other.append(line)
        for q in qs:wires[q].append(line)
    return dict(wires),Counter(directives),Counter(other)

def native(path):
    program,errors=to_stim(path.read_text());assert not errors,errors
    _,steps,gaps=schedule(program)
    # Gap field zero is the serialized instruction insertion index. Physical
    # interval comparison uses qubit, start tick and duration, not that index.
    return (Counter((str(ins),tick) for group in steps for ins,tick in group),
            Counter(tuple(gap[1:]) for gap in gaps))

x,y=partial_order(ROOT/BASE),partial_order(ROOT/CAND)
nx,ny=native(ROOT/BASE),native(ROOT/CAND)
checks={
    'per_wire_instruction_sequences_equal':x[0]==y[0],
    'directive_multisets_equal':x[1]==y[1],
    'declarations_and_other_statements_equal':x[2]==y[2],
    'native_scheduled_instruction_multisets_equal':nx[0]==ny[0],
    'physical_idle_interval_multisets_equal':nx[1]==ny[1],
}
base_meta=json.loads((ROOT/BASE).with_suffix('.json').read_text())
cand_meta=json.loads((ROOT/CAND).with_suffix('.json').read_text())
checks['data_qubit_order_equal']=base_meta['data_qubits']==cand_meta['data_qubits']
receipt={
    'base':BASE,'candidate':CAND,
    'latest_commit':'e31cec14e20f5d9fec9da759ef0d61cd4a5358ab',
    'official_commit':'76fe47c0324f1c1f8b72a7d55af200e88043b522',
    'checks':checks,'passed':all(checks.values()),
    'scope':'QASM partial order and pinned official native operation/idle-interval equivalence. This is not a fresh expected-loss or Monte Carlo run.',
}
Path(__file__).with_name('reorder_equivalence.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
assert receipt['passed']
