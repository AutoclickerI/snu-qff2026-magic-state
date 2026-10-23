"""Text-level retention of postselected MX states: for the last 'reset q; h q' of each Bell a-member (q1,q13,q9)
that follows a 'h q; measure q -> c[b]' of the same qubit, delete the reset/h and add 'h q' after the measure.
Usage: retain.py <in qasm> <mask 1..7> <out qasm>"""
import sys
def retain(text, mask):
    lines = text.split("\n")
    for bit, q in enumerate((1, 13, 9)):
        if not (mask >> bit) & 1: continue
        ri = max(i for i, l in enumerate(lines) if l is not None and l.strip() == f"reset q[{q}];" and lines[i + 1] is not None and lines[i + 1].strip() == f"h q[{q}];")
        mi = max(i for i in range(ri) if lines[i] is not None and lines[i].strip().startswith(f"measure q[{q}] ->"))
        assert lines[mi - 1] and lines[mi - 1].strip() == f"h q[{q}];", (q, lines[mi - 1])
        assert not any(lines[j] and f"q[{q}]" in lines[j] and not lines[j].startswith("barrier") for j in range(mi + 1, ri)), q
        lines[ri] = lines[ri + 1] = None
        lines[mi] = lines[mi] + f"\nh q[{q}];"
    return "\n".join(l for l in lines if l is not None)
if __name__ == "__main__":
    open(sys.argv[3], "w").write(retain(open(sys.argv[1]).read(), int(sys.argv[2])))
