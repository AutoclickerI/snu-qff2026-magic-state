#!/usr/bin/env python3
"""Reproduce scoped code-audit findings for quantumn commit 7f5a18cf.

No network, host access, submission, or repository mutation. The small metadata
probe writes only to a TemporaryDirectory. The optional baseline recomputation
uses the repository's NumPy evaluator; it is not an independent official judge.

Usage:
  OPENBLAS_NUM_THREADS=1 python quantumn_code_audit.py --output code_audit.json
  OPENBLAS_NUM_THREADS=1 python quantumn_code_audit.py --recompute-baseline
"""
from __future__ import annotations

import argparse
import ast
import contextlib
import hashlib
import io
import json
import sys
import tempfile
from pathlib import Path

COMMIT = "7f5a18cf386c850ad8a59e195edb14df087f6457"


def functions_from_source(path, names, namespace):
    """Execute only inspected function definitions, not module-level side effects."""
    tree = ast.parse(path.read_text())
    selected = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names]
    assert {n.name for n in selected} == set(names)
    exec(compile(ast.Module(body=selected, type_ignores=[]), str(path), "exec"), namespace)
    return namespace


def literal_assignments(path, names):
    out = {}
    for n in ast.parse(path.read_text()).body:
        if isinstance(n, ast.Assign):
            for target in n.targets:
                if isinstance(target, ast.Name) and target.id in names:
                    out[target.id] = ast.literal_eval(n.value)
    assert set(out) == set(names)
    return out


def ranking_probe(root):
    lane = root / "work/lanes/MERGE"
    ns = literal_assignments(lane / "campaign.py", {"TAU", "FLOOR"})
    functions_from_source(lane / "greedy_pass.py", {"choose", "eligible"}, ns)
    # These are synthetic feasible rows, not measured candidate circuits.
    rows = [
        {"name": "v37d_like", "loss": 3.676347e-5, "acceptance": .50235},
        {"name": "hypothetical_higher_acceptance", "loss": 3.678e-5, "acceptance": .52},
    ]
    for row in rows:
        row["J_tau"] = row["acceptance"] * (row["loss"] - ns["TAU"])
    chosen = ns["choose"](rows)
    correct = min(rows, key=lambda row: row["loss"])
    assert chosen["loss"] > correct["loss"]
    # Updating tau to the current ratio makes a non-improving row nonnegative.
    dynamic = dict(ns, TAU=correct["loss"])
    functions_from_source(lane / "greedy_pass.py", {"choose"}, dynamic)
    assert dynamic["choose"](rows)["name"] == correct["name"]
    single_loser = dict(loss=correct["loss"] + 1e-8, acceptance=correct["acceptance"])
    assert not ns["eligible"](single_loser, correct)
    return dict(
        evidence="synthetic counterexample executing the unmodified choose function",
        tau=ns["TAU"], floor=ns["FLOOR"], rows=rows,
        live_choose=chosen["name"], minimum_loss=correct["name"],
        excess_loss=chosen["loss"] - correct["loss"],
        dynamic_tau_choice=dynamic["choose"](rows)["name"],
        singleton_loser_removed_before_combinations=True,
        scope="Shows possible misranking; does not show that an archived physical candidate was missed.",
        source=["work/lanes/MERGE/campaign.py:10-11", "work/lanes/MERGE/greedy_pass.py:26-29,42,45-74", "work/lanes/MERGE/final_repair.py:29-41"],
    )


def metadata_probe(root):
    path = root / "work/lanes/MERGE/ev37.py"
    d1, d2 = [6, 20, 19, 10, 2, 22, 16], [20, 6, 19, 10, 2, 22, 16]
    with tempfile.TemporaryDirectory(prefix="quantumn_metadata_audit_") as td:
        ns = dict(D=d1, CDIR=Path(td), EVH="fixed", json=json, hashlib=hashlib)
        functions_from_source(path, {"sha_of", "key", "write_stem"}, ns)
        text = "OPENQASM 2.0;\nqreg q[36];\n"
        first = ns["write_stem"](text, d1)
        second = ns["write_stem"](text, d2)
        stored = json.loads(second.with_suffix(".json").read_text())["data_qubits"]
        keys_differ = ns["key"](ns["sha_of"](text), d1) != ns["key"](ns["sha_of"](text), d2)
        assert first == second and stored == d1 and keys_differ
    return dict(
        evidence="synthetic metadata counterexample executing unmodified key/write_stem functions",
        same_stem=True, requested_second_outputs=d2, stored_second_outputs=stored,
        cache_keys_differ=keys_differ,
        scope="Current fixed-output MERGE lane is not shown affected; this breaks variable-output reuse.",
        source=["work/lanes/MERGE/ev37.py:88-89,104-114", "work/lanes/MERGE/campaign.py:15-20"],
    )


