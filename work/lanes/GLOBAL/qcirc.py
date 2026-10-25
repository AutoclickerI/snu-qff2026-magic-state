"""Layered-QASM circuit model for the T14 lane.

A circuit is a list of native units: dict(k=kind, q=(qubits), t=step, b=record bit or None, tag=str).
Kinds: R, RX, M, MX, CX, T, TDG.  RX = reset+h, MX = h+measure(+h).  Emission writes one full barrier
per native step, so the judge's ASAP schedule reproduces the steps exactly when every qubit has at most
one unit per step and no idle-only reordering is needed.
"""
import re, json
from pathlib import Path

ALL_BARRIER = None


def parse(text):
    """Units with their native step, from a v36c-style layered QASM (one full barrier per step)."""
    lines = [l.strip() for l in text.splitlines()]
    units, dets, step = [], [], 0
    i = 0
    body = []
    for l in lines:
        if not l or l.startswith(('OPENQASM', 'include', 'qreg', 'creg')):
            continue
        if l.startswith('// DETECTOR'):
            dets.append(sorted(set(map(int, re.findall(r'c\[(\d+)\]', l)))))
            continue
        if l.startswith('//'):
            continue
        body.append(l)
    pending_h = {}  # qubit -> index in units of an RX/MX awaiting fold, or a bare h
    n = len(body)
    while i < n:
        l = body[i]
        if l.startswith('barrier'):
            step += 1; i += 1; continue
        name = l.split()[0]
        qs = tuple(map(int, re.findall(r'q\[(\d+)\]', l)))
        bits = list(map(int, re.findall(r'c\[(\d+)\]', l)))
        if name == 'reset':
            if i + 1 < n and body[i + 1] == f'h q[{qs[0]}];':
                units.append(dict(k='RX', q=qs, t=step, b=None)); i += 2; continue
            units.append(dict(k='R', q=qs, t=step, b=None)); i += 1; continue
        if name == 'h':
            q = qs[0]
            if i + 1 < n and body[i + 1].startswith(f'measure q[{q}] '):
                b = int(re.findall(r'c\[(\d+)\]', body[i + 1])[0])
                j = i + 2
                if j < n and body[j] == f'h q[{q}];':
                    j += 1
                units.append(dict(k='MX', q=(q,), t=step, b=b)); i = j; continue
            raise ValueError(('bare h', i, l))
        if name == 'measure':
            units.append(dict(k='M', q=qs, t=step, b=bits[0])); i += 1; continue
        if name in ('cx', 't', 'tdg'):
            units.append(dict(k={'cx': 'CX', 't': 'T', 'tdg': 'TDG'}[name], q=qs, t=step, b=None)); i += 1; continue
        raise ValueError(l)
    return units, dets


def emit(units, dets, nbits=None, used=None):
    """Layered QASM text: one full barrier (over every used qubit) between consecutive steps."""
    units = sorted(units, key=lambda u: u['t'])
    if used is None:
        used = sorted({q for u in units for q in u['q']})
    bar = 'barrier ' + ','.join(f'q[{q}]' for q in used) + ';'
    if nbits is None:
        nbits = max([u['b'] for u in units if u['b'] is not None] + [0]) + 1
    out = ['OPENQASM 2.0;', 'include "qelib1.inc";', 'qreg q[36];', f'creg c[{nbits}];']
    T = max(u['t'] for u in units)
    by = {}
    for u in units:
        by.setdefault(u['t'], []).append(u)
    for t in range(T + 1):
        seen = set()
        for u in by.get(t, []):
            for q in u['q']:
                assert q not in seen, ('two units on a qubit in one step', t, q)
                seen.add(q)
            k, qs = u['k'], u['q']
            if k == 'R': out.append(f'reset q[{qs[0]}];')
            elif k == 'RX': out += [f'reset q[{qs[0]}];', f'h q[{qs[0]}];']
            elif k == 'M': out.append(f'measure q[{qs[0]}] -> c[{u["b"]}];')
            elif k == 'MX':
                out += [f'h q[{qs[0]}];', f'measure q[{qs[0]}] -> c[{u["b"]}];', f'h q[{qs[0]}];']
            elif k == 'CX': out.append(f'cx q[{qs[0]}],q[{qs[1]}];')
            elif k == 'T': out.append(f't q[{qs[0]}];')
            elif k == 'TDG': out.append(f'tdg q[{qs[0]}];')
            else: raise ValueError(k)
        if t < T:
            out.append(bar)
    for d in dets:
        out.append('// DETECTOR ' + ' '.join(f'c[{b}]' for b in d))
    return '\n'.join(out) + '\n'


def adjacent(a, b):
    return abs(a // 6 - b // 6) + abs(a % 6 - b % 6) == 1


def save(stem, units, dets, data_qubits, meta=None, nbits=None):
    stem = Path(stem)
    stem.with_suffix('.qasm').write_text(emit(units, dets, nbits))
    m = dict(data_qubits=list(data_qubits))
    cx = sum(1 for u in units if u['k'] == 'CX')
    m.update(cx=cx, native_depth=max(u['t'] for u in units) + 1)
    if meta: m.update(meta)
    stem.with_suffix('.json').write_text(json.dumps(m, indent=2) + '\n')
    return stem
