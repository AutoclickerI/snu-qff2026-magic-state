"""Racing seed-0 re-draws: reorder.py's variants, scored chunk by chunk, dropped once they cannot win.

The official score is tprep's 1e8 shots in 100 chunks (chunk k uses seed k) summed in chunk order. Each variant
(reorder.shuffle with rng k, noise schedule signature asserted, gates re-run by tprep.check) is sampled chunk by
chunk in that order with the same per-chunk code as fast_check._chunk. At each checkpoint a normal model of the
remaining chunks, fitted to every chunk this process has sampled, gives the probability that the variant's completed
score ends below the threshold; below KAPPA times that probability for a variant not yet sampled, the variant is
dropped (a fixed floor would drop nearly every eventual winner at chunk 3 once the threshold is ~4 sigma deep). A completed variant's score, sem and acceptance
are therefore the official ones, bit for bit. Threshold: env RACE_THRESHOLD (default: never drop), lowered by every
completed variant that beats it and by reorder/<name>.thr, where promote.sh relays the best completed score of every host.

    RACE_THRESHOLD=3.875e-5 python race.py <stem> <n variants> [procs] [first variant]  ->  reorder/<name>_r<k>.*
"""
import json
import math
import multiprocessing as mp
import os
import random
import sys
import signal
import queue
import itertools
from pathlib import Path

import numpy as np

import tprep
import tprep.check  # noqa: F401  (tprep/__init__ rebinds tprep.check to the function)
from reorder import shuffle, signature
from race_identity import load_mean, digest, environment, file_hash
from race_checkpoint import Journal, replay
from race_control import register_controller

tc = sys.modules["tprep.check"]
KAPPA = 0.7
CHECKS = (1, 2, 3, 4, 6, 8, 10, 15, 20, 30, 45, 60, 80)
N_CHUNKS = 100
_orig = tc._sample
_G = {}


def _capture(circuit, shots, seed, plan=None):
    """tprep.check's sampler hook: run the 64-shot noiseless cross-check, keep the noisy circuit for racing."""
    if shots == 64:
        return _orig(circuit, shots, seed, plan)
    _G["circuit"], _G["plan"] = circuit, plan
    return {"score": 0.0, "sem": 0.0, "acceptance": 1.0, "corrected": 0}


