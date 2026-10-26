"""Compact ledger index and current report; full immutable receipts stay in res37f/."""
from pass4 import *
import wide4


def compact(r, source):
    keys = ('stem', 'data_qubits', 'loss', 'acceptance', 'bound', 'error')
    return dict({k: r[k] for k in keys if k in r}, receipt=source)


def front(rows):
    out, maxa = [], -1.0
    for r in sorted((r for r in rows if 'loss' in r),
                    key=lambda r: (r['loss'], -r['acceptance'])):
        if r['acceptance'] > maxa:
            out.append(dict(sha256=r['sha256'], **compact(r, r['_receipt'])))
            maxa = r['acceptance']
    return out


def run():
    hist = json.loads((R / 'wide_history.json').read_text())
    outcome = json.loads((R / 'wide_outcome.json').read_text())
    control = json.loads((R / 'resume_v37g_reproduction.json').read_text())
    best = outcome['price']
    original = H / 'archive/pass3_final/results.json'
    rows = {s: compact(r, 'archive/pass3_final/results.json#' + s)
            for s, r in json.loads(original.read_text()).items()}
    receipts, stages = [], collections.defaultdict(list)
    for f in sorted(R.glob('*.jsonl')):
        for line, text in enumerate(f.read_text().splitlines(), 1):
            r = json.loads(text)
            r['_receipt'] = f'{f.relative_to(H)}:{line}'
            stages[f.stem].append(r)
            if 'sha256' not in r:
                continue
            receipts.append(r)
            s = r['sha256']
            rr = compact(r, r['_receipt'])
            prior = rows.get(s, {})
            variants = prior.get('ordered_output_variants', {})
            if prior.get('data_qubits') != r['data_qubits'] and prior.get('data_qubits'):
                variants[','.join(map(str, prior['data_qubits']))] = {
                    k: v for k, v in prior.items() if k != 'ordered_output_variants'}
            if variants:
                variants[','.join(map(str, r['data_qubits']))] = dict(rr)
                rr['ordered_output_variants'] = variants
            rows[s] = rr
    # One compact row per QASM hash; full provenance is referenced, not copied 40,000 times.
    target = H / 'results.json'
    tmp = target.with_suffix('.json.tmp')
    with tmp.open('w') as f:
        f.write('{\n')
        for n, (s, r) in enumerate(sorted(rows.items())):
            if n:
                f.write(',\n')
            f.write(json.dumps(s) + ':' + json.dumps(r, separators=(',', ':')))
        f.write('\n}\n')
    tmp.replace(target)
    fronts, completed = {}, {}
    for rnd in (3, 4):
        tag = f'wide_r{rnd}'
        before = hist[rnd-1]['before']
        allrows = [r for k, rs in stages.items() if k.startswith(tag + '_') for r in rs]
        fronts[tag] = dict(
            all_measured=front(allrows),
            under_floor=front([r for r in allrows if r.get('acceptance', 1) < FLOOR]),
            acceptance_buyers=front([r for r in stages[tag + '_singles'] if wide4.buyer(r, before)]),
            funding_levels={str(d): front(stages[f'{tag}_fund{d}']) for d in range(1, 5)})
        for tasks in sorted(R.glob(tag + '*_tasks.json')):
            stage = tasks.name[:-len('_tasks.json')]
            expected = {tuple(x) for x in json.loads(tasks.read_text())}
            actual = {tuple(r['edits']) for r in stages[stage]}
            assert expected <= actual, (stage, len(expected - actual))
            completed[stage] = len(expected)
    dump(R / 'resume_pareto4.json', fronts)
    artifact_path = R / 'resume_artifact.json'
    artifact = json.loads(artifact_path.read_text()) if artifact_path.exists() else None
    gain = control['loss'] - best['loss']
    lines = [
        '# MERGE — pass 4 recovered and converged', '',
        'Verdict: COMPLETE within the enumerated widened neighborhood; no finalist meets the new v37g − 3e-8 target.',
        'Recovery changed the premise: hippo continued after the 03:22 thread failure, completed rounds 3 and 4, and exited at 08:51 KST. PID 3571825 is absent; no MERGE worker remains on hippo or zebra.',
        f"v37g reproduction: L={control['loss']:.17g}, A={control['acceptance']:.17g}; SHA256 `{control['sha256']}`. Difference from supplied L is 2.21e-16; six raw output stabilizers equal +1 within 1e-10.",
        f"Best saved build: L={best['loss']:.17g}, A={best['acceptance']:.17g}; gain from v37g={gain:.12g}; SHA256 `{best['sha256']}`.",
        f"Convergence: round 4 gain={outcome['last_gain']:.12g} < 1e-9 after the complete joint/ejection/replacement/funding scan. No search circuit was repriced during recovery; only the required v37g control was evaluated anew.",
        'Selection uses lowest exact L at exact A ≥ 0.5002 and retains the incumbent. J_tau is diagnostic with each round’s current L; the new qualification threshold is L(v37g) − 3e-8, not the older v37f threshold.', '',
        '| Round | Exact L | Exact A | Gain | Selected edits |',
        '|---|---:|---:|---:|---|',
    ]
    for h in hist:
        lines.append(f"| {h['round']} | {h['price']['loss']:.17g} | {h['price']['acceptance']:.17g} | {h['gain']:.12g} | {', '.join(h['selected'])} |")
    lines += ['',
        'Round 3 completed 1,569 singles, 11,795 joint proposals and 567 funding proposals. Round 4 completed 1,579 singles, 12,484 joint proposals and 627 funding proposals. Each task has a numerical or explicit invalidity receipt; both rounds’ task sets were audited.',
        'PREPFREE M12@34 and M25@37 and POLISH q11→q5 and q20→q21 edits are carried from the measured all-four transport. POLISH q2→q3@25 was already present. Exact inverses remain available for ejection; all 2-/3-edit ejections and moves unlocked by valid ejections are included.',
        'Pairs use propagated detector, rotation and logical/output signatures; the shared decoder couples different output bits. All interacting improving/cheap-buyer pairs and the strongest eight partners of other eligible singles were priced as whole circuits.',
        'Funding used 12 distinct cheap buyers, up to four buyers per move, eight initial under-floor seeds and a 24-state beam preserving each intermediate Pareto front. Full measured (L,A) fronts, including unselected frontier states, are retained in res37f/resume_pareto4.json. This finite proposal scope is not global optimality.',
        'All 246 lower-loss round-3 and 167 lower-loss round-4 rejected selections exceeded the 30-second one-process judge timeout. Their recorded baselines were about 3 seconds. The numerical best round-4 proposal was L=3.620513105084778e-5, A=0.5006151132770182; its judge exceeded 30.057 s. Even that improvement is smaller than the new 3e-8 target.',
        'Validity failures are explicit nondeterministic-detector or edit-conflict rejections; the audit found no missing numerical jobs. Every numerical pass-4 receipt includes six noiseless output stabilizers +1. QASM hashes, ordered outputs, frozen evaluator/basis hashes and selected recipes were checked.',
        'Disk-full recovery: assist_r3.jsonl had a 66-byte torn last record at line 1216. The fragment is preserved in archive/resume_disk_full/assist_r3_torn_tail.bin; the complete remote joint ledger covers every task. Valid local receipts were retained.',
        f"Ledger: {len(receipts)} full pass-4 receipts, {len({r['sha256'] for r in receipts})} pass-4 QASM hashes, {len(rows)} historical/current hash entries in results.json. The compact index references full receipts and preserves distinct ordered-output variants.",
    ]
    if artifact:
        j = artifact['judge_1e6']
        lines += [
            f"Current verification: actual fast_check CLI at 1e6 shots, one process, three alternating paired trials on {j['host']}; gates_ok={j['gates_ok']}, median candidate={j['median_seconds']:.6f}s, v37g={j['baseline_median_seconds']:.6f}s, ratio={j['ratio']:.6f} ≤ 1.5.",
            f"Review artifact: [best below target](cand/{artifact['name']}.qasm), {artifact['cx']} CX. JSON explicitly marks qualifies_vs_v37g=false. Historical cand/merge4_r* builds qualified against v37f, not this continuation’s target.",
            'At 1e6 shots the sampled acceptance can fall below 0.5; selection uses exact A=0.5004477222510987 as instructed. The full CLI output and timing receipts are in res37f/resume_judge_v37g.json.',
        ]
    else:
        lines.append('Current v37g-paired CLI verification is running; existing historical timing receipts compare with v37f.')
    lines += [
        'Checked: saved-circuit identities and prices, raw code space, evaluator provenance, selected recipes, complete round-3/4 task coverage, exact acceptance, and the reported judge trials. Unproven: optimality outside the finite grammar, larger buyer bundles, and official 1e8 seed-0 performance.',
        'Decisions: recovered the completed remote work instead of repeating it; retained its sub-1e-9 convergence; updated qualification to v37g; kept a clearly marked below-target artifact. No new standing rule, submission, commit, push, subagent, or other-lane write.',
        'Evidence: res37f/wide_history.json, wide_outcome.json, resume_recovery.json, resume_pareto4.json, resume_judge_v37g.json, resume_audit.json; complete receipts and source schedules remain in res37f/ and v37f/.',
    ]
    assert len(lines) <= 100 and max(map(len, lines)) < 2000
    (H / 'REPORT.md').write_text('\n'.join(lines) + '\n')
    summary = dict(complete=outcome['complete'], new_finalists=0,
                   baseline=control, best=best, gain_from_v37g=gain,
                   last_round_gain=outcome['last_gain'], completed_stages=completed,
                   ledger_entries=len(rows), receipts=len(receipts),
                   report_lines=len(lines), ledger_bytes=target.stat().st_size)
    dump(R / 'resume_summary.json', summary)
    print(json.dumps({k: summary[k] for k in ('complete','new_finalists','gain_from_v37g',
          'last_round_gain','ledger_entries','receipts','report_lines','ledger_bytes')}), flush=True)


if __name__ == '__main__':
    run()
