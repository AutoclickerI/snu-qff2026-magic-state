#!/usr/bin/env python3
"""Population search over native circuit macro rewrites on FRESH v30f.

This lane deliberately keeps the representation used by LNS: a folded native
unit list plus an integer time for each unit.  Every mutation is followed by
the same precedence/DAG retiming and nearest-neighbour assertions used by
LNS.  The search score is the exact second-order conditional loss for a broad
population; the Pareto survivors are then rescored with the unchanged exact2
third-order evaluator and the judge gates by ``run_verify.sh``.
"""
import argparse, copy, hashlib, json, math, os, random, re, sys, time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")
sys.path.insert(0, str(OUT))
sys.path.insert(1, str(ROOT / "work/lanes/LNS"))
import core as C  # noqa: E402
import moves as M  # noqa: E402

# LNS's module-level output path points at LNS when imported.  Redirect all
# saves/caches in this process to ST2, without writing to another lane.
C.OUT = OUT
C.xtim.cache_dir = str(OUT / ".xtim_cache")
M.OUT = OUT

BAR = 5.823933151e-5
SEEDS = [OUT / x["name"] for x in json.loads((OUT / "v30_seed_manifest.json").read_text())[:16]]
SEEDS += [OUT / "comp29_f_timing_mz_5_12", OUT / "comp29_f_timing_best_r2"]
_POOL_CACHE = {}


def read_seed(path):
    try:
        c = C.read(path)
        return C.normalize(c)
    except Exception as e:
        return None


def fast_eval(payload):
    """Exact categorical Fourier cubic screen; independent per job."""
    text, data, meta = payload
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("st2_moments", ROOT / "work/lanes/BCPOL/moments_batch.py")
        mom = importlib.util.module_from_spec(spec); spec.loader.exec_module(mom)
        r = mom.evaluate(mom.exact2.Eval(text, data))
        return {"ok": True, "third_screen": True, "c1": float(r["c1"]),
                "second": float(r["second"]), "third": float(r["third"]),
                "total": float(r["total"]), "A1": float(-math.log(r["exp_minus_A1"])),
                "exp_minus_A1": float(r["exp_minus_A1"]),
                "cx": int(meta.get("cx", 0)),
                "R": meta.get("R", meta.get("round_range", [None])[0]),
                "native_depth": meta.get("native_depth"), "nchars": len(text),
                "pair_seconds": r.get("pair_seconds"), "triples": r.get("triples")}
    except Exception as e:
        return {"ok": False, "error": repr(e)}


def payload(c):
    return C.textof(c), list(c["meta"].get("data_qubits", C.D)), dict(c["meta"])


def move_pool(c):
    """Collect bounded macro rewrites from the mature native move families."""
    key = fingerprint(c)
    if key in _POOL_CACHE:
        return _POOL_CACHE[key]
    gens = [
        ("timing", lambda: M.timing_moves(c, True)),
        ("init", lambda: M.init_moves(c)),
        ("idle_detector", lambda: M.extra_init_moves(c)),
        ("commute", lambda: M.commute_moves(c)),
        ("phase", lambda: M.phase_moves(c)),
        ("readout", lambda: M.readout_moves(c)),
        ("detector", lambda: M.detector_moves(c)),
    ]
    # Materializing timing is cheap for these ~500-unit circuits; cap every
    # family so one large family cannot erase population diversity.
    out = []
    for fam, gen in gens:
        rows = []
        try:
            # Do not materialize the full commute/timing neighbourhood.  Some
            # windows contain thousands of legal schedules.
            for j, row in enumerate(gen()):
                rows.append(row)
                if j + 1 >= 32:
                    break
        except Exception:
            rows = []
        for x, d in rows:
            if x is None:
                continue
            d = dict(d)
            d["family"] = fam
            # The all-pivot MX replacement is the known slow path.  Keep
            # ordinary verified RX checks in the search, but do not spend the
            # population on random-MX outcomes before the speed gate.
            if d.get("move") in {"mx_init_pivots", "rx_to_postselected_mx"}:
                continue
            out.append((x, d))
    _POOL_CACHE[key] = out
    return out


