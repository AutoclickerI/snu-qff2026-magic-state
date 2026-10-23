"""ALAP (commute) variants of the Bell-delayed A1 optimum. Usage: ev2.py <res2 json> <idx> <bl list json> <seed lo> <seed hi> <out dir>"""
import hashlib, json, os, sys
sys.path.insert(0, "/home/jihoon/competitions/quantumn/work/lanes/me_layout"); sys.path.insert(0, "/home/jihoon/competitions/quantumn/work"); sys.path.insert(0, "/home/jihoon/competitions/quantumn/work/lanes/BP_push")
import tprep, fast_check, gmodel2 as G, run_moves as R
from verify import load_assign
from alap import alap_circuit
f, idx, bl, s0, s1, out = sys.argv[1], int(sys.argv[2]), json.loads(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), sys.argv[6]
os.makedirs(out, exist_ok=True)
m = R.variant("A1"); m.__class__ = G.GModel; m.bell_layer = {t: bl[t] for t in range(3)}
r = json.load(open(f))[idx]; A = load_assign(r[1]); o = r[2]
procs = int(os.environ.get("PROCS", 16)); seen = set()
for s in range(s0, s1):
    for cm in (True, False):
        c, data = alap_circuit(m, A, o, seed=s, can_commute=cm)
        text = c.text(); h = hashlib.sha1(text.encode()).hexdigest()[:10]
        if h in seen: continue
        seen.add(h)
        rep = fast_check.check(text, data, shots=10**8, procs=procs)
        open(f"{out}/{h}.qasm", "w").write(text)
        json.dump({"data_qubits": data, "score": rep.score, "acceptance": rep.acceptance, "n_2q": rep.n_2q, "passed": rep.passed, "seed": s, "commute": cm, "bl": bl, "src": f"{f}#{idx}"}, open(f"{out}/{h}.json", "w"))
        print(f"{h} s{s} cm{int(cm)} {rep.score:.5e} acc {rep.acceptance:.4f} 2q {rep.n_2q} pass {rep.passed}", flush=True)
