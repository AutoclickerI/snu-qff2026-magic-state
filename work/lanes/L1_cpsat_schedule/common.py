"""Lane-local imports and serialization; run with PYTHONDONTWRITEBYTECODE=1."""
import ast
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORK = HERE.parent.parent
sys.path.insert(0, str(WORK))
os.chdir(HERE)
import gen2_cycle as g2
import proxy2
from qcirc import Circ
from tprep.noise import STANDARD, apply_noise
from tprep.qasm import to_stim

EXTRAS = ['t1c13', 't2c42']
BASE = WORK / 'gen2_t1c13+t2c42_8_1792739653.json'

def decode(row):
    def key(k):
        t, d, typ = k
        return (int(t), d, ast.literal_eval(typ) if d == 'A' else typ) if d in ('U', 'A') else (int(t), ast.literal_eval(d), typ)
    return {key(k): int(v) for k, v in row[1]}, list(row[2])

def encode(value, a, o, label=0):
    return [value, [[list(map(str, k)), a[k]] for k in g2.Model(EXTRAS).keys], list(o), label, EXTRAS]

def baseline():
    return decode(json.loads(BASE.read_text())[0])

def cycle(a, o):
    m = g2.Model(EXTRAS)
    c = Circ(); c.g('id', *proxy2.DATA); m.emit(c, a, o)
    bit_check = {b: t if B == 'X' else 3+t for (t, B), bits in m.checks.items() for b in bits}
    c.detectors = []; c = c.rescheduled(lazy_init=True)
    s, err = to_stim(c.text()); assert not err, err
    bits = [b for kind, qs, b in c.sops if kind in ('M', 'MX')]
    noisy = apply_noise(s, 1e-3, STANDARD)
    return c, s, m._full(noisy, bits, bit_check, 'X'), m._full(noisy, bits, bit_check, 'Z')

def save(path, obj):
    def convert(value):
        if hasattr(value, 'item'): return value.item()
        raise TypeError(type(value).__name__)
    path=Path(path)
    tmp=path.with_name(path.name+f'.{os.getpid()}.tmp')
    tmp.write_text(json.dumps(obj, indent=2, default=convert)+'\n')
    tmp.replace(path)
