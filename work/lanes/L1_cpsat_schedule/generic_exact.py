"""Exact finite-noise objective and CP-SAT model for a me_layout GModel.

The model is intentionally independent of the older fixed ``gen2`` key set.  It
uses the operations emitted by ``me_layout.gmodel.GModel`` and therefore covers
the moved-data CNOTs, X-only extras, and post-unbell single CNOTs present in A1.
The DEM grouping and probability tables are the same closed form as
``ordered_objective.py``; the only layout-specific part is operation labeling.
"""
from __future__ import annotations

import math
import sys
from collections import defaultdict
from itertools import combinations

from ortools.sat.python import cp_model

from common import HERE, WORK, proxy2, Circ, to_stim, STANDARD, apply_noise

ME = WORK / "lanes" / "me_layout"
if str(ME) not in sys.path:
    sys.path.insert(0, str(ME))
import gmodel  # noqa: E402
import cultiv_port as cp  # noqa: E402
import bounds  # noqa: E402

P = 1e-3
SCALE = 10**9
A1 = math.sqrt(1 - 4 * P / 3)
A2 = (1 - 16 * P / 15) ** (1 / 8)
AR = 1 - 2 * P


def compact(a):
    levels = {v: i + 2 for i, v in enumerate(sorted(set(a.values())))}
    return {k: levels[v] for k, v in a.items()}


def signature(terms):
    det = obs = 0
    for x in terms:
        t = x.dem_target if hasattr(x, "dem_target") else x
        if t.is_relative_detector_id():
            det ^= 1 << t.val
        elif t.is_logical_observable_id():
            obs ^= 1 << t.val
    return det, obs


def addexpr(a, b, factor=1):
    out = dict(a)
    for k, v in b.items():
        out[k] = out.get(k, 0) + factor * v
    return {k: v for k, v in out.items() if v}


def evaluate(expr, a):
    return sum(v * (1 if k == "const" else max(a.values()) if k == "end" else a[k]) for k, v in expr.items())


