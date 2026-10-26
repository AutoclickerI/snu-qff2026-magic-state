"""Verify recovered pass-4 builds against v37g without repricing the ledger."""
from pass4 import *
import statistics, socket, runpy


def cli(st):
    sys.path.insert(0, str(ROOT / 'work'))
    import xtim
    xtim.cache_dir = str(H / '.xtim_cache')
    source = H / 'judge_snapshot/fast_check.py'
    sys.argv = [str(source), str(st.with_suffix('.qasm')),
                str(st.with_suffix('.json')), '1000000', '1']
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        state = runpy.run_path(str(source), run_name='__main__')
    rep = state['rep']
    r = dict(sha256=sha(st), seconds=time.time()-state['t'],
             gates_ok=bool(rep.correct_ok), format_ok=bool(rep.format_ok),
             class_ok=bool(rep.class_ok), shots=10**6, procs=1,
             host=socket.gethostname(), stdout=out.getvalue(),
             fast_check_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
             tprep_check_sha256=hashlib.sha256(Path(sys.modules['tprep.check'].__file__).read_bytes()).hexdigest())
    print(json.dumps(dict(event='current_cli', **r)), flush=True)
    return r


def run():
    baseline = H / 'cand/merge4_r2_79fc464667ef'
    baseline_price = json.loads(baseline.with_suffix('.json').read_text())
    outcome = json.loads((R / 'wide_outcome.json').read_text())
    assert outcome['complete'] and outcome['last_gain'] < 1e-9
    best = outcome['price']
    stem = Path(best['stem'])
    assert sha(stem) == best['sha256'] and feasible(best)
    assert sha(baseline) == baseline_price['sha256']
    assert all(abs(x - 1) < 1e-10 for x in best['raw_stabilizers'])
    controls, runs = [], []
    for i in range(3):
        order = [('v37g', baseline), ('candidate', stem)]
        if i % 2:
            order.reverse()
        for kind, path in order:
            r = cli(path)
            (controls if kind == 'v37g' else runs).append(r)
    bs = statistics.median(x['seconds'] for x in controls)
    cs = statistics.median(x['seconds'] for x in runs)
    judge = dict(sha256=sha(stem), baseline_sha256=sha(baseline),
                 baseline='v37g', host=socket.gethostname(),
                 gates_ok=all(x['gates_ok'] for x in runs), speed_ok=cs <= 1.5*bs,
                 median_seconds=cs, baseline_median_seconds=bs, ratio=cs/bs,
                 judge_runs=runs, baseline_runs=controls)
    dump(R / 'resume_judge_v37g.json', judge)
    assert judge['gates_ok'] and judge['speed_ok'], judge
    gain = baseline_price['loss'] - best['loss']
    qualifies = gain > 3e-8
    plan = M.read(stem)
    artifact = dict(best, judge_1e6=judge, tau=baseline_price['loss'],
                    J_tau=best['acceptance']*(best['loss']-baseline_price['loss']),
                    gain_from_v37g=gain, qualifies_vs_v37g=qualifies,
                    cx=sum(M.unit(o).name == 'CX' for o in plan['ops']),
                    native_depth=M.depth(plan),
                    status='finalist' if qualifies else 'below requested improvement',
                    source=dict(base='v37g', history='res37f/wide_history.json',
                                price_receipt='res37f/wide_r4_joint.jsonl',
                                recovery='completed hippo worker; no search repricing'))
    name = ('merge4_resume_finalist_' if qualifies else 'merge4_resume_below_target_') + best['sha256'][:12]
    dest = H / 'cand' / name
    shutil.copyfile(stem.with_suffix('.qasm'), dest.with_suffix('.qasm'))
    dump(dest.with_suffix('.json'), artifact)
    dump(R / 'resume_artifact.json', dict(name=name, **artifact))
    print(json.dumps(dict(event='resume_verified', name=name, loss=best['loss'],
                         acceptance=best['acceptance'], gain=gain,
                         qualifies=qualifies, ratio=cs/bs)), flush=True)


if __name__ == '__main__':
    run()
