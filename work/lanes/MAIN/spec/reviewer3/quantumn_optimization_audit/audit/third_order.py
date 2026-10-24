"""Reproduce the repository's cubic objective on the bundled QASM candidates.

Uses the pinned repository's Eval and BCSYN2/moments.evaluate with the independent
Pauli frontend. Does not run the official Monte Carlo judge or submit anything.
"""
import ast
import collections
import itertools
import json
import math
import os
from pathlib import Path
import re
import sys
import time
import numpy as np
import full_single_audit as fa
from fresh_signature_width import parse_current

repo = Path(os.environ['QUANTUMN_REPO']).resolve()
stem = Path(sys.argv[1]).with_suffix('')
fa.DATA = json.loads(stem.with_suffix('.json').read_text())['data_qubits']
ops, dets = parse_current(stem.with_suffix('.qasm').read_text())
original_noise = fa.noise_blocks
fa.noise_blocks = lambda text, p, first_order=True: original_noise(text, p, first_order=False)
m = fa.make_model(ops, dets)
fa.noise_blocks = original_noise

path = repo / 'work/lanes/EVAL/exact2.py'
nodes = [n for n in ast.parse(path.read_text()).body
         if isinstance(n, (ast.ClassDef, ast.FunctionDef)) and n.name in {'Eval', 'qasm_lines'}]
ns = dict(np=np, re=re, Model=lambda *a, **k: m, Engine=fa.Engine)
exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), 'exec'), ns)
ev = ns['Eval']('', fa.DATA)

path = repo / 'work/lanes/BCSYN2/moments.py'
nodes = [n for n in ast.parse(path.read_text()).body
         if isinstance(n, ast.FunctionDef) and n.name == 'evaluate']
ns = dict(np=np, collections=collections, itertools=itertools, math=math,
          time=time, Basis=fa.ns['Basis'])
exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), 'exec'), ns)
out = ns['evaluate'](ev)
a0, n0 = ev.e.ntable(0, 0)
phi = ev.e.phi(0)
stabilizers = []
for x, z, c in m.gen_m:
    xb = ev.e.B.express(x)
    stabilizers.append(0.0 if xb is None else ev.e.expect(phi, (xb, ev.e._w(z), c)))
assert abs(a0 - 1) < 1e-10 and abs(n0[0]) < 1e-10
assert max(abs(v - 1) for v in stabilizers) < 1e-10
out.update(source=str(stem), channels=len(m.chans), components=len(m.faults),
           cx=sum(o.kind == 'CX' for o in ops),
           depth=max(t for row in m.steps for _, t in row) + 1,
           harmful_singles=int((ev.n_single > 1e-10).sum()),
           noiseless_acceptance=float(a0), noiseless_loss=float(n0[0]),
           noiseless_stabilizers=stabilizers)
print(json.dumps(out, indent=2))
