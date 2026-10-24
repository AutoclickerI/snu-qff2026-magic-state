import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_candidates as bc


def raw_prefix():
    lines = bc.V14.read_text().splitlines()
    return lines[:204]


def pattern_prefix(removed):
    out, bi = [], 0
    for s in raw_prefix():
        if s.startswith('barrier'):
            if bi not in removed:
                out.append(s)
            else:
                out.append('')
            bi += 1
        else:
            out.append(s)
    return '\n'.join(out) + '\n', bi


def main():
    jobs = {}
    _, nbar = pattern_prefix(set())
    jobs['compact_full'] = set()
    for k in range(1, nbar + 1):
        jobs[f'compact_dropfirst{k:02d}'] = set(range(k))
        jobs[f'compact_droplast{k:02d}'] = set(range(nbar - k, nbar))
    jobs['compact_dropeven'] = set(range(0, nbar, 2))
    jobs['compact_dropodd'] = set(range(1, nbar, 2))
    jobs['compact_dropedges'] = set(range(0, 8)) | set(range(nbar - 8, nbar))
    for name, rem in jobs.items():
        p = bc.write_prefix(name, pattern_prefix(rem)[0])
        bc.merge(name, p, compact=True)
        bc.measure_init(name)
    print('generated', len(jobs), 'barriers', nbar)


if __name__ == '__main__':
    main()
