"""Move terminal T-dagger gates on data to chosen ticks (1q op into a tick where the qubit is idle)."""
import sys, json, shutil
sys.path.insert(0, '.')
from qedit import load
def build(src, out, moves):
    c = load(src)
    for q, t2 in moves:
        hits = c.find(lambda g: g[0] == f"tdg q[{q}];")
        assert len(hits) == 1, (q, hits)
        t, j = hits[0]
        assert q not in c.qubits_at(t2), (q, t2)
        c.move(t, j, t2)
    open(out + '.qasm', 'w').write(c.text())
    shutil.copy(src + '.json', out + '.json')
if __name__ == '__main__':
    moves = [tuple(map(int, m.split(':'))) for m in sys.argv[3:]]
    build(sys.argv[1], sys.argv[2], moves)
