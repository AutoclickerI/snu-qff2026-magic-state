"""Full-circuit check of a run_moves result: correctness, fault_scan c1, official fast_check score.
Usage: python verify.py <res json> [n distinct] ; writes cand_<name>_<i>.qasm/.json for passing ones."""
import ast
import json
import sys

sys.path.insert(0, ".")
sys.path.insert(0, "/home/jihoon/competitions/quantumn/work")
import tprep  # noqa: E402
import fast_check  # noqa: E402
import run_moves as R  # noqa: E402


def load_assign(a):
    out = {}
    for k, L in a:
        k0, k1, k2 = k
        if k0 == "M":
            out[("M", int(k1), int(k2))] = L
        elif k1 == "U":
            out[(int(k0), "U", "")] = L
        elif k1 == "A":
            out[(int(k0), "A", ast.literal_eval(k2))] = L
        else:
            out[(int(k0), int(k1), k2)] = L
    return out


if __name__ == "__main__":
    f = sys.argv[1]
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    res = json.load(open(f))
    seen = set()
    for i, (cost, a, o, seed, name) in enumerate(res):
        if round(cost, 13) in seen:
            continue
        seen.add(round(cost, 13))
        if len(seen) > n:
            break
        m = R.variant(name)
        assign = load_assign(a)
        c, data = m.full_circuit(assign, o)
        text = c.text()
        sc = tprep.fault_scan(text, data)
        rep = fast_check.check(text, data, shots=10**8, procs=25)
        tag = f"cand_{name}_{i}"
        print(f"{tag}: proxy {cost:.4e}  official 1-F {rep.score:.5e} ± {rep.sem:.1e}  acc {rep.acceptance:.4f}  "
              f"2q {rep.n_2q}  passed {rep.passed}  c1 {sc.c1:.3g}", flush=True)
        if rep.passed:
            open(tag + ".qasm", "w").write(text)
            json.dump({"data_qubits": data, "score": rep.score, "sem": rep.sem, "acceptance": rep.acceptance,
                       "n_2q": rep.n_2q, "c1": sc.c1, "source": f"{f}#{i}"}, open(tag + ".json", "w"), indent=1)