def apply_random_macro(base, rng, depth):
    """Apply 1..depth whole-window rewrites, retaining worse intermediates."""
    c = C.clone(base)
    desc = []
    for _ in range(depth):
        pool = move_pool(c)
        if not pool:
            return None, desc
        # Bias toward cross-region families while retaining random exploration.
        fam_weights = {"timing": 3.0, "init": 3.0, "idle_detector": 2.0,
                       "commute": 2.0, "phase": 2.0, "readout": 2.0,
                       "detector": 1.0}
        weights = [fam_weights.get(d.get("family"), 1.0) for _, d in pool]
        x, d = rng.choices(pool, weights=weights, k=1)[0]
        c = C.clone(x)
        try:
            c = C.normalize(c)
        except Exception:
            return None, desc
        desc.append(d)
    return c, desc


def fingerprint(c):
    # A structural diversity key: occupied native time histogram and CX order.
    return hashlib.sha256(C.textof(c).encode()).hexdigest()[:12]


def save_candidate(stem, c, rec):
    txt = C.textof(c)
    md = dict(c["meta"])
    md.update({"st2": rec, "data_qubits": list(md.get("data_qubits", C.D)),
               "cx": sum(u.name == "CX" for u in c["u"]),
               "native_depth": max(c["t"]) + 1})
    (OUT / f"{stem}.qasm").write_text(txt)
    (OUT / f"{stem}.json").write_text(json.dumps(md, indent=2) + "\n")


def pareto(rows):
    """Nondominated on loss, -acceptance, size, and diversity proxy."""
    good = [r for r in rows if r.get("ok") and r.get("exp_minus_A1", 0) >= 0.5002]
    front = []
    for r in good:
        dominated = False
        for q in good:
            if q is r:
                continue
            better = (q["second"] <= r["second"] and
                      q["nchars"] <= r["nchars"] and
                      q["exp_minus_A1"] >= r["exp_minus_A1"])
            strict = (q["second"] < r["second"] or q["nchars"] < r["nchars"] or
                      q["exp_minus_A1"] > r["exp_minus_A1"])
            if better and strict:
                dominated = True
                break
        if not dominated:
            front.append(r)
    return sorted(front, key=lambda r: (r["second"], -r["exp_minus_A1"]))