class ExactObjective:
    """Closed-form DEM objective for one fixed per-qubit gate-order class."""

    def __init__(self, model, assign, orient):
        self.model = model
        self.order = compact(assign)
        self.orient = list(orient)
        m = model
        a = self.order
        c = Circ()
        c.g("id", *[cp.phys(q) for q in gmodel.DATA0])
        m.emit(c, a, orient)
        self.emitted = c
        bit_check = {b: t if B == "X" else 3 + t for (t, B), bits in m.checks.items() for b in bits}
        c.detectors = []
        c = c.rescheduled(lazy_init=True)
        ops = [op for op in c.sops if op[0] != "barrier"]

        key_by_pair = defaultdict(list)
        for k in m.keys:
            pair = tuple(map(cp.phys, m.qubits_of(k, orient)))
            key_by_pair[pair].append(k)
        for pair in key_by_pair:
            key_by_pair[pair].sort(key=a.__getitem__)
        core_pairs = {tuple(map(cp.phys, pair)) for pair in gmodel.BELL}
        extra_by_q = {cp.phys(cc): (t, "A", cc) for t, cc, _ in m.extras}
        q_to_keys = defaultdict(list)
        for k in m.keys:
            for q in m.qubits_of(k, orient):
                q_to_keys[cp.phys(q)].append(k)

        labels = []
        self.cx_keys = []
        bell_seen = set()
        pair_used = defaultdict(set)
        for kind, qs, bit in ops:
            pqs = tuple(qs)
            if kind == "cx":
                if pqs in core_pairs and pqs not in bell_seen:
                    bell_seen.add(pqs)
                    labels.append({"const": 2})
                else:
                    if pqs not in key_by_pair:
                        raise AssertionError(f"unlabeled CX {pqs}")
                    choices = [k for k in key_by_pair[pqs] if k not in pair_used[pqs]]
                    if not choices:
                        raise AssertionError(f"too many CX occurrences for {pqs}")
                    k = choices[0]
                    pair_used[pqs].add(k)
                    self.cx_keys.append((pqs, k, a[k]))
                    labels.append({k: 1, "const": 1})
            elif kind == "g:id":
                labels.append({})
            elif kind in ("R", "RX"):
                # Lazy initialization moves a reset/RX to the layer immediately
                # before the qubit's next operation.  Its symbolic timestamp is
                # therefore derived from that next operation (a moved-data
                # destination is the important case for A1).
                labels.append(None)
            elif kind in ("M", "MX"):
                q = qs[0]
                ks = [k for k in q_to_keys[q] if k[0] != "M" or True]
                last = max(ks, key=a.__getitem__)
                labels.append({last: 1, "const": 2})
            else:
                raise AssertionError(kind)

        for i, (kind, qs, _bit) in enumerate(ops):
            if kind not in ("R", "RX"):
                continue
            j = next((j for j in range(i + 1, len(ops)) if qs[0] in ops[j][1]), None)
            if j is None or labels[j] is None:
                labels[i] = {"const": 1}
            else:
                labels[i] = addexpr(labels[j], {"const": -1})

        next_on, gaps = {}, {}
        for i in range(len(ops) - 1, -1, -1):
            kind, qs, _ = ops[i]
            for q in qs:
                j = next_on.get(q)
                if j is not None and ops[j][0] not in ("R", "RX"):
                    expr = addexpr(addexpr(labels[j], labels[i], -1), {"const": -1})
                elif j is None and kind not in ("M", "MX"):
                    expr = addexpr({"end": 1, "const": 2}, labels[i], -1)
                else:
                    expr = {}
                if expr:
                    gaps[i, q] = expr
                next_on[q] = i

        self.ops = ops
        self.labels = labels
        self.gap_exprs = gaps

        channels = {}
        noisy = __import__("stim").Circuit()
        bits = []

        def noise(name, qs, expr=None):
            tag = str(len(channels))
            channels[tag] = (name, expr)
            noisy.append(name, qs, P, tag=tag)

        seen = set()
        for i, (kind, qs, bit) in enumerate(ops):
            fresh = [q for q in qs if q not in seen]
            seen.update(qs)
            if fresh and kind not in ("R", "RX"):
                for q in fresh:
                    noise("X_ERROR", [q])
            if kind in ("M", "MX"):
                noise("X_ERROR" if kind == "M" else "Z_ERROR", list(qs))
                bits.append(bit)
            noisy.append({"g:id": "I", "cx": "CX"}.get(kind, kind), qs)
            if kind in ("R", "RX"):
                for q in qs:
                    noise("X_ERROR" if kind == "R" else "Z_ERROR", [q])
            elif kind == "cx":
                noise("DEPOLARIZE2", qs)
            else:
                for q in qs:
                    noise("DEPOLARIZE1", [q], {"const": 1})
            for q in qs:
                if (i, q) in gaps:
                    noise("DEPOLARIZE1", [q], gaps[i, q])

        self.channels = channels
        self.noisy = noisy
        summaries = []
        for logical in ("X", "Z"):
            circ = m._full(str(noisy), bits, bit_check, logical)
            grouped = {}
            for err in circ.explain_detector_error_model_errors():
                sig = signature(err.dem_error_terms)
                expr = {}
                n2 = nr = 0
                for loc in err.circuit_error_locations:
                    name, e = channels[loc.noise_tag]
                    if name == "DEPOLARIZE1":
                        expr = addexpr(expr, e)
                    elif name == "DEPOLARIZE2":
                        n2 += 1
                    else:
                        nr += 1
                if sig in grouped:
                    # Separate independent faults with the same full signature
                    # combine multiplicatively, so their exponents add.
                    old_expr, old_n2, old_nr = grouped[sig]
                    grouped[sig] = (addexpr(old_expr, expr), old_n2 + n2, old_nr + nr)
                else:
                    grouped[sig] = (expr, n2, nr)
            summaries.append(grouped)

        self.basis_groups = {}
        for basis, grouped in enumerate(summaries):
            for (d, s), (expr, n2, nr) in grouped.items():
                self.basis_groups.setdefault((d, s & 63), [[], []])[basis].append((s >> 6, expr, n2, nr))
        # A moved-data layout can change the logical-flip bit while preserving
        # the detector/stabilizer signature.  That is still the same joint-loss
        # group, but it must use the general probability sorting/matching path.
        self.general = (set(summaries[0]) != set(summaries[1])) or any(
            len(x) != 1 or len(y) != 1 or x[0][1:] != y[0][1:]
            for x, y in self.basis_groups.values()
        )
        if self.general:
            self.mech = []
            self.pairs = []
            self.first = []
            self.rounding_bound = None
            return

        A, B = [
            {(d, s): (s >> 6, expr, n2, nr) for (d, s), (expr, n2, nr) in grouped.items()}
            for grouped in summaries
        ]
        if A.keys() != B.keys():
            print("X keys", len(A), "Z keys", len(B), "onlyX", sorted(A.keys() - B.keys())[:8], "onlyZ", sorted(B.keys() - A.keys())[:8])
            raise AssertionError("unmatched X/Z mechanism mapping")
        self.mech = []
        for k in sorted(A):
            fa, expr, n2, nr = A[k]
            fb, expr_b, n2b, nrb = B[k]
            if (expr, n2, nr) != (expr_b, n2b, nrb):
                raise AssertionError("X/Z noise mismatch")
            self.mech.append((*k, fa, fb, expr, n2, nr))
        self.pairs, self.first = [], []
        for i, (d, s, fa, fb, *_rest) in enumerate(self.mech):
            if d == 0 and (w := self.weight(s, fa, fb)):
                self.first.append((i, w))
            for j in range(i):
                dd, ss, aa, bb, *_ = self.mech[j]
                if d == dd and (w := self.weight(s ^ ss, fa ^ aa, fb ^ bb)):
                    self.pairs.append((i, j, w))

    @staticmethod
    def weight(stab, fa, fb):
        fx = fa ^ bool(stab & 7)
        fz = fb ^ bool(stab & 56)
        return 2 if fx and not fz else 1 if fz else 0

    def masses(self, a):
        return [(1 - A1 ** evaluate(e, a) * A2 ** n2 * AR ** nr) / 2 for d, s, fa, fb, e, n2, nr in self.mech]

    def value(self, a):
        if self.general:
            groups = defaultdict(list)
            for (_d, s), (left, right) in self.basis_groups.items():
                vals = []
                for side in (left, right):
                    vals.append(sorted([((1 - A1 ** evaluate(e, a) * A2 ** n2 * AR ** nr) / 2, f)
                                        for f, e, n2, nr in side], reverse=True))
                for i in range(max(map(len, vals))):
                    pa, fa = vals[0][i] if i < len(vals[0]) else (0, 0)
                    pb, fb = vals[1][i] if i < len(vals[1]) else (0, 0)
                    groups[_d].append((s, max(pa, pb), fa, fb))
            value = 0.0
            for d, gl in groups.items():
                for i, (s, p, fa, fb) in enumerate(gl):
                    if d == 0:
                        value += p * self.weight(s, fa, fb) / 2
                    for ss, pp, aa, bb in gl[:i]:
                        value += p * pp * self.weight(s ^ ss, fa ^ aa, fb ^ bb) / 2
            return value
        ps = self.masses(a)
        return sum(ps[i] * w / 2 for i, w in self.first) + sum(ps[i] * ps[j] * w / 2 for i, j, w in self.pairs)

    def install(self, schedule):
        if self.general:
            return self._install_general(schedule)
        c, v, end, lmax = schedule.model, schedule.v, schedule.end, schedule.lmax
        probs, ubs, error_bound = [], [], 0.0
        for idx, (_d, _s, _fa, _fb, e, n2, nr) in enumerate(self.mech):
            lb = ub = e.get("const", 0)
            for k, z in e.items():
                if k == "const":
                    continue
                lb += z * (2 if z > 0 else lmax)
                ub += z * (lmax if z > 0 else 2)
            lb, ub = max(0, lb), max(lb, ub)
            cnt = c.new_int_var(lb, ub, f"count_{idx}")
            c.add(cnt == sum(z * (1 if k == "const" else end if k == "end" else v[k]) for k, z in e.items()))
            table = [round(SCALE * (1 - A1 ** n * A2 ** n2 * AR ** nr) / 2) for n in range(lb, ub + 1)]
            p = c.new_int_var(min(table), max(table), f"prob_{idx}")
            c.add_element(cnt - lb, table, p)
            probs.append(p)
            ubs.append(max(table))
        terms = []
        for i, w in self.first:
            terms.append(probs[i] * (w * SCALE))
            error_bound += w / (4 * SCALE)
        for n, (i, j, w) in enumerate(self.pairs):
            prod = c.new_int_var(0, ubs[i] * ubs[j], f"pair_{n}")
            c.add_multiplication_equality(prod, [probs[i], probs[j]])
            terms.append(w * prod)
            error_bound += w / 2 * ((ubs[i] + ubs[j]) / (2 * SCALE**2) + 1 / (4 * SCALE**2))
        c.minimize(sum(terms))
        self.rounding_bound = error_bound
        return len(self.mech), len(self.pairs)

    def _install_general(self, schedule):
        """Integer CP encoding of the same sorting/max-matching as joint_loss."""
        c, v, end, lmax = schedule.model, schedule.v, schedule.end, schedule.lmax
        cache = {}
        serial = 0

        def probability(expr, n2, nr):
            nonlocal serial
            key = (tuple(sorted(expr.items(), key=lambda kv: str(kv[0]))), n2, nr)
            if key in cache:
                return cache[key]
            idx = serial
            serial += 1
            lb = ub = expr.get("const", 0)
            for k, z in expr.items():
                if k == "const":
                    continue
                lb += z * (2 if z > 0 else lmax)
                ub += z * (lmax if z > 0 else 2)
            lb, ub = max(0, lb), max(lb, ub)
            cnt = c.new_int_var(lb, ub, f"general_count_{idx}")
            c.add(cnt == sum(z * (1 if k == "const" else end if k == "end" else v[k]) for k, z in expr.items()))
            real = {n: (1 - A1 ** n * A2 ** n2 * AR ** nr) / 2 for n in range(lb, ub + 1)}
            table = [round(SCALE * real[n]) for n in real]
            p = c.new_int_var(min(table), max(table), f"general_prob_{idx}")
            c.add_element(cnt - lb, table, p)
            cache[key] = (cnt, p, max(table), real)
            return cache[key]

        def sorted_side(side, label):
            raw = [(f, *probability(e, n2, nr)) for f, e, n2, nr in side]
            if len(raw) < 2:
                return [(p, f, ub) for f, cnt, p, ub, _real in raw]
            if len(raw) != 2:
                raise AssertionError("unexpected mechanism multiplicity")
            fa, ca, pa, ua, ra = raw[0]
            fb, cb, pb, ub, rb = raw[1]
            choose = c.new_bool_var(label + "_choose")
            rows = [(na, nb, int((rb[nb], fb) >= (ra[na], fa))) for na in ra for nb in rb]
            c.add_allowed_assignments([ca, cb, choose], rows)
            high = c.new_int_var(0, max(ua, ub), label + "_high")
            low = c.new_int_var(0, max(ua, ub), label + "_low")
            c.add(high == pb).only_enforce_if(choose)
            c.add(high == pa).only_enforce_if(~choose)
            c.add(low == pa).only_enforce_if(choose)
            c.add(low == pb).only_enforce_if(~choose)
            fh = c.new_bool_var(label + "_fh")
            fl = c.new_bool_var(label + "_fl")
            c.add(fh == fb).only_enforce_if(choose)
            c.add(fh == fa).only_enforce_if(~choose)
            c.add(fl == fa).only_enforce_if(choose)
            c.add(fl == fb).only_enforce_if(~choose)
            return [(high, fh, max(ua, ub)), (low, fl, max(ua, ub))]

        mechs = []
        for idx, ((_d, s), (left, right)) in enumerate(sorted(self.basis_groups.items())):
            aa = sorted_side(left, f"sortA_{idx}")
            bb = sorted_side(right, f"sortB_{idx}")
            for rank in range(max(len(aa), len(bb))):
                pa, fa, ua = aa[rank] if rank < len(aa) else (0, 0, 0)
                pb, fb, ub = bb[rank] if rank < len(bb) else (0, 0, 0)
                p = c.new_int_var(0, max(ua, ub), f"joint_{idx}_{rank}")
                c.add_max_equality(p, [pa, pb])
                mechs.append((_d, s, fa, fb, p, max(ua, ub)))

        def weight_var(stab, fa, fb, aa, bb, label):
            if all(isinstance(x, int) for x in (fa, fb, aa, bb)):
                return self.weight(stab, fa ^ aa, fb ^ bb)
            def xor_bit(x, y, parity, name):
                out = c.new_bool_var(name)
                c.add_bool_xor([x, y, out, int(not parity)])
                return out
            fx = xor_bit(fa, aa, bool(stab & 7), label + "_fx")
            fz = xor_bit(fb, bb, bool(stab & 56), label + "_fz")
            w = c.new_int_var(0, 2, label + "_w")
            c.add_allowed_assignments([fx, fz, w], [(0, 0, 0), (1, 0, 2), (0, 1, 1), (1, 1, 1)])
            return w

        terms, error, pairs = [], 0.0, 0
        for i, (d, s, fa, fb, p, ub) in enumerate(mechs):
            if d == 0:
                w = weight_var(s, fa, fb, 0, 0, f"first_{i}")
                if isinstance(w, int):
                    if w:
                        terms.append(w * SCALE * p)
                        error += w / (4 * SCALE)
                else:
                    x = c.new_int_var(0, 2 * ub, f"firstprod_{i}")
                    c.add_multiplication_equality(x, [p, w])
                    terms.append(SCALE * x)
                    error += 1 / (2 * SCALE)
            for j, (dd, ss, aa, bb, pp, uub) in enumerate(mechs[:i]):
                if dd != d:
                    continue
                w = weight_var(s ^ ss, fa, fb, aa, bb, f"pair_{i}_{j}")
                if isinstance(w, int) and w == 0:
                    continue
                prod = c.new_int_var(0, ub * uub, f"prod_{i}_{j}")
                c.add_multiplication_equality(prod, [p, pp])
                pairs += 1
                if isinstance(w, int):
                    terms.append(w * prod)
                else:
                    wp = c.new_int_var(0, 2 * ub * uub, f"wprod_{i}_{j}")
                    c.add_multiplication_equality(wp, [prod, w])
                    terms.append(wp)
                error += (ub + uub) / (2 * SCALE**2) + 1 / (4 * SCALE**2)
        c.minimize(sum(terms))
        self.rounding_bound = error
        self.mech = mechs
        self.pairs_count = pairs
        return len(mechs), pairs


