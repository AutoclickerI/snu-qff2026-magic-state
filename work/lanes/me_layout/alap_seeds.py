"""Randomized-priority ALAP variants of a gmodel result (schedules.greedy seed>0), official seed-0 score;
fault_scan only for those below a threshold. Usage: python alap_seeds.py <res json> <idx> <nseeds> <thresh>"""
import hashlib, json, os, sys
sys.path.insert(0, ".")
from alap import alap_circuit, R, load_assign, fast_check, tprep  # noqa: E402

f, idx, n, thr = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4])
cost, a, o, seed, name = json.load(open(f))[idx]
m = R.variant(name)
seen = set()
os.makedirs("alapvar", exist_ok=True)
S0 = int(os.environ.get("S0", 1))
for s in range(S0, S0 + n):
    for cm in ((True,) if os.environ.get("CMONLY") else (False, True)):
        c, data = alap_circuit(m, load_assign(a), o, seed=s, can_commute=cm)
        text = c.text()
        h = hashlib.sha1(text.encode()).hexdigest()[:10]
        if h in seen:
            continue
        seen.add(h)
        rep = fast_check.check(text, data, shots=10**8, procs=int(os.environ.get("PROCS", 20)))
        c1 = tprep.fault_scan(text, data).c1 if rep.passed and rep.score < thr else None
        open(f"alapvar/{h}.qasm", "w").write(text)
        json.dump({"data_qubits": data, "score": rep.score, "acceptance": rep.acceptance, "n_2q": rep.n_2q,
                   "c1": c1, "seed": s, "commute": cm, "src": f"{f}#{idx}"}, open(f"alapvar/{h}.json", "w"))
        print(f"{h} s{s} cm{int(cm)} 1-F {rep.score:.5e} acc {rep.acceptance:.4f} 2q {rep.n_2q} pass {rep.passed} c1 {c1}", flush=True)
