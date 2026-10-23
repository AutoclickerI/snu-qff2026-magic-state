"""Full-circuit ALAP + official seed-0 score for plateau states. Usage: ev.py <states json> <lo> <hi> <seed lo> <seed hi> <out dir> [thr for fault_scan]"""
import hashlib, json, os, sys
sys.path.insert(0, "/home/jihoon/competitions/quantumn/work/lanes/me_layout")
sys.path.insert(0, "/home/jihoon/competitions/quantumn/work")
import tprep, fast_check
import run_moves as R
from verify import load_assign
from alap import alap_circuit
f, lo, hi, s0, s1, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), sys.argv[6]
procs = int(os.environ.get("PROCS", 16))
os.makedirs(out, exist_ok=True)
st = json.load(open(f))
seen = set()
for i in range(lo, min(hi, len(st))):
    cost, a, o, _, name = st[i]
    m = R.variant("A1" if name == "A1" else name)
    for s in range(s0, s1):
        for cm in (True, False):
            c, data = alap_circuit(m, load_assign(a), o, seed=s, can_commute=cm)
            text = c.text()
            h = hashlib.sha1(text.encode()).hexdigest()[:10]
            if h in seen or os.path.exists(f"{out}/{h}.json"):
                continue
            seen.add(h)
            rep = fast_check.check(text, data, shots=10**8, procs=procs)
            open(f"{out}/{h}.qasm", "w").write(text)
            json.dump({"data_qubits": data, "score": rep.score, "acceptance": rep.acceptance, "n_2q": rep.n_2q,
                       "passed": rep.passed, "state": i, "proxy": cost, "seed": s, "commute": cm, "src": f"{f}#{i}"},
                      open(f"{out}/{h}.json", "w"))
            print(f"{h} st{i} p{cost*1e4:.4f} s{s} cm{int(cm)} {rep.score:.5e} acc {rep.acceptance:.4f} 2q {rep.n_2q} pass {rep.passed}", flush=True)
