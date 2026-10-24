"""Warm-start and LNS driver for the ST1 global placement object.

The model is imported read-only from ST1.  All receipts and witnesses are
written in FRESH.  A solver witness is copied as a complete assignment when
the model has the same encoder/resource family; otherwise only a compatibility
receipt is made and the resource is left out of that run.
"""
import argparse, json, pathlib, sys, time

ROOT = pathlib.Path(__file__).resolve().parents[3]
FRESH = ROOT / "work/lanes/FRESH"
ST1 = ROOT / "work/lanes/ST1"
sys.path.insert(0, str(ST1))
import redesign

# Keep the model's input root in ST1 while forcing all emitted artefacts to FRESH.
redesign.H = ST1


def make_args(ns):
    return argparse.Namespace(
        prefix_variant=ns.prefix_variant,
        max_round=ns.max_round,
        min_round=ns.min_round,
        free_prefix=ns.free_prefix,
        embedding=-1,
        catalog=ns.catalog,
        encoder=ns.encoder,
        moves=ns.moves,
        data_moves=ns.data_moves,
        prep_before_moves=ns.prep_before_moves,
        compact9=False,
        external_moves=1,
        move_budget=1000,
        exposure_objective=ns.exposure_objective,
    )


def value_map(V, old, pre, ns):
    """Return (model variable, value, label) pairs for every hinted field."""
    out = []
    skipped = []
    def add(v, z, label):
        if v is None or z is None:
            return
        # Avoid querying IntVar.Proto() here: OR-Tools 9.15 can invalidate
        # the temporary protobuf wrapper when a model has a short horizon.
        # These are the explicit primary-variable domains in create().
        z = int(z); valid = True
        if label == "R": valid = ns.min_round <= z <= ns.max_round
        elif label.startswith("prefix_t[") or label.startswith("jobs[") and label.endswith(".t"):
            valid = 0 <= z < ns.max_round
        elif label.startswith("tokens.") and (".init" in label or ".ts[" in label):
            valid = 0 <= z < ns.max_round
        elif label.startswith("tokens.") and ".moves[" in label:
            valid = z in (0, 1)
        elif label.startswith("prefix_locs[") or label.startswith("mapping") or label == "embedding":
            valid = 0 <= z <= 35
        elif label.startswith("tokens.") and ".pos[" in label:
            valid = 0 <= z <= 35
        elif label.startswith("jobs[") and (".stage[" in label):
            valid = 0 <= z <= 6
        elif label.startswith("jobs[") and ".loc[" in label:
            valid = 0 <= z <= 35
        elif label.startswith("permutations."):
            valid = 0 <= z <= 6
        elif label.startswith("endpoints."):
            valid = 0 <= z <= 35
        if not valid:
            skipped.append((label, z, "explicit-domain"))
            return
        out.append((v, z, label))

    add(V["R"], old.get("R", old.get("round")), "R")
    if "embedding" in old:
        add(V["embedding"], old["embedding"], "embedding")
    omap = old.get("mapping", {})
    for q, v in V["mapping"].items():
        if str(q) in omap:
            add(v, omap[str(q)], f"mapping[{q}]")
    for i, v in enumerate(V["prefix_t"]):
        if i < len(old.get("prefix_t", [])):
            add(v, old["prefix_t"][i], f"prefix_t[{i}]")
    # Older catalog witnesses did not store per-unit locations.  Derive those
    # locations from the mapping, which is exactly the model's free-prefix
    # equality for each prefix segment.
    old_pl = old.get("prefix_locs")
    for i, vs in enumerate(V["prefix_locs"]):
        if old_pl is not None and i < len(old_pl):
            vals = old_pl[i]
        else:
            vals = [omap.get(str(q)) for q in pre[i].qs]
        for j, v in enumerate(vs):
            if j < len(vals) and vals[j] is not None:
                add(v, vals[j], f"prefix_locs[{i},{j}]")
    for key, tok in V["tokens"].items():
        ot = old.get("tokens", {}).get(key, {})
        for name, v in tok.items():
            if name not in ot:
                continue
            z = ot[name]
            if isinstance(v, list):
                for j, vv in enumerate(v):
                    if j < len(z):
                        add(vv, z[j], f"tokens.{key}.{name}[{j}]")
            else:
                add(v, z, f"tokens.{key}.{name}")
    for key, vs in V["permutations"].items():
        z = old.get("permutations", {}).get(key, [])
        for j, v in enumerate(vs):
            if j < len(z):
                add(v, z[j], f"permutations.{key}[{j}]")
    for key, vs in V["endpoints"].items():
        z = old.get("endpoints", {}).get(key, [])
        for j, v in enumerate(vs):
            if j < len(z):
                add(v, z[j], f"endpoints.{key}[{j}]")
    for i, job in enumerate(V["jobs"]):
        if i >= len(old.get("jobs", [])):
            continue
        oj = old["jobs"][i]
        if job["k"] != oj.get("k") or job["indices"] != oj.get("indices"):
            continue
        add(job["t"], oj.get("t"), f"jobs[{i}].t")
        for name in ("stage", "loc"):
            z = oj.get(name, [])
            for j, v in enumerate(job[name]):
                if j < len(z):
                    add(v, z[j], f"jobs[{i}].{name}[{j}]")
    return out, skipped