def correctness_probe(root):
    sp = root / "work/lanes/MAIN/sparse"
    sys.path.insert(0, str(sp))
    import frontend as fa
    stem = sp.parent / "v37d"
    text = stem.with_suffix(".qasm").read_text()
    fa.DATA = json.loads(stem.with_suffix(".json").read_text())["data_qubits"]
    q = fa.DATA[0]
    barrier = next(line for line in text.splitlines() if line.startswith("barrier"))
    # H T^4 H = X exactly. The ideal judge corrects this physical X, but
    # the official noiseless correctness gate requires the output code space
    # BEFORE that correction. No official sampler is invoked in this probe.
    suffix = ("\n" + barrier + "\n").join([f"h q[{q}];"] + [f"t q[{q}];"] * 4 + [f"h q[{q}];"])
    rows = []
    for name, src in [("v37d", text), ("v37d_with_physical_X_on_one_output", text + "\n" + suffix + "\n")]:
        ops, dets = fa.parse_current(src)
        model = fa.make_model(ops, dets)
        eng = fa.Engine(model)
        state = eng.phi(0)
        stab = [eng.expect(state, (eng.B.express(x), eng._w(z), c)) for x, z, c in model.gen_m]
        acceptance, numerator = eng.ntable(0, 0)
        rows.append(dict(case=name, t_count=len(model.rots), ideal_acceptance=float(acceptance),
                         ideal_decoded_loss=float(numerator[0]), output_stabilizers=stab,
                         output_in_code_space=all(abs(v - 1) < 1e-10 for v in stab)))
    assert rows[0]["output_in_code_space"] and not rows[1]["output_in_code_space"]
    assert abs(rows[1]["ideal_decoded_loss"]) < 1e-10 and rows[1]["ideal_acceptance"] > 1 - 1e-10
    return dict(
        evidence="exact noiseless NumPy frontend calculation; official gate read from source",
        rows=rows,
        scope="Current v37d is valid in this check; this demonstrates a weaker search validity predicate.",
        source=["work/lanes/MAIN/sparse/sparse_walsh.py:101-107", "official tprep/exact.py:256-267"],
    )


def baseline(root, recompute):
    sp = root / "work/lanes/MAIN/sparse"
    path = sp / "v37d_canonical_sparse_result.json"
    if recompute or not path.exists():
        sys.path.insert(0, str(sp))
        import sparse_walsh as sw
        with contextlib.redirect_stdout(io.StringIO()):
            result = sw.run(sp.parent / "v37d", 72, True, 1)
    else:
        result = json.loads(path.read_text())
    assert abs(result["loss"] - 3.676346632406467e-5) < 2e-13
    assert abs(result["acceptance"] - .5023547642585299) < 2e-13
    names = ["loss", "acceptance", "channels", "factors", "conditioned_width", "seconds", "conditional_loss_kernel_omission_bound"]
    return dict(evidence="locally reproduced all-orders evaluator result; no official MC run", **{k: result[k] for k in names})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, default=Path(__file__).resolve().parent / "quantumn_snapshot")
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parent / "quantumn_code_audit_results.json")
    parser.add_argument("--recompute-baseline", action="store_true")
    args = parser.parse_args()
    root = args.snapshot.resolve()
    result = dict(commit=COMMIT, ranking=ranking_probe(root), metadata=metadata_probe(root),
                  correctness=correctness_probe(root), baseline=baseline(root, args.recompute_baseline))
    relevant = ["work/lanes/MERGE/greedy_pass.py", "work/lanes/MERGE/campaign.py", "work/lanes/MERGE/ev37.py", "work/lanes/MERGE/final_repair.py", "work/lanes/MAIN/sparse/frontend.py", "work/lanes/MAIN/sparse/sparse_walsh.py", "work/lanes/MAIN/v37d.qasm", "work/lanes/MAIN/v37d.json"]
    result["source_sha256"] = {p: hashlib.sha256((root / p).read_bytes()).hexdigest() for p in relevant}
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
