"""Reproduce coverage/selection restrictions in the pinned public ST2 source.
These are certificates about committed legacy functions, not the unpublished live engine.
"""
import ast
import json
import re
from pathlib import Path
from types import SimpleNamespace

HERE=Path(__file__).resolve().parent
source=(HERE/"source/population.py").read_text()
tree=ast.parse(source)
def extract_function(name):
    node=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name==name)
    return compile(ast.fix_missing_locations(ast.Module(body=[node],type_ignores=[])),str(HERE/"source/population.py"),"exec")

def offered(*args):
    for i in range(100):
        yield {"index":i},{"index":i}
empty=lambda *args: iter(())
M=SimpleNamespace(timing_moves=offered,init_moves=empty,commute_moves=empty,phase_moves=empty,readout_moves=empty)
env={"M":M}
exec(extract_function("move_pool"),env)
pool=env["move_pool"]({})
coverage=[x[0]["index"] for x in pool]
assert coverage==list(range(48))
def fail_after_ten(*args):
    for i in range(10):
        yield {"index":i},{"index":i}
    raise RuntimeError("controlled generator failure")
M.timing_moves=fail_after_ten
after_error=env["move_pool"]({})
assert not after_error

env2={}
exec(extract_function("pareto"),env2)
main=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=="main")
loop=next(x for x in main.body if isinstance(x,ast.For) and isinstance(x.target,ast.Name) and x.target.id=="gen")
body=loop.body
start=next(i for i,n in enumerate(body) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=="front" for t in n.targets))
end=next(i for i,n in enumerate(body[start:],start) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=="chosen" for t in n.targets) and isinstance(n.value,ast.Subscript))
rows=[{"ok":True,"second":1e-5+i*1e-7,"exp_minus_A1":.501+i*.001,"nchars":100,"index":i} for i in range(20)]
class LastThree:
    def sample(self,rows,n):
        return rows[-n:]
env2.update(results=rows,args=SimpleNamespace(population=12),rng=LastThree())
exec(compile(ast.fix_missing_locations(ast.Module(body=body[start:end+1],type_ignores=[])),"<actual survivor selection>","exec"),env2)
selected=[r["index"] for r in env2["chosen"]]
assert selected==list(range(12))
qasm=(HERE/"inputs/v36a.qasm").read_text()
refs=[int(x) for line in qasm.splitlines() if not line.strip().startswith("creg ") for x in re.findall(r"c\[(\d+)\]",line)]
assert max(refs)==278
from qiskit import qasm2
qasm2.loads(qasm,custom_instructions=qasm2.LEGACY_CUSTOM_INSTRUCTIONS)
error=None
try:
    qasm2.loads(qasm.replace("creg c[279];","creg c[256];"),custom_instructions=qasm2.LEGACY_CUSTOM_INSTRUCTIONS)
except Exception as e:
    error=str(e)
assert error and "out-of-range" in error
result={
 "source_commit":"e438fb60c3da53584fc336fda76bd1fe46a5a6e2",
 "scope":"Pinned public legacy code only; live pop35/knapsack engine not available in this snapshot",
 "offered_moves":100,"reachable_indices":coverage,"unreachable_indices":list(range(48,100)),
 "valid_yields_before_error":10,"retained_after_generator_error":len(after_error),
 "population_size":12,"selected":selected,"requested_random_survivors":[17,18,19],
 "new_random_survivors_retained":0,"highest_acceptance_survives":19 in selected,
 "v36a_declared_classical_size":279,"v36a_max_referenced_index":278,
 "forced_classical_size":256,"parser_error":error
}
(HERE/"search_reachability_certificate.json").write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps(result,indent=2))
