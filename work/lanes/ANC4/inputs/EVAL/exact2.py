#!/usr/bin/env python
"""Exact second-order (optionally third-order) score of a full submission circuit, no sampling.
See REPORT.md.

    exact2.py <circuit.qasm> [--top 30] [--json sens.json] [--procs 16] [--p 1e-3] [--third]

Reads <circuit>.json for data_qubits (or --data).  --third adds the exact weight-3 term (30-50 s).
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_v] = "1"

import argparse
import json
import multiprocessing as mp
import re
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from engine import Engine  # noqa: E402
from model import Model  # noqa: E402

G = {}


def qasm_lines(text):
    out = []
    for i, raw in enumerate(text.splitlines(), start=1):
        s = raw.split("//")[0].strip()
        if not s or s.startswith(("OPENQASM", "include", "qreg", "creg")):
            continue
        out.append((i, s))
    return out


class Eval:
    def __init__(self, qasm_text, data_qubits, p=1e-3, log=lambda *a: None):
        self.qasm = qasm_text
        self.m = m = Model(qasm_text, data_qubits, p=p)
        self.e = Engine(m)
        self.p = p
        F = m.faults
        self.n_f = len(F)
        self.fp = np.array([f["p"] for f in F])
        self.fch = np.array([f["chan"] for f in F])
        self.fe = np.array([f["e"] for f in F], dtype=np.int64)
        self.fs = [f["s"] for f in F]
        self.fd = [f["d"] for f in F]
        # groups by (s, d)
        groups = {}
        for i, f in enumerate(F):
            groups.setdefault((f["s"], f["d"]), []).append(i)
        self.gkeys = list(groups)
        self.gmem = [np.array(groups[k]) for k in self.gkeys]
        # singles
        self.ga = np.zeros(len(self.gkeys))
        self.n_single = np.zeros(self.n_f)
        for g, (s, d) in enumerate(self.gkeys):
            a, n = self.e.ntable(s, d)
            self.ga[g] = a
            if n is not None:
                self.n_single[self.gmem[g]] = n[self.fe[self.gmem[g]]]
        self.a_single = np.zeros(self.n_f)
        for g in range(len(self.gkeys)):
            self.a_single[self.gmem[g]] = self.ga[g]
        # label data
        ql = qasm_lines(qasm_text)
        self.ql = ql

    # -- label of a channel
    def chan_label(self, c):
        ch = self.m.chans[c]
        ii = ch["ins"]
        lab = self.m.labels[self.m.prog[ii].line_no - 1]
        k = int(re.match(r"instruction (\d+)", lab).group(1))
        qasm_line = None
        if 1 <= k <= len(self.ql):
            qasm_line = self.ql[k - 1][0]
        st = self.m.steps[ii]
        step = st[0][1] if st else None
        if ch["gap"] is not None:
            q, first, n = ch["gap"]
            return dict(kind="idle", line=qasm_line, qubits=ch["qubits"], steps=f"{first}..{first + n - 1}", ins=lab)
        return dict(kind=ch["kind"], line=qasm_line, qubits=ch["qubits"], steps=str(step), ins=lab,
                    when=ch["when"])

    def fault_label(self, i):
        f = self.m.faults[i]
        c = self.chan_label(f["chan"])
        qs = ",".join(str(q) for q in f["qubits"])
        pl = f["pauli"]
        return f"L{c['line']} {c['kind']} {pl}@q{qs} t={c['steps']}"


def _pair_chunk(args):
    ev = G["ev"]
    lo, hi, keep_thr = args
    ng = len(ev.gkeys)
    pairs = G["pairs"][lo:hi]
    nch = len(ev.m.chans)
    sens = np.zeros(nch)
    pair_sum = 0.0
    A2 = 0.0
    Asum = 0.0
    big = []
    t3bc = 0.0
    for (ga, gb) in pairs:
        sa, da = ev.gkeys[ga]
        sb, db = ev.gkeys[gb]
        a_ab, nt = ev.e.ntable(sa ^ sb, da ^ db)
        ia, ib = ev.gmem[ga], ev.gmem[gb]
        pa, pb = ev.fp[ia], ev.fp[ib]
        cross = ev.fch[ia][:, None] != ev.fch[ib][None, :]
        if ga == gb:
            cross &= np.triu(np.ones_like(cross, dtype=bool), 1)
        pp = pa[:, None] * pb[None, :]
        aa, ab = ev.ga[ga], ev.ga[gb]
        # acceptance second-order: 1 - a_i - a_j + a_ij (cross-channel unordered pairs)
        Asum += float((pp * cross).sum() * (1 - aa - ab + a_ab))
        nij = 0.0 if nt is None else nt[ev.fe[ia][:, None] ^ ev.fe[ib][None, :]]
        ni = ev.n_single[ia][:, None]
        nj = ev.n_single[ib][None, :]
        T = nij - ab * ni - aa * nj
        c = pp * T * cross
        if G.get("third"):
            coefm = -G["SA"] + G["Pch"][ev.fch[ia]][:, None] + G["Pch"][ev.fch[ib]][None, :]
            t3bc += float((pp * nij * cross * coefm).sum())
        # in-exact zeros from rounding
        c = np.where(np.abs(c) < 1e-18, 0.0, c)
        tot = float(c.sum())
        pair_sum += tot
        if tot != 0.0 or np.any(c):
            ci = ev.fch[ia][:, None] + 0 * ev.fch[ib][None, :]
            cj = ev.fch[ib][None, :] + 0 * ev.fch[ia][:, None]
            np.add.at(sens, ci.ravel(), c.ravel())
            np.add.at(sens, cj.ravel(), c.ravel())
            ii_, jj_ = np.nonzero(np.abs(c) > keep_thr)
            for u, v in zip(ii_, jj_):
                big.append((float(c[u, v]), int(ia[u]), int(ib[v]), float(nij[u, v] if nt is not None else 0.0), a_ab))
    return pair_sum, Asum, sens, big, t3bc


def _triple_chunk(args):
    ev = G["ev"]
    jobs = args
    tot = 0.0
    big = []
    for (ga, gb) in jobs:
        sa, da = ev.gkeys[ga]
        sb, db = ev.gkeys[gb]
        cs = np.arange(gb, len(ev.gkeys))
        S = np.array([sa ^ sb ^ ev.gkeys[c][0] for c in cs])
        D = np.array([da ^ db ^ ev.gkeys[c][1] for c in cs])
        A, N = ev.e.batch_n(S, D)
        live = np.nonzero(N.max(axis=1) > 1e-15)[0]
        if len(live) == 0:
            continue
        ia, ib = ev.gmem[ga], ev.gmem[gb]
        for u in live:
            gc = int(cs[u])
            ic = ev.gmem[gc]
            nt = N[u]
            ea, eb, ec = ev.fe[ia], ev.fe[ib], ev.fe[ic]
            pa, pb, pc = ev.fp[ia], ev.fp[ib], ev.fp[ic]
            ca, cb, cc = ev.fch[ia], ev.fch[ib], ev.fch[ic]
            step = max(1, int(2_000_000 // max(1, len(ib) * len(ic))))
            for lo in range(0, len(ia), step):
                sl = slice(lo, lo + step)
                e3 = ea[sl, None, None] ^ eb[None, :, None] ^ ec[None, None, :]
                val = nt[e3] * (pa[sl, None, None] * pb[None, :, None] * pc[None, None, :])
                mask = (ca[sl, None, None] != cb[None, :, None]) & (ca[sl, None, None] != cc[None, None, :]) \
                    & (cb[None, :, None] != cc[None, None, :])
                if ga == gb:
                    mask &= ia[sl, None, None] < ib[None, :, None]
                if gb == gc:
                    mask &= ib[None, :, None] < ic[None, None, :]
                val = val * mask
                t = float(val.sum())
                tot += t
                if t > 1e-14:
                    x, y, z = np.nonzero(val > 3e-13)
                    for xx, yy, zz in zip(x, y, z):
                        big.append((float(val[xx, yy, zz]), int(ia[sl][xx]), int(ib[yy]), int(ic[zz])))
    return tot, big


def third_order(ev, procs):
    ng = len(ev.gkeys)
    jobs = [(a, b) for a in range(ng) for b in range(a, ng)]
    G["ev"] = ev
    chunk = max(1, len(jobs) // (procs * 16))
    parts = [jobs[i:i + chunk] for i in range(0, len(jobs), chunk)]
    if procs > 1:
        with mp.get_context("fork").Pool(procs) as pool:
            res = pool.map(_triple_chunk, parts, chunksize=1)
    else:
        res = [_triple_chunk(p_) for p_ in parts]
    return sum(r[0] for r in res), [b for r in res for b in r[1]]


def run(ev, procs=16, keep_thr=1e-12, log=print, third=False):
    ng = len(ev.gkeys)
    G["third"] = third
    G["SA"] = float((ev.fp * ev.a_single).sum())
    G["Pch"] = np.bincount(ev.fch, weights=ev.fp)
    pairs = [(a, b) for a in range(ng) for b in range(a, ng)]
    G["ev"], G["pairs"] = ev, pairs
    chunk = max(1, len(pairs) // (procs * 8))
    jobs = [(lo, min(lo + chunk, len(pairs)), keep_thr) for lo in range(0, len(pairs), chunk)]
    if procs > 1:
        with mp.get_context("fork").Pool(procs) as pool:
            res = pool.map(_pair_chunk, jobs, chunksize=1)
    else:
        res = [_pair_chunk(j) for j in jobs]
    pair_sum = sum(r[0] for r in res)
    A2 = sum(r[1] for r in res)
    sens = sum(r[2] for r in res)
    big = [b for r in res for b in r[3]]
    t3bc = sum(r[4] for r in res)
    # first order and the same-channel product terms
    p, n, a = ev.fp, ev.n_single, ev.a_single
    N1 = float((p * n).sum())
    A1 = float((p * (1 - a)).sum())
    same = 0.0
    nch = len(ev.m.chans)
    for c in range(nch):
        idx = np.nonzero(ev.fch == c)[0]
        same += float((p[idx] * n[idx]).sum() * (p[idx] * (1 - a[idx])).sum())
    out = dict(N1=N1, A1=A1, A2=A2, pair=pair_sum, same=same, loss1=N1, loss2=pair_sum + same,
               loss=N1 + pair_sum + same, t3bc=t3bc, acc1=1 - A1, acc2=1 - A1 + A2, sens=sens, big=big)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("qasm")
    ap.add_argument("--top", type=int, default=30)
    ap.add_argument("--json", default=None)
    ap.add_argument("--procs", type=int, default=16)
    ap.add_argument("--p", type=float, default=1e-3)
    ap.add_argument("--third", action="store_true", help="also the exact third-order term (needs c1 = 0)")
    ap.add_argument("--data", default=None, help="data_qubits json (default: <qasm>.json)")
    a = ap.parse_args()
    text = open(a.qasm).read()
    jf = a.data or a.qasm.rsplit(".", 1)[0] + ".json"
    data = json.load(open(jf))["data_qubits"]
    t0 = time.time()
    ev = Eval(text, data, p=a.p)
    t1 = time.time()
    r = run(ev, a.procs, third=a.third)
    t2 = time.time()
    if a.third and abs(r["loss1"]) >= 1e-12:
        print("c1 != 0: the third-order term is implemented for c1 = 0 only; skipped")
        a.third = False
    if a.third:
        T3a, big3 = third_order(ev, a.procs)
        r["T3a"], r["big3"] = T3a, big3
        r["loss3"] = T3a + r["t3bc"]
    t3 = time.time()
    m = ev.m
    print(f"circuit {a.qasm}: {len(m.chans)} noise channels, {ev.n_f} faults, {len(ev.gkeys)} (s,d) classes, "
          f"rotation rank {ev.e.r}, {m.n_det} detectors, noiseless acceptance {ev.e.A0:.6f}")
    print(f"first order : c1 p = {r['loss1']:.4e}   (sum_i p_i n_i; 0 means every single fault is caught or harmless)")
    print(f"second order: {r['loss2']:.5e}   (pairs {r['pair']:.5e} + same-channel normalisation {r['same']:.3e})")
    print(f"1-F (2nd order) = {r['loss']:.5e}")
    if a.third:
        print(f"third order: {r['loss3']:.5e}   (weight-3 sets {r['T3a']:.5e} + pair-times-others {r['t3bc']:.5e})")
        print(f"1-F (to 3rd order) = {r['loss'] + r['loss3']:.5e}")
    print(f"acceptance: first order {r['acc1']:.5f}, second order {r['acc2']:.5f}; "
          f"exp(-A1) = {np.exp(-r['A1']):.5f}  (A1 = {r['A1']:.5f})")
    print(f"time: model+singles {t1 - t0:.1f}s, pairs {t2 - t1:.1f}s" + (f", triples {t3 - t2:.1f}s" if a.third else ""))
    big = sorted(r["big"], key=lambda b: -abs(b[0]))
    print(f"\ntop {a.top} fault pairs by contribution to 1-F (each pair counted once):")
    for c, i, j, nij, aab in big[:a.top]:
        print(f"  {c:.3e} ({100 * c / r['loss']:5.2f}%)  n_ij={nij:.3f}  {ev.fault_label(i)}   +   {ev.fault_label(j)}")
    cs = np.zeros(4)
    kinds = {}
    for c, ch in enumerate(m.chans):
        k = "idle" if ch["gap"] is not None else ("gate" if ch["kind"] in ("gate1", "gate2") else ch["kind"])
        kinds[k] = kinds.get(k, 0.0) + r["sens"][c] / 2
    print("\nloss by channel kind (each pair split half/half):", {k: f"{v:.3e}" for k, v in kinds.items()})
    if a.json:
        out = []
        for c, ch in enumerate(m.chans):
            lab = ev.chan_label(c)
            P = ch["prob"]
            # d loss / d P_l : bilinear pair terms give attribution/P_l; first order adds sum p_i n_i / P_l
            idx = np.nonzero(ev.fch == c)[0]
            first = float((ev.fp[idx] * ev.n_single[idx]).sum())
            out.append(dict(channel=c, kind=lab["kind"], qasm_line=lab["line"], qubits=lab["qubits"],
                            steps=lab["steps"], prob=P, loss_attribution=float(r["sens"][c] + first),
                            dloss_dP=float((r["sens"][c] + first) / P)))
        json.dump(dict(note="loss_attribution sums to 2x loss (each pair is credited to both partners); "
                        "dloss_dP = d(1-F)/d(channel probability) at the current p", kinds=kinds,
                       loss=r["loss"], loss1=r["loss1"], loss2=r["loss2"], acc1=r["acc1"], acc2=r["acc2"],
                       locations=out), open(a.json, "w"), indent=1)


if __name__ == "__main__":
    main()
