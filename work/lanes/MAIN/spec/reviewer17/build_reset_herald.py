#!/usr/bin/env python3
"""Move one R to the previous free tick, add a checked MZ at its old tick.

This is a native circuit edit; it does not delete or weaken noise.
The input must use explicit all-used-qubit barrier layers, as v37f does.
"""
import argparse
import json
from pathlib import Path
import re


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('input_qasm', type=Path)
    ap.add_argument('output_qasm', type=Path)
    ap.add_argument('--qubit', type=int, default=17)
    ap.add_argument('--tick', type=int, default=30, help='Zero-indexed original reset tick')
    args = ap.parse_args()
    assert args.tick > 0
    lines = args.input_qasm.read_text().splitlines()
    tick = 0
    occupied = set()
    creg_size = None
    for line in lines:
        if line.startswith('barrier'):
            tick += 1
        elif not line.startswith(('//', 'qreg', 'creg', 'OPENQASM', 'include')):
            occupied.update((tick, int(q)) for q in re.findall(r'q\[(\d+)\]', line))
        match = re.fullmatch(r'creg c\[(\d+)\];', line)
        if match:
            creg_size = int(match[1])
    assert creg_size is not None
    assert (args.tick - 1, args.qubit) not in occupied, 'Previous tick is occupied'
    tick = 0
    changed = 0
    emitted_reset = 0
    out = []
    for line in lines:
        if line.startswith('barrier'):
            if tick == args.tick - 1:
                out.append(f'reset q[{args.qubit}];')
                emitted_reset += 1
            tick += 1
        if tick == args.tick and line.strip() == f'reset q[{args.qubit}];':
            line = f'measure q[{args.qubit}] -> c[{creg_size}];'
            changed += 1
        if re.fullmatch(r'creg c\[\d+\];', line):
            line = f'creg c[{creg_size + 1}];'
        out.append(line)
    assert changed == 1 and emitted_reset == 1
    out.append(f'// DETECTOR c[{creg_size}]')
    args.output_qasm.parent.mkdir(parents=True, exist_ok=True)
    args.output_qasm.write_text('\n'.join(out) + '\n')
    metadata = json.loads(args.input_qasm.with_suffix('.json').read_text())
    args.output_qasm.with_suffix('.json').write_text(json.dumps({
        'data_qubits': metadata['data_qubits'],
        'change': {'reset_qubit': args.qubit, 'old_reset_tick': args.tick,
                   'new_reset_tick': args.tick - 1, 'new_measure_tick': args.tick,
                   'new_detector_record': creg_size},
        'official_judge_run': False,
    }, indent=2) + '\n')


if __name__ == '__main__':
    main()