class LayoutSchedule:
    def __init__(self, model, lmax, seed=None, fixed_order=None):
        self.layout = model
        self.lmax = lmax
        self.model = cp_model.CpModel()
        self.v = {k: self.model.new_int_var(2, lmax, f"v_{i}") for i, k in enumerate(model.keys)}
        self.keys = list(model.keys)
        self.end = self.model.new_int_var(2, lmax, "last_layer")
        self.model.add_max_equality(self.end, list(self.v.values()))
        self.perq = {}
        for k in self.keys:
            for q in model.qubits_of(k, [0, 0, 0]):
                self.perq.setdefault(q, []).append(k)
        for ks in self.perq.values():
            self.model.add_all_different([self.v[k] for k in ks])
        # Moves are strict chains, and all interactions on moved data follow the chain.
        for d, path in model.moves.items():
            ms = [self.v[("M", d, j)] for j in range(2 * len(path))]
            for x, y in zip(ms, ms[1:]):
                self.model.add(x < y)
            for k in self.keys:
                if isinstance(k[0], int) and k[1] == d:
                    self.model.add(self.v[k] > ms[-1])
        # Extra preparation, service, and parent precedence.
        for t, cc, parent in model.extras:
            ak = (t, "A", cc)
            for d, mcoord in model.xmem.items():
                if d[0] == t and mcoord == cc:
                    self.model.add(self.v[ak] < self.v[(t, d[1], "X")])
            for tt, c2, p2 in model.extras:
                if p2 == cc:
                    self.model.add(self.v[ak] < self.v[(tt, "A", c2)])
            # An extra at a vacated data coordinate becomes available after its owner's move.
            for d, path in model.moves.items():
                srcs = [gmodel.DATA0[d], *path[:-1]]
                if cc in srcs:
                    self.model.add(self.v[("M", d, 2 * len(path) - 1)] < self.v[ak])
        # Matching-basis operations after unbell are the only legal post-U interactions.
        self.o = [self.model.new_bool_var(f"orientation_{t}") for t in range(3)]
        for t in range(3):
            u = self.v[(t, "U", "")]
            ax, az = model.readers(t, [0, 0, 0])
            # A boolean orientation selects which physical member is X-reader.
            for k in self.keys:
                if k[0] != t or k[1] in ("U", "A"):
                    continue
                q = model.xmem[(t, k[1])] if k[2] == "X" else model.zmem[(t, k[1])]
                if q not in gmodel.BELL[t]:
                    # X-only extras are independent cat members and may be
                    # serviced after the Bell unmeasurement in either basis.
                    continue
                want = k[2] == "X"
                m0, m1 = gmodel.BELL[t]
                # If q is m0, orientation 0 makes it X-reader; if m1, orientation 1.
                desired = int((q == m1) == want)
                disallowed = self.o[t] if desired == 0 else ~self.o[t]
                self.model.add(self.v[k] < u).only_enforce_if(disallowed)
            for k in self.keys:
                if k[0] == t and k[1] == "A":
                    q = model.qubits_of(k, [0, 0, 0])[0]
                    desired = int(q == gmodel.BELL[t][1])
                    disallowed = self.o[t] if desired == 0 else ~self.o[t]
                    self.model.add(self.v[k] < u).only_enforce_if(disallowed)
        # All nine parity equations.
        for ta, da in enumerate(gmodel.PLAQ):
            for tb, db in enumerate(gmodel.PLAQ):
                terms = []
                for d in set(da) & set(db):
                    b = self.model.new_bool_var(f"parity_{ta}_{tb}_{d}")
                    self.model.add(self.v[(ta, d, "X")] < self.v[(tb, d, "Z")]).only_enforce_if(b)
                    self.model.add(self.v[(ta, d, "X")] >= self.v[(tb, d, "Z")]).only_enforce_if(~b)
                    terms.append(b)
                if terms:
                    ev = self.model.new_int_var(0, len(terms) // 2, f"even_{ta}_{tb}")
                    self.model.add(sum(terms) == 2 * ev)
        if fixed_order is not None:
            aa, oo = fixed_order
            for k in self.keys:
                self.model.add_hint(self.v[k], aa[k])
            for b, x in zip(self.o, oo):
                self.model.add(b == x)
            for ks in self.perq.values():
                seq = sorted(ks, key=aa.__getitem__)
                for x, y in zip(seq, seq[1:]):
                    self.model.add(self.v[x] < self.v[y])
            self.o = [int(x) for x in oo]

    def solve(self, seconds=60, workers=8, seed=0):
        s = cp_model.CpSolver()
        s.parameters.max_time_in_seconds = seconds
        s.parameters.num_search_workers = workers
        s.parameters.random_seed = seed
        s.parameters.cp_model_presolve = False
        status = s.solve(self.model)
        return s, status

    def extract(self, solver):
        return {k: solver.value(v) for k, v in self.v.items()}, [solver.value(x) for x in self.o] if isinstance(self.o[0], cp_model.IntVar) else list(self.o)


def load_row(path, idx=0):
    import json
    import ast
    row = json.loads(open(path).read())[idx]
    out = {}
    for k, L in row[1]:
        x, y, z = k
        if x == "M":
            out[("M", int(y), int(z))] = L
        elif y == "U":
            out[(int(x), "U", "")] = L
        elif y == "A":
            out[(int(x), "A", ast.literal_eval(z))] = L
        else:
            out[(int(x), int(y), z)] = L
    return out, list(row[2])


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default=str(ME / "res_A1_9b_1792752451.json"))
    ap.add_argument("--idx", type=int, default=0)
    ap.add_argument("--lmax", type=int, default=9)
    ap.add_argument("--seconds", type=float, default=120)
    args = ap.parse_args()
    mm = __import__("run_moves").variant("A1")
    aa, oo = load_row(args.file, args.idx)
    obj = ExactObjective(mm, aa, oo)
    print("order", obj.value(aa), "mechs", len(obj.mech), "pairs", len(obj.pairs), flush=True)
    sc = LayoutSchedule(mm, args.lmax, fixed_order=(aa, oo))
    print("model", obj.install(sc), "rounding", obj.rounding_bound, flush=True)
    sol, st = sc.solve(args.seconds)
    print("status", sol.status_name(st), "bound", sol.best_objective_bound / (2 * SCALE**2), "obj", sol.objective_value / (2 * SCALE**2), flush=True)
    if st in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        a2, o2 = sc.extract(sol)
        print("proxy", obj.value(a2), "orient", o2, "assign", a2, flush=True)