def _chunk(circuit, plan, k):
    """fast_check._chunk for chunk k of the official run (seed k)."""
    n_syn = 2 * len(tc.SUPPORTS)
    n_meas = circuit.num_measurements
    beta = np.array(list(tc.TARGET.values()))
    dets, exps, meas = circuit.compile_detector_sampler(seed=k, engine="exact").sample(
        tc.CHUNK, return_expectations=True, return_measurements=True, bit_packed=True)
    keep = ~dets.any(axis=1)
    for v, recs in plan.postselect:
        parity = np.zeros(len(keep), dtype=np.uint8)
        for r in recs:
            parity ^= (meas[:, r >> 3] >> (r & 7)) & 1
        keep &= parity == v
    kept = meas[keep]
    syn = [(kept[:, b >> 3] >> (b & 7)) & 1 for b in range(n_meas - n_syn, n_meas)]
    z_fix = np.bitwise_or.reduce(syn[:n_syn // 2]).astype(bool)
    x_fix = np.bitwise_or.reduce(syn[n_syn // 2:]).astype(bool)
    sign = np.stack([np.where(z_fix, -1, 1), np.where(z_fix ^ x_fix, -1, 1)], axis=1) * plan.signs
    infid = (1 - (exps[keep] * sign) @ beta) / 2
    return int(keep.sum()), int((z_fix | x_fix).sum()), infid.sum(), (infid ** 2).sum()


def _init(lines, data, ref, best, thr_file, exact, stop, checkpoint_dir):
    _G.update(lines=lines, data=data, ref=ref, best=best, thr_file=thr_file, exact=exact, stop=stop, checkpoint_dir=Path(checkpoint_dir), totals=[], kepts=[])
    signal.signal(signal.SIGUSR1, signal.SIG_IGN)


def _threshold(best, thr_file):
    """This host's best completed score, or the relayed best of all hosts if lower."""
    try:
        return min(best.value, float(open(thr_file).read()))
    except (OSError, ValueError):
        return best.value


def _p_below(kept, total, c, thr):
    """P(completed score < thr) after c chunks, from the per-chunk mean and spread seen so far."""
    t, n = np.array(_G["totals"]), len(_G["totals"])
    if n < 30:
        return 1.0
    m = N_CHUNKS - c
    mu_t, sd_t, mu_k = t.mean(), t.std(ddof=1), float(np.mean(_G["kepts"]))
    z = (thr * (kept + m * mu_k) - total - m * mu_t) / (math.sqrt(m) * sd_t)
    return 0.5 * math.erfc(-z / math.sqrt(2))



def _p_below_exact(kept, total, c, thr):
    """Normal tail of R=S-tau*K with exact E[S], E[K]; samples estimate spread only."""
    if math.isinf(thr) and thr > 0:
        return 1.0
    if c == N_CHUNKS:
        return float(total < thr * kept)
    t, n = np.asarray(_G["totals"]), len(_G["totals"])
    if n < 30:
        return 1.0
    a, numerator = _G["exact"]
    mu = tc.CHUNK * (numerator - thr * a)
    residuals = t - thr * np.asarray(_G["kepts"])
    variance = float(np.mean((residuals - mu) ** 2))
    m = N_CHUNKS - c
    target = -(total - thr * kept) - m * mu
    if variance == 0:
        return float(target > 0)
    z = target / math.sqrt(m * variance)
    return 0.5 * math.erfc(-z / math.sqrt(2))


def _header(var, k):
    return dict(schema=1, qasm=var, data_qubits=_G["data"], variant=k,
                environment_sha256=digest(environment()),
                chunk_code_sha256=digest(_chunk.__code__.co_code.hex()),
                race_source_sha256=file_hash(__file__),
                noise="tprep.STANDARD", p=float(1e-3).hex(),
                chunk_shots=tc.CHUNK, n_chunks=N_CHUNKS, seed_rule="seed = chunk index (zero based)")


def _resume_worthwhile(journal, thr):
    """Compare probability per remaining chunk, excluding already spent work.
    Defer an uncalibrated finite-threshold prefix; never treat n<30's 1 as a model.
    """
    c = len(journal.obj["chunks"])
    if c == N_CHUNKS:
        return True
    if math.isinf(thr) and thr > 0:
        return c > 0
    prior = journal.obj['prior']
    if max(len(_G['totals']),len(prior['totals'])) < 30:
        return False
    current = _G['totals'], _G['kepts']
    if len(prior['totals']) > len(current[0]):
        _G['totals'] = [float.fromhex(s) for s in prior['totals']]
        _G['kepts'] = prior['kepts']
    try:
        a, _, s, _ = replay(journal.values())
        # A fresh race often stops early. Estimate that cost from the persisted
        # calibration, using deterministic bootstrap paths through the same checks.
        fresh_p, fresh_cost = _fresh_value(thr)
        resume_p = _p_below_exact(a,s,c,thr)
        return resume_p / (N_CHUNKS-c) > fresh_p / fresh_cost
    finally:
        _G['totals'],_G['kepts'] = current


def _fresh_value(thr):
    """Predicted fresh success/cost includes the current sample-mean pruning rule.
    Bootstrap is a scheduling estimate only; official sums never use these draws.
    """
    a,numerator = _G['exact']
    r = np.asarray(_G['totals']) - thr*np.asarray(_G['kepts'])
    mu = tc.CHUNK*(numerator-thr*a)
    variance = float(np.mean((r-mu)**2))
    if variance == 0:
        return float(mu < 0), float(N_CHUNKS if mu < 0 else 1)
    from statistics import NormalDist
    rng = np.random.default_rng(70313)
    increments = rng.normal(mu,math.sqrt(variance),size=(2048,N_CHUNKS))
    sums = np.cumsum(increments,axis=1)
    costs = np.full(len(sums),N_CHUNKS)
    # Keep the live drop policy for fresh races until item 3 passes held-out replay.
    prune_mu = float(np.mean(_G['totals'])) - thr*float(np.mean(_G['kepts']))
    prune_variance = float(np.var(_G['totals'],ddof=1))
    prune_prior = _p_below(0,0.,0,thr)
    prior = 0.5*math.erfc(N_CHUNKS*mu/math.sqrt(2*N_CHUNKS*variance))
    if prior == 0:
        return 0.,1.
    # Draw bridges conditional on a winning final sum. This resolves a 4-sigma
    # tail without claiming zero probability from 2048 unconditional samples.
    ends = N_CHUNKS*mu + math.sqrt(N_CHUNKS*variance)*np.array([
        NormalDist().inv_cdf(max(1e-300,min(1-1e-16,float(u)*prior))) for u in rng.random(len(sums))])
    fraction = np.arange(1,N_CHUNKS+1)/N_CHUNKS
    winners = sums + fraction[None,:]*(ends-sums[:,-1])[:,None]
    alive = np.ones(len(sums),dtype=bool)
    winning_alive = alive.copy()
    for c in CHECKS:
        if c >= N_CHUNKS: continue
        scale = math.sqrt((N_CHUNKS-c)*prune_variance)
        def prob(t):
            z = (-t-(N_CHUNKS-c)*prune_mu)/scale
            return np.array([0.5*math.erfc(-v/math.sqrt(2)) for v in z])
        drop = alive & (prob(sums[:,c-1]) < KAPPA*prune_prior)
        costs[drop] = c; alive[drop] = False
        winning_alive &= prob(winners[:,c-1]) >= KAPPA*prune_prior
    return prior*float(winning_alive.mean()),float(costs.mean())


def race(k):
    if _G['stop'].is_set():
        return k,None,0,'paused'
    var = "\n".join(shuffle(_G["lines"], random.Random(k)))
    assert signature(var) == _G["ref"], f"variant {k} changes the schedule"
    path = _G['checkpoint_dir']/f'r{k}.json'
    with Journal(path,_header(var,k)) as journal:
        if journal.obj['state'] in ('dropped','published'):
            return k,None,0,journal.obj['state']
        values = journal.values()
        if values and not _resume_worthwhile(journal,_threshold(_G['best'],_G['thr_file'])):
            return k,None,0,'deferred'
        if values:
            prior = journal.obj['prior']
            if len(prior['totals']) > len(_G['totals']):
                _G['totals'] = [float.fromhex(s) for s in prior['totals']]
                _G['kepts'] = prior['kepts']
        tc._sample = _capture
        try:
            rep = tprep.check(var, _G["data"], shots=10**8, seed=0)
        finally:
            tc._sample = _orig
        if not (rep.format_ok and rep.class_ok and rep.correct_ok):
            journal.state('dropped')
            return k,None,0,'invalid'
        circuit, plan = _G["circuit"], _G["plan"]
        kept, corrected, total, total_sq = replay(values)
        used = 0
        for c in range(len(values),N_CHUNKS):
            if _G['stop'].is_set():
                journal.state('paused')
                return k,None,used,'paused'
            if c in CHECKS:
                thr = _threshold(_G["best"],_G["thr_file"])
                if _p_below(kept,total,c,thr) < KAPPA*_p_below(0,0.,0,thr):
                    journal.state('dropped')
                    return k,None,used,'dropped'
            a,b,s,s2 = _chunk(circuit,plan,c)
            kept += a; corrected += b; total += s; total_sq += s2
            _G['totals'].append(float(s)); _G['kepts'].append(a)
            journal.append((a,b,s,s2),_G['totals'],_G['kepts'])
            used += 1
        mean = max(total/kept,0.)
        var_ = max(total_sq/kept-mean**2,0.)
        acceptance = kept/(N_CHUNKS*tc.CHUNK)
        out = dict(score=mean,sem=(var_/kept)**0.5,acceptance=acceptance,n_2q=rep.n_2q,
                   passed=acceptance>=tc.ACCEPTANCE_FLOOR,text=var,
                   checkpoint=str(path),checkpoint_write_seconds=journal.write_seconds,
                   kept=kept,corrected=corrected,total=total.hex(),total_sq=total_sq.hex())
        # No incomplete run can ever reach the promotion output path.
        assert len(journal.obj['chunks']) == N_CHUNKS
        journal.state('complete')
        with _G['best'].get_lock():
            if out['passed'] and mean < _G['best'].value:
                _G['best'].value = mean
        return k,out,used,'complete'


def main():
    stem, n = sys.argv[1], int(sys.argv[2])
    procs = int(sys.argv[3]) if len(sys.argv) > 3 else 20
    k0 = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    thr = float(os.environ.get("RACE_THRESHOLD", "inf"))
    text = open(stem + ".qasm").read()
    meta = json.load(open(stem + ".json"))
    exact = load_mean(stem + ".exact.json", text, meta["data_qubits"])
    name = os.path.basename(stem)
    os.makedirs("reorder", exist_ok=True)
    best = mp.Value("d", thr)
    thr_file = f"reorder/{name}.thr"
    checkpoint_dir = Path('reorder/checkpoints')/digest(dict(text=text,data=meta['data_qubits']))
    checkpoint_dir.mkdir(parents=True,exist_ok=True)
    stop = mp.Event()
    signal.signal(signal.SIGUSR1,lambda signum,frame: stop.set())
    register_controller(Path(f'reorder/{name}.pid.json'),stem)
    # Across hour names, content identity gives the same checkpoint directory.
    resumes = []
    for path in sorted(checkpoint_dir.glob('r*.json')):
        obj = Journal.read(path)
        if obj['state'] in ('active','paused','complete') and obj['chunks']:
            hdr = obj['header']
            if (hdr['environment_sha256'] != digest(environment()) or
                    hdr['race_source_sha256'] != file_hash(__file__) or
                    hdr['chunk_shots'] != tc.CHUNK or hdr['n_chunks'] != N_CHUNKS):
                print(f'checkpoint incompatible with this build: {path}',flush=True)
                continue
            resumes.append(obj['header']['variant'])
    resume_set = set(resumes)
    tasks = iter(itertools.chain(resumes,(k for k in range(k0,k0+n) if k not in resume_set)))
    results = queue.Queue()
    used = done = 0
    with mp.get_context('fork').Pool(procs,_init,
            (text.split('\n'),meta['data_qubits'],signature(text),best,thr_file,exact,stop,str(checkpoint_dir))) as pool:
        active = 0
        def dispatch():
            nonlocal active
            if stop.is_set(): return False
            try: k = next(tasks)
            except StopIteration: return False
            pool.apply_async(race,(k,),callback=results.put,error_callback=results.put)
            active += 1
            return True
        for _ in range(procs): dispatch()
        while active:
            result = results.get()  # completion event, no polling
            active -= 1
            if isinstance(result,BaseException): raise result
            k,out,c,state = result
            used += c
            if out is None:
                print(f'{name}_r{k} {state} after {c} new chunks (threshold {_threshold(best,thr_file):.17g})',flush=True)
            else:
                done += 1
                path = Path(f'reorder/{name}_r{k}')
                path.with_suffix('.qasm').write_text(out['text'])
                path.with_suffix('.json').write_text(json.dumps(dict(data_qubits=meta['data_qubits'],
                    score=out['score'],acceptance=out['acceptance'],n_2q=out['n_2q'],passed=out['passed'],
                    source=f'{stem} reordered, rng {k}'),indent=1))
                saved = Journal.read(out['checkpoint'])
                with Journal(out['checkpoint'],saved['header']) as journal:
                    journal.state('published')
                print(f"{name}_r{k} 1-F {out['score']:.17g} acc {out['acceptance']:.4f} 2q {out['n_2q']} pass {out['passed']}",flush=True)
            dispatch()
    print(f'{name}: {done} completed, {used} new chunks, cut={stop.is_set()}',flush=True)


if __name__ == '__main__':
    main()
