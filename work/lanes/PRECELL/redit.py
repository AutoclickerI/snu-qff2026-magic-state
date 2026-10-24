"""Segment-level edits of a full-barrier stem (one segment = one native tick).

Edit ops (python API):
  rm(c, t, text)            remove the op group at tick t whose joined lines contain `text` (exactly one match)
  add(c, t, lines)          append an op group at tick t
  rmdet(c, bit)             remove the singleton detector on c[bit] (fails if the bit is in a larger detector)
  adddet(c, bits)           append a detector
  newbit(c)                 next unused classical bit (creg grown on save)
  save(c, base, out, meta)  conflict check, write out.qasm/.json (json copied from base + meta)
"""
import sys, re, json
sys.path.insert(0, '/home/jihoon/competitions/quantumn/work/lanes/EARLY')
from qedit import load

QRE = re.compile(r"q\[(\d+)\]")
CRE = re.compile(r"c\[(\d+)\]")


def rm(c, t, text):
    hits = [j for j, g in enumerate(c.segs[t]) if text in ' '.join(g)]
    assert len(hits) == 1, (t, text, c.segs[t])
    return c.segs[t].pop(hits[0])


def add(c, t, lines):
    c.segs[t].append(list(lines))


def rmdet(c, bit):
    line = f'// DETECTOR c[{bit}]'
    assert line in c.dets, (bit, [d for d in c.dets if f'c[{bit}]' in d])
    c.dets.remove(line)


def adddet(c, bits):
    c.dets.append('// DETECTOR ' + ' '.join(f'c[{b}]' for b in bits))


def newbit(c):
    used = set()
    for seg in c.segs:
        for g in seg:
            for ln in g:
                used |= set(map(int, CRE.findall(ln)))
    for d in c.dets:
        used |= set(map(int, CRE.findall(d)))
    return max(used) + 1


def save(c, base, out, meta=None):
    for t in range(len(c.segs)):
        seen = set()
        for g in c.segs[t]:
            qs = set()
            for ln in g:
                qs |= set(map(int, QRE.findall(ln)))
            assert not (qs & seen), (t, g)
            seen |= qs
            for ln in g:
                if ln.startswith('cx'):
                    a, b = map(int, QRE.findall(ln))
                    if a < 36 and b < 36:
                        assert abs(a // 6 - b // 6) + abs(a % 6 - b % 6) == 1, ln
    hi = max([int(x) for seg in c.segs for g in seg for ln in g for x in CRE.findall(ln)] + [0])
    c.header = [h if not h.startswith('creg') else f'creg c[{hi + 1}];' for h in c.header]
    open(out + '.qasm', 'w').write(c.text())
    m = json.load(open(base + '.json'))
    m.pop('allorders', None); m.pop('allorders_acceptance', None)
    m['cx'] = sum(ln.startswith('cx') for seg in c.segs for g in seg for ln in g)
    if meta:
        m.update(meta)
    json.dump(m, open(out + '.json', 'w'), indent=1)