def run(ns):
    # The correlated-BC resource itself is outside ST1's three-independent-
    # encoder model.  For the warm/LNS placement object we use the same direct
    # 10/11/11-CX endpoint encoders as the compatible catalog witness, but keep
    # their cells and all terminal permutations free.  This is the global
    # placement model; the correlated resource is priced separately by FRESH.
    if ns.direct_encoder:
        direct = json.loads(pathlib.Path(ns.direct_encoder).read_text())
        def direct_encoder(_name, k):
            initial = direct["initial"][k]
            ops = [(initial.index(u), initial.index(v)) for u, v in direct["blocks"][k]["ops"]]
            piv = [initial.index(q) for q in direct["blocks"][k]["pivots"]]
            return ops, piv
        redesign.encoder = direct_encoder
        ns.catalog = None
        ns.encoder = "cdirect"
    a = make_args(ns)
    model, V, pre, dets, embs, enc, decisions = redesign.create(a)
    old = json.loads(pathlib.Path(ns.hint).read_text())
    raw_pairs, skipped = value_map(V, old, pre, ns)
    # A prefix location can occur in several units; CP-SAT accepts one hint
    # per variable, so collapse repeated references and detect disagreement.
    by_index = {}
    conflicts = []
    for v, z, label in raw_pairs:
        idx = v.Index()
        if idx in by_index and by_index[idx][1] != z:
            conflicts.append((idx, by_index[idx][1], z, by_index[idx][2], label))
        else:
            by_index.setdefault(idx, (v, z, label))
    pairs = list(by_index.values())
    if conflicts:
        raise ValueError("inconsistent warm hint values: " + repr(conflicts[:5]))
    def free_label(label):
        g = ns.lns_group
        if not g:
            return False
        if g == "prefix":
            return label.startswith("prefix_") or label.startswith("mapping") or label == "embedding"
        if g == "late_prefix":
            if label.startswith("prefix_t[") or label.startswith("prefix_locs["):
                try:
                    i = int(label.split("[")[1].split(",")[0].split("]")[0])
                    return i >= ns.late_prefix_from
                except Exception:
                    return False
            return False
        if g == "data":
            return label.startswith("tokens.d") or label.startswith("jobs[") and "." in label and any(f"jobs[{i}]" in label for i in range(7)) or label.startswith("endpoints.d")
        if g == "resource":
            return (label.startswith("tokens.a") or label.startswith("tokens.b") or label.startswith("tokens.c")
                    or label.startswith("endpoints.a") or label.startswith("endpoints.b") or label.startswith("endpoints.c")
                    or label.startswith("permutations.a") or label.startswith("permutations.b") or label.startswith("permutations.c")
                    or label.startswith("jobs["))
        if g == "endpoints":
            return label.startswith("endpoints.") or label.startswith("permutations.")
        return False
    fixed_count = 0
    for v, z, label in pairs:
        model.AddHint(v, z)
        if ns.fix_hint or (ns.lns_group and not free_label(label)):
            model.Add(v == z)
            fixed_count += 1
    receipt = dict(
        out=ns.out, hint=ns.hint, fix_hint=ns.fix_hint,
        hinted_variables=len(pairs), model_variables=len(model.Proto().variables),
        hint_R=old.get("R", old.get("round")), args=vars(ns),
        lns_group=ns.lns_group, fixed_variables=fixed_count,
        skipped_hint_values=len(skipped), skipped_hint_examples=skipped[:8],
    )
    (FRESH / (ns.out + ".hint.json")).write_text(json.dumps(receipt, indent=2))
    solver = redesign.cp_model.CpSolver()
    solver.parameters.num_workers = ns.workers
    solver.parameters.max_time_in_seconds = ns.seconds
    solver.parameters.cp_model_presolve = False
    solver.parameters.random_seed = ns.seed
    solver.parameters.log_search_progress = bool(ns.progress)
    solver.parameters.log_to_stdout = bool(ns.progress)
    started = time.monotonic()

    class CB(redesign.cp_model.CpSolverSolutionCallback):
        def __init__(self):
            super().__init__(); self.n = 0
        def on_solution_callback(self):
            self.n += 1
            row = dict(n=self.n, elapsed=time.monotonic()-started,
                       objective=self.ObjectiveValue(), bound=self.BestObjectiveBound(),
                       R=self.Value(V["R"]))
            with (FRESH / (ns.out + ".progress.jsonl")).open("a") as f:
                f.write(json.dumps(row) + "\n")
            # Preserve any R improvement as a complete model witness while the
            # callback is still live; later emission/pricing is sequential.
            if self.Value(V["R"]) < old.get("R", old.get("round", 10**9)):
                x = redesign.get(self, a, V, pre, dets, embs, enc)
                (FRESH / (ns.out + f"_R{self.Value(V['R'])}_w{self.n}.solver.json")).write_text(json.dumps(x, indent=1))
            print(json.dumps(row), flush=True)

    cb = CB()
    status = solver.Solve(model, cb)
    receipt.update(status=solver.StatusName(status), seconds=time.monotonic()-started,
                   stats=solver.ResponseStats(), solutions=cb.n,
                   objective=solver.ObjectiveValue(), bound=solver.BestObjectiveBound())
    if status in (redesign.cp_model.FEASIBLE, redesign.cp_model.OPTIMAL):
        x = redesign.get(solver, a, V, pre, dets, embs, enc)
        # This is a FRESH-only solver witness.  A separate emitter can consume
        # it without mutating ST1.
        (FRESH / (ns.out + ".solver.json")).write_text(json.dumps(x, indent=1))
    (FRESH / (ns.out + ".receipt.json")).write_text(json.dumps(receipt, indent=2))
    print(json.dumps(receipt), flush=True)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True); p.add_argument("--hint", required=True)
    p.add_argument("--catalog"); p.add_argument("--encoder", default="l3_10")
    p.add_argument("--direct-encoder")
    p.add_argument("--moves", type=int, default=1); p.add_argument("--data-moves", type=int, default=6)
    p.add_argument("--min-round", type=int, default=30); p.add_argument("--max-round", type=int, default=70)
    p.add_argument("--prefix-variant", default="base"); p.add_argument("--free-prefix", action="store_true")
    p.add_argument("--prep-before-moves", action="store_true"); p.add_argument("--exposure-objective", action="store_true")
    p.add_argument("--workers", type=int, default=16); p.add_argument("--seconds", type=float, default=3600)
    p.add_argument("--seed", type=int, default=0); p.add_argument("--fix-hint", action="store_true")
    p.add_argument("--lns-group", choices=["prefix", "late_prefix", "data", "resource", "endpoints"])
    p.add_argument("--late-prefix-from", type=int, default=90)
    p.add_argument("--progress", action="store_true")
    run(p.parse_args())


if __name__ == "__main__":
    main()
