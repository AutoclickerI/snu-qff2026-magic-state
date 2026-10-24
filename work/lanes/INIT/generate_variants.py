#!/usr/bin/env python3
"""Generate INIT measurement/preparation/retention variants.

The generator deliberately emits only variants whose new X-preparation fold has
passed tprep's exact noiseless detector/correctness check.  Reset subsets and
retention subsets are emitted directly; the batch scorer records the exact
numbers for all of them.
"""
from __future__ import annotations

import json
import re
from itertools import combinations
from pathlib import Path

import tprep

ROOT = Path('/home/jihoon/competitions/quantumn')
HERE = ROOT / 'work/lanes/INIT'
SOURCES = {
    'v12': (ROOT / 'work/submissions/v12_L5lns12_r86.qasm',
            ROOT / 'work/submissions/v12_L5lns12_r86.json'),
    'cand14': (ROOT / 'work/lanes/ST_BC/cand14.qasm',
               ROOT / 'work/lanes/ST_BC/cand14.json'),
}

RESET_RE = re.compile(r'^\s*reset q\[(\d+)\];\s*$')
H_RE = re.compile(r'^\s*h q\[(\d+)\];\s*$')
MEAS_RE = re.compile(r'^\s*measure q\[(\d+)\] -> c\[(\d+)\];\s*$')
Q_RE = re.compile(r'q\[(\d+)\]')
CREG_RE = re.compile(r'^(\s*creg c\[)(\d+)(\];\s*)$')
DET_RE = re.compile(r'^(\s*//\s*DETECTOR\s+)(.*)$')
BIT_RE = re.compile(r'c\[(\d+)\]')


def ops(lines):
    """Return (line index, kind, qubits, classical bit) for real operations."""
    out = []
    for i, line in enumerate(lines):
        s = line.split('//', 1)[0].strip()
        if not s or s.startswith(('OPENQASM', 'include', 'qreg', 'creg')):
            continue
        m = MEAS_RE.match(s)
        if m:
            out.append((i, 'measure', (int(m.group(1)),), int(m.group(2))))
            continue
        name = s.split()[0]
        if name == 'barrier':
            continue
        qs = tuple(int(x) for x in Q_RE.findall(s))
        if qs:
            out.append((i, name, qs, None))
    return out


def max_bit(lines):
    vals = [int(x) for line in lines for x in BIT_RE.findall(line)]
    return max(vals, default=-1)


def creg_size(lines):
    for line in lines:
        m = CREG_RE.match(line)
        if m:
            return int(m.group(2))
    raise ValueError('missing creg c[...]')


def set_creg(lines, n):
    out = list(lines)
    for i, line in enumerate(out):
        m = CREG_RE.match(line)
        if m:
            out[i] = f'{m.group(1)}{n}{m.group(3)}'
            return out
    raise ValueError('missing creg c[...]')


def detector_lines(lines):
    return [i for i, line in enumerate(lines) if DET_RE.match(line)]


def first_reset_sites(lines):
    """First-use ordinary Z resets (not reset+h native RX)."""
    by_q = {}
    for i, kind, qs, _ in ops(lines):
        for q in qs:
            by_q.setdefault(q, []).append((i, kind))
    sites = []
    for q, seq in sorted(by_q.items()):
        if seq[0][1] != 'reset':
            continue
        if len(seq) > 1 and seq[1][1] == 'h':
            continue
        sites.append((q, seq[0][0]))
    return sites


def first_rx_sites(lines):
    """First-use reset+h pairs, represented by (q, reset line, h line)."""
    by_q = {}
    for i, kind, qs, _ in ops(lines):
        for q in qs:
            by_q.setdefault(q, []).append((i, kind))
    sites = []
    for q, seq in sorted(by_q.items()):
        if len(seq) > 1 and seq[0][1] == 'reset' and seq[1][1] == 'h':
            sites.append((q, seq[0][0], seq[1][0]))
    return sites