def exact3_eval(payload):
    """Third-order categorical Fourier score for a small accepted shortlist."""
    text, data, meta = payload
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("st2_moments3", ROOT / "work/lanes/BCPOL/moments_batch.py")
        mom = importlib.util.module_from_spec(spec); spec.loader.exec_module(mom)
        r = mom.evaluate(mom.exact2.Eval(text, data))
        r.update(ok=True, cx=int(meta.get("cx", 0)), R=meta.get("R"),
                 native_depth=meta.get("native_depth"), nchars=len(text))
        return r
    except Exception as e:
        return {"ok": False, "error": repr(e)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--generations", type=int, default=6)
    ap.add_argument("--population", type=int, default=16)
    ap.add_argument("--children", type=int, default=8)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--seed", type=int, default=20261026)
    args = ap.parse_args()
    rng = random.Random(args.seed)
    OUT.mkdir(exist_ok=True)
    logrows = []
    circuits = []

    # Seed from diverse valid physical families; duplicate byte-identical seeds
    # collapse by fingerprint, while their provenance remains in the log.
    seen = set()
    for p in SEEDS:
        if not p.with_suffix(".qasm").exists():
            continue
        c = read_seed(p)
        if c is None:
            continue
        fp = fingerprint(c)
        if fp not in seen:
            seen.add(fp)
            circuits.append((c, {"seed": str(p), "moves": []}))

    for gen in range(args.generations):
        jobs = []
        # Evaluate current population, then generate several children per
        # parent.  Worse children are retained in the candidate pool until the
        # Pareto selection step.
        for c, prov in circuits:
            jobs.append((c, dict(prov, generation=gen, kind="parent")))
            for j in range(args.children):
                child, moves = apply_random_macro(c, rng, rng.choice([1, 1, 2, 3]))
                if child is not None:
                    fp = fingerprint(child)
                    if fp not in seen:
                        seen.add(fp)
                        jobs.append((child, dict(prov, generation=gen, kind="child",
                                                 moves=moves, parent=fingerprint(c))))
        # Avoid an accidental runaway population while preserving each seed's
        # structural family.
        if len(jobs) > args.population * 8:
            jobs = rng.sample(jobs, args.population * 8)
        print(f"generation {gen}: evaluating {len(jobs)} candidates", flush=True)
        payloads = [payload(c) for c, _ in jobs]
        results = [None] * len(jobs)
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            futs = {pool.submit(fast_eval, p): i for i, p in enumerate(payloads)}
            for f in as_completed(futs):
                i = futs[f]
                try:
                    r = f.result()
                except Exception as e:
                    r = {"ok": False, "error": repr(e)}
                r.update(jobs[i][1]); r["fingerprint"] = fingerprint(jobs[i][0])
                r["candidate_index"] = i
                results[i] = r
                logrows.append(r)
        front = pareto(results)
        # Exact third order is the ranking objective.  Use second order only
        # to make the broad population affordable, then rescore the accepted
        # low-loss shortlist before selection and persistence.
        shortlist = [r for r in results if r.get("ok") and r.get("exp_minus_A1", 0) >= 0.5002]
        shortlist.sort(key=lambda r: r["second"])
        shortlist = shortlist[:max(8, args.population // 2)]
        byfp_all = {r["fingerprint"]: jobs[r["candidate_index"]][0] for r in results if r.get("ok")}
        exjobs = [(byfp_all[r["fingerprint"]], r) for r in shortlist]
        if exjobs:
            exres = [None] * len(exjobs)
            with ProcessPoolExecutor(max_workers=args.workers) as pool:
                futs = {pool.submit(exact3_eval, payload(c)): i for i, (c, _) in enumerate(exjobs)}
                for f in as_completed(futs):
                    i = futs[f]
                    try: x = f.result()
                    except Exception as e: x = {"ok": False, "error": repr(e)}
                    x.update(exjobs[i][1]); x["third_screen"] = True
                    x["fingerprint"] = exjobs[i][1]["fingerprint"]
                    exres[i] = x
            by3 = {x["fingerprint"]: x for x in exres if x.get("ok")}
            for r in results:
                if r["fingerprint"] in by3:
                    r.update({k: v for k, v in by3[r["fingerprint"]].items()
                              if k in {"c1", "second", "third", "total", "A1", "exp_minus_A1",
                                       "weight3", "pair_times_others", "seconds"}})
        front = sorted([r for r in results if r.get("ok") and r.get("exp_minus_A1", 0) >= 0.5002],
                       key=lambda r: (r.get("total", r["second"]), r["second"], -r["exp_minus_A1"]))
        # At least one low-loss and one high-acceptance survivor, plus a random
        # slot for diversity.  This is the evolutionary selection pressure.
        chosen = []
        for r in front[: max(2, args.population // 2)]:
            chosen.append(r)
        good = [r for r in results if r.get("ok") and r.get("exp_minus_A1", 0) >= 0.5002]
        good.sort(key=lambda r: (r.get("total", float("inf")), r["second"]))
        for r in good[: args.population]:
            if r not in chosen:
                chosen.append(r)
        for r in rng.sample(good, min(3, len(good))):
            if r not in chosen:
                chosen.append(r)
        chosen = chosen[: args.population]
        byfp = {r["fingerprint"]: jobs[r["candidate_index"]][0] for r in results if r.get("ok")}
        circuits = [(byfp[r["fingerprint"]], r) for r in chosen]
        for k, r in enumerate(chosen[:10]):
            c = byfp[r["fingerprint"]]
            save_candidate(f"v30g{gen}_{k:02d}_{r['fingerprint']}", c, r)
        (OUT / f"generation_{gen}.json").write_text(json.dumps({"front": front,
            "selected": chosen, "evaluated": len(results)}, indent=2) + "\n")
        print("front", [(r.get("total", r.get("second")), r.get("second"), r.get("exp_minus_A1"), r.get("fingerprint")) for r in front[:8]], flush=True)

    # Persist a compact search trace.  Full QASM is retained only for the
    # selected Pareto screens; the trace is compressed after finalization.
    trace = OUT / "population.jsonl"
    with trace.open("w") as f:
        for r in logrows:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    import lzma
    with lzma.open(OUT / "population.jsonl.xz", "wt") as f:
        for r in logrows:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    trace.unlink()
    summary = {"evaluations": len(logrows), "valid": sum(r.get("ok", False) for r in logrows),
               "acceptance_survivors": sum(r.get("ok", False) and r.get("exp_minus_A1", 0) >= .5002 for r in logrows),
               "best_second": min((r["second"] for r in logrows if r.get("ok") and r.get("exp_minus_A1", 0) >= .5002), default=None),
               "third_scored": sum(bool(r.get("third_screen")) for r in logrows),
               "best_third": min((r["total"] for r in logrows if r.get("third_screen") and r.get("ok") and r.get("exp_minus_A1", 0) >= .5002), default=None),
               "seed": args.seed, "generations": args.generations, "population": args.population,
               "children": args.children}
    (OUT / "population_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
