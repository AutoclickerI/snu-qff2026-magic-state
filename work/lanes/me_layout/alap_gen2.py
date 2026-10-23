"""Pre-cycle ALAP (L5 greedy, reverse) applied to a gen2-format schedule built by batch_score.make.
Usage: python alap_gen2.py <gen2 json> <idx> <nseeds> <label>; scores cm0 and cm1 seeds 1..n at seed 0."""
import hashlib, json, os, sys
sys.path.insert(0, ".")
sys.path.insert(0, "/home/jihoon/competitions/quantumn/work")
import batch_score  # noqa: E402
from alap import emit, greedy, fast_check, tprep  # noqa: E402


def alap_of(c, seed, cm):
    split = next(i for i, op in enumerate(c.sops) if op[0] == "barrier")
    pre = c.sops[:split]
    ts = greedy(pre, seed, True, cm)
    used = sorted({q for k, qs, b in pre for q in qs})
    out = []
    for t in range(max(ts) + 1):
        out.extend(op for op, s in zip(pre, ts) if s == t)
        if t < max(ts):
            out.append(("barrier", tuple(used), None))
    return emit(out + c.sops[split:], c).rescheduled(lazy_init=True)


f, idx, n, label = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
c0, data = batch_score.make({"kind": "gen2", "file": f, "idx": idx})
os.makedirs("alapvar", exist_ok=True)
seen = set()
for s, cm in [(0, False)] + [(s, True) for s in range(1, n + 1)]:
    text = alap_of(c0, s, cm).text()
    h = hashlib.sha1(text.encode()).hexdigest()[:10]
    if h in seen:
        continue
    seen.add(h)
    rep = fast_check.check(text, data, shots=10**8, procs=int(os.environ.get("PROCS", 16)))
    open(f"alapvar/{h}.qasm", "w").write(text)
    json.dump({"data_qubits": data, "score": rep.score, "acceptance": rep.acceptance, "n_2q": rep.n_2q,
               "seed": s, "commute": cm, "src": f"{f}#{idx}", "label": label}, open(f"alapvar/{h}.json", "w"))
    print(f"{label} {h} s{s} cm{int(cm)} 1-F {rep.score:.5e} acc {rep.acceptance:.4f} 2q {rep.n_2q} pass {rep.passed}", flush=True)