def retained_sites(lines):
    """X readouts whose later reset+h can be replaced by the retained |+/- state."""
    allops = ops(lines)
    by_q = {}
    for rec in allops:
        by_q.setdefault(rec[2][0], []).append(rec)
    sites = []
    for q, seq in sorted(by_q.items()):
        for k, (mi, kind, _, bit) in enumerate(seq):
            if kind != 'measure' or k == 0 or seq[k - 1][1] != 'h':
                continue
            # Find the first subsequent q operation.  It must be reset, and the
            # following q operation must be h (native RX in the source).
            if k + 1 >= len(seq) or seq[k + 1][1] != 'reset':
                continue
            ri = seq[k + 1][0]
            if k + 2 >= len(seq) or seq[k + 2][1] != 'h':
                continue
            hi = seq[k + 2][0]
            # This is an X readout only if its bit participates in a detector.
            if not any(f'c[{bit}]' in lines[di] for di in detector_lines(lines)):
                continue
            sites.append((q, mi, ri, hi, bit))
    return sites


def add_bit_to_detectors(lines, rec, detnos):
    out = list(lines)
    dset = set(detnos)
    k = 0
    for i, line in enumerate(out):
        m = DET_RE.match(line)
        if not m:
            continue
        if k in dset:
            body = m.group(2).rstrip()
            out[i] = f'{m.group(1)}{body} c[{rec}]'
        k += 1
    return out


def transform_reset(text, selected, name):
    lines = text.splitlines()
    sites = dict(first_reset_sites(lines))
    newbits = []
    nxt = max(max_bit(lines) + 1, creg_size(lines))
    for q in selected:
        i = sites[q]
        lines[i] = f'measure q[{q}] -> c[{nxt}];'
        newbits.append(nxt)
        nxt += 1
    lines = set_creg(lines, max(creg_size(text.splitlines()), nxt))
    # Each fresh Z measurement is noiselessly 0, so each new record is its own
    # deterministic postselection detector.
    lines.extend(f'// DETECTOR c[{b}]' for b in newbits)
    return '\n'.join(lines) + '\n', newbits


def transform_rx(text, site, folds, name):
    lines = text.splitlines()
    q, ri, hi = site
    nxt = max(max_bit(lines) + 1, creg_size(lines))
    # H;M;H is the native MX readout while retaining |+>/|-> for the next use.
    lines[ri] = f'h q[{q}];\nmeasure q[{q}] -> c[{nxt}];\nh q[{q}];'
    lines[hi] = ''
    lines = set_creg(lines, max(creg_size(text.splitlines()), nxt + 1))
    lines = add_bit_to_detectors(lines, nxt, folds)
    return '\n'.join(lines) + '\n', [nxt]


def transform_rx_many(text, sites, foldmap):
    lines = text.splitlines()
    nxt = max(max_bit(lines) + 1, creg_size(lines))
    for q, ri, hi in sites:
        lines[ri] = f'h q[{q}];\nmeasure q[{q}] -> c[{nxt}];\nh q[{q}];'
        lines[hi] = ''
        # Fold this new record into exactly the detector indices found by the
        # individual exact test.
        lines = add_bit_to_detectors(lines, nxt, foldmap[q])
        nxt += 1
    lines = set_creg(lines, max(creg_size(text.splitlines()), nxt))
    return '\n'.join(lines) + '\n'


def transform_retain(text, selected):
    lines = text.splitlines()
    for q, mi, ri, hi, bit in selected:
        lines[ri] = ''  # keep the existing h; measure; h sequence
    return '\n'.join(lines) + '\n'


def report_meta(source, text, data, kind, sites=None, folds=None):
    return {
        'data_qubits': data,
        'source': source,
        'variant': kind,
        'sites': sites or [],
        'folds': folds or {},
    }


def write(name, text, meta):
    (HERE / f'{name}.qasm').write_text(text)
    (HERE / f'{name}.json').write_text(json.dumps(meta, indent=2) + '\n')


def random_detectors(text, data):
    rep = tprep.check(text, data, shots=1, seed=0)
    # A candidate without folds is expected to fail only because a listed
    # detector is random.  Keep the exact detector IDs for the fold.
    s = ' '.join(rep.correctness_errors)
    stim_nums = [int(x) - 1 for x in re.findall(r'#(\d+)', s)]
    # tprep numbers detectors in the native Stim execution order.  QASM
    # comments are moved next to their last measurement by qasm.convert, so
    # map those native indices back to source-comment order before editing.
    from tprep.qasm import convert
    _, labels, errors = convert(text)
    native_to_source = [int(m.group(1)) - 1 for lab in labels
                        if (m := re.match(r'DETECTOR line (\d+)$', lab))]
    nums = [native_to_source[i] for i in stim_nums if 0 <= i < len(native_to_source)]
    return rep, sorted(set(nums))


