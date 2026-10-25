"""Segment-level QASM editing for full-barrier circuits (one barrier-delimited segment = one native tick).

Circuit = header lines, list of segments (each a list of op-statement groups), detector lines.
An op group is the list of QASM lines of one native op (e.g. ['h q[8];','measure q[8] -> c[16];','h q[8];']).
"""
import re
from pathlib import Path

QRE = re.compile(r"q\[(\d+)\]")
CRE = re.compile(r"c\[(\d+)\]")


class Circ:
    def __init__(self, text):
        lines = text.splitlines()
        self.header, self.dets = [], []
        segs, cur = [], []
        self.barrier = None
        body = []
        for ln in lines:
            s = ln.strip()
            if s.startswith(("OPENQASM", "include", "qreg", "creg")):
                self.header.append(ln)
            elif s.startswith("// DETECTOR") or s.startswith("// FRAME") or s.startswith("// POSTSELECT"):
                self.dets.append(ln)
            elif s.startswith("barrier"):
                self.barrier = ln
                segs.append(cur)
                cur = []
            elif s:
                cur.append(ln)
        segs.append(cur)
        self.segs = [self.group(seg) for seg in segs]
        if not self.segs[-1]:
            self.segs.pop()

    @staticmethod
    def group(seg):
        """Fold h/measure/h, reset/h, h/measure into single op groups."""
        out, i = [], 0
        while i < len(seg):
            ln = seg[i]
            q = QRE.findall(ln)
            if ln.startswith("h ") and i + 1 < len(seg) and seg[i + 1].startswith("measure") and QRE.findall(seg[i + 1]) == q:
                g = [ln, seg[i + 1]]
                i += 2
                if i < len(seg) and seg[i].startswith("h ") and QRE.findall(seg[i]) == q:
                    g.append(seg[i]); i += 1
                out.append(g)
            elif ln.startswith("reset") and i + 1 < len(seg) and seg[i + 1].startswith("h ") and QRE.findall(seg[i + 1]) == q:
                out.append([ln, seg[i + 1]]); i += 2
            else:
                out.append([ln]); i += 1
        return out

    def text(self, used=None):
        qs = set()
        for seg in self.segs:
            for g in seg:
                for ln in g:
                    qs.update(map(int, QRE.findall(ln)))
        if used:
            qs |= set(used)
        bar = "barrier " + ",".join(f"q[{q}]" for q in sorted(qs)) + ";"
        out = list(self.header)
        for k, seg in enumerate(self.segs):
            for g in seg:
                out.extend(g)
            if k < len(self.segs) - 1:
                out.append(bar)
        out.extend(self.dets)
        return "\n".join(out) + "\n"

    def find(self, pred):
        return [(t, j) for t, seg in enumerate(self.segs) for j, g in enumerate(seg) if pred(g)]

    def qubits_at(self, t):
        qs = set()
        for g in self.segs[t]:
            for ln in g:
                qs.update(map(int, QRE.findall(ln)))
        return qs

    def move(self, t, j, t2):
        g = self.segs[t].pop(j)
        self.segs[t2].append(g)
        return g

    def max_creg(self):
        m = -1
        for seg in self.segs:
            for g in seg:
                for ln in g:
                    for c in CRE.findall(ln):
                        m = max(m, int(c))
        return m


def load(stem):
    return Circ(Path(stem + ".qasm").read_text())