def main():
    for target, (src, jf) in SOURCES.items():
        base = src.read_text()
        data = json.loads(jf.read_text())['data_qubits']
        blines = base.splitlines()
        rsites = first_reset_sites(blines)
        print(target, 'reset sites', rsites, flush=True)
        # Baseline is useful in the report and provides the reference metadata.
        write(f'{target}_base', base, report_meta(str(src), base, data, 'base'))

        # Every first-use Z-reset subset, including empty and full.
        qs = [q for q, _ in rsites]
        for mask in range(1 << len(qs)):
            sel = tuple(q for i, q in enumerate(qs) if (mask >> i) & 1)
            tag = 'r0' if not sel else 'r_' + '_'.join(f'q{q}' for q in sel)
            text, bits = transform_reset(base, sel, tag)
            write(f'{target}_{tag}', text,
                  report_meta(str(src), text, data, 'first_use_z_reset', list(sel), {'records': bits}))

        # Test every fresh RX site through exact determinism and emit only the
        # valid folded candidate.  This also classifies data/output RX sites as
        # invalid without any heuristic.
        rx = first_rx_sites(blines)
        valid = []
        invalid = []
        for q, ri, hi in rx:
            provisional, bits = transform_rx(base, (q, ri, hi), [], target)
            rep, dets = random_detectors(provisional, data)
            if dets:
                folded = add_bit_to_detectors(provisional.splitlines(), bits[0], dets)
                folded_text = '\n'.join(folded) + '\n'
            else:
                folded_text = provisional
            chk = tprep.check(folded_text, data, shots=1, seed=0)
            # At one shot a valid circuit can randomly reject; correctness is
            # the deterministic gate needed to classify the fold here.
            if chk.correct_ok:
                valid.append((q, ri, hi, dets))
                write(f'{target}_rx_q{q}', folded_text,
                      report_meta(str(src), folded_text, data, 'fresh_plus_to_mx', [q], {str(q): dets}))
            else:
                invalid.append({'q': q, 'random_detectors': dets, 'errors': chk.correctness_errors})
        # Combine every individually valid fresh RX fold.  Pauli byproducts are
        # linear, but still run the judge check in the batch verifier later.
        if valid:
            sites = [(q, ri, hi) for q, ri, hi, _ in valid]
            foldmap = {q: dets for q, _, _, dets in valid}
            text = transform_rx_many(base, sites, foldmap)
            write(f'{target}_rx_all', text,
                  report_meta(str(src), text, data, 'fresh_plus_to_mx_all', [q for q, _, _, _ in valid], {str(q): d for q, _, _, d in valid}))
        (HERE / f'{target}_rx_classification.json').write_text(json.dumps({'valid': [q for q, _, _, _ in valid], 'invalid': invalid}, indent=2) + '\n')

        # Retention candidates: all nonempty subsets, plus the combined winner.
        rets = retained_sites(blines)
        for mask in range(1, 1 << len(rets)):
            sel = [r for i, r in enumerate(rets) if (mask >> i) & 1]
            qs2 = [r[0] for r in sel]
            tag = 'ret_' + '_'.join(f'q{q}' for q in qs2)
            text = transform_retain(base, sel)
            write(f'{target}_{tag}', text,
                  report_meta(str(src), text, data, 'retained_x_measurement', qs2, {'records': [r[4] for r in sel]}))

        # A combined candidate that applies all three independent transforms is
        # made after screening: q16 is the known winner on v12, while the
        # batch scorer selects the best reset subset for each target and then
        # the best valid RX/retention combination is recorded separately.
        print(target, 'RX valid', [q for q, _, _, _ in valid], 'invalid', [x['q'] for x in invalid], 'retained', [r[0] for r in rets], flush=True)


if __name__ == '__main__':
    main()
