from common import *
import statistics
summaries={p.name.removesuffix('.split.json'):json.loads(p.read_text())['summary'] for p in HERE.glob('*.split.json')}
order=['v12_reference','extra1_s0','extra1_s1','extra1_s4','extra1_s8','extra1_pinned_s0','extra1_pinned_s4',
       'extra2_s4','extra2_pinned_s4','alap_ordered','alap_commuting','alap_best','central_verify_s0','central_verify_s4',
       'central_retain_s0','central_retain_s4','central_retain_pinned','late_verify_s0','late_verify_s4','all_verify_s0','all_verify_s4']
assert set(order)=={n for n,r in summaries.items() if r['passed']}
base=summaries['v12_reference'];audit={r['name']:r for r in json.loads((HERE/'suffix_audit.json').read_text())}
for name in order:
    assert audit[name]['suffix_relative_native_timing']
    assert (HERE/f'{name}.exact.json').is_file()
    assert all(json.loads((HERE/f'{name}.check.json').read_text())[k] for k in ('passed','format','class_ok','correctness','acceptance_ok'))
lines=['# PRE: acceptance spent on cultivation','',
       'Added double-cat checks do not pay in the measured families. The best one-addition candidate raises exact second-order loss by 8.96% and the three-seed judge mean by 13.20%. Its A1 increment is 0.15878, inside the proposed spare budget. The scheduling winner lowers second-order loss by 0.7567% for only ΔA1=0.00393, but the requested Monte Carlo runs do not establish a true-mean improvement over v12. Retain v12 on the measured three-seed criterion.','',
       'Baseline reproduced before variant scoring: **loss2=1.1219494706696269e-4, loss1=4.9032383092e-19, A1=0.370303793945133**, exp(-A1)=0.690524522. The supplied rounded targets match. `v12_reference.qasm` reconstructs v12 byte for byte.','',
       '25 full circuits have exact CLI receipts and judge checks at 1e6 shots; 21 pass, including the reference. Every row below passes format, class, correctness and acceptance. Four other two-addition schedules fail acceptance (0.490202–0.497099) and are excluded; their exact/check/split receipts remain available. The two valid two-addition circuits consume almost all acceptance and leave no room for the proposed next round.','',
       'All tables use the native judge schedule, with zero-based steps. **End** is the last cultivation operation; **D** is full circuit depth. v12 overlaps cultivation and its final cycle, so its cultivation ends at step 37 rather than the cited v11 boundary at 33. The ALAP winner delays some cultivation readouts until step 40 while keeping total depth 42. The saved LNS `npre=148` was an optimization cutoff: the actual final cycle begins at construction node 137. All 25 emitted native suffixes were compared against v12 for identical gates and relative timing (`suffix_audit.json`); classical bits were shifted for added checks.','',
       '## Exact results','',
       'Each name links to its QASM; the matching `.json` contains `data_qubits`, construction schedule, native schedule, source and hash. `.exact.log`/`.exact.json` are uncached `exact2.py` CLI output. First-order values below 9e-18, including tiny negative values, are floating-point zero. Δ is relative to the reproduced v12 loss2.','',
       '| Variant | CX | End / D | Exact loss2 | First order | Pre A1 | Total A1 | exp(-A1) | Judge acceptance | Δ loss2 |',
       '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
for n in order:
    r=summaries[n];delta=100*(r['loss2']/base['loss2']-1)
    if abs(delta)<1e-9:delta=0
    lines.append(f"| [{n}]({n}.qasm) | {r['CX']} | {r['pre_end_step']} / {r['depth']} | {r['loss2']:.8e} | {r['loss1']:.2e} | {r['construction_pre_A1']:.6f} | {r['A1']:.6f} | {r['exp_minus_A1']:.6f} | {r['acceptance']:.6f} | {delta:+.3f}% |")
lines+=['','## Stage attribution','',
        'A1 is summed directly from `ev.fp * (1 - ev.a_single)`. A fault pair contributes half its loss to each fault location, using `exact2.run` channel sensitivities. Gate/reset/readout channels belong to their construction stage. An idle interval is split using the steps returned by `ev.chan_label`, at the last cultivation operation on that wire. This handles the interleaved boundary without assigning all early final-cycle gates to cultivation. Cross-stage pairs are shared; these are additive attributions, not standalone-circuit infidelities. Same-channel normalization is below 8e-20 here.','',
        '| Variant | Pre A1 | Suffix A1 | Pre loss2 | Suffix loss2 |',
        '|---|---:|---:|---:|---:|']
for n in order:
    r=summaries[n]
    lines.append(f"| {n} | {r['construction_pre_A1']:.6f} | {r['construction_suffix_A1']:.6f} | {r['construction_pre_loss2']:.8e} | {r['construction_suffix_loss2']:.8e} |")
lines+=['',
        'For a literal single-time cutoff at each circuit’s End, the `.split.json` fields `pre_A1`/`suffix_A1` and `pre_loss2`/`suffix_loss2` provide that alternative temporal split; `construction_*` fields are the stage attribution above. For v12 the temporal split is A1=0.344106/0.026198 and loss2=3.306604e-5/7.912891e-5. Its construction split attributes 86.95% of loss2 to final-cycle locations. The temporal split changes sharply when harmless readouts move late, so it should not be interpreted as an isolated cultivation error rate. Every channel’s steps, A1, loss contribution and split fractions are saved.','',
        '## Judge Monte Carlo, 1e8 shots per seed','',
        'All four circuits pass every judge gate at seeds 0, 1000 and 2000 through unchanged `work/fast_check.py`. Means rank candidates; the seed-0 key is the score rounded to three significant figures. SEM below is the standard error of the three-seed mean.','',
        '| Variant | Seed 0 | Seed 1000 | Seed 2000 | Mean ± SEM | Mean acceptance | Seed-0 key |',
        '|---|---:|---:|---:|---:|---:|---:|']
mcs={}
for n in ('v12_reference','extra1_pinned_s4','alap_commuting','alap_best'):
    m=json.loads((HERE/f'{n}.mc.json').read_text());mcs[n]=m
    assert len(m['rows'])==3 and all(r['passed'] and r['shots']==100000000 for r in m['rows'])
    scores=' | '.join(f"{r['score']:.8e}" for r in m['rows'])
    lines.append(f"| {n} | {scores} | {m['mean']:.8e} ± {m['mean_sem']:.2e} | {statistics.mean(r['acceptance'] for r in m['rows']):.6f} | {m['rows'][0]['score']:.3g} |")
lines+=['',
        'The best exact ALAP candidate’s mean is 0.606% worse than v12 in these samples; the difference is only 0.76 combined standard errors if estimated as independent, so its true-mean advantage remains unresolved. Its seed-0 key improves from 1.15e-4 to 1.13e-4. The added-check mean is 13.20% worse, a clear loss. No submissions were made.','',
        '## Constructions and reproducibility','',
        '- `extra1_*` adds one upstream `make_chunk_d3_double_cat_check`; `extra2_*` adds two. These reuse `cultiv_port.run_chunk(..., s_to="Tswap")`. Non-pinned schedules repack the full cultivation prefix against fixed suffix deadlines; pinned schedules additionally preserve v12’s original last-check timing, isolating the effect of inserting an earlier check. `build_extra.py` and `build_pinned.py` generate them.',
        '- `central_verify` repeats the central cat MX with a parity detector before the existing reset. `central_retain` replaces that reset with a second native MX and retains the accepted X state; the pinned version changes exactly that operation at its existing time. `late_verify` repeats all six terminal cat readouts; `all_verify` repeats both central and terminal readouts. `build_readouts.py` generates the scheduled versions. The pinned central replacement leaves loss2 unchanged and spends ΔA1=0.001333.',
        '- `alap_ordered`, `alap_commuting` and `alap_best` are the winners of ordered reverse scheduling, commuting reverse scheduling, and subsequent local/LNS search. Forty distinct greedy schedules and 400 local proposals were exactly screened with `Eval/run`, batching identical Engine tables; all reported shortlist circuits were then rechecked through uncached `exact2.py`. `alap_best` comes from `alap_lns_0387`, selected for minimum A1 among loss2 ties within 1e-15. This is a finite search, not an optimality proof.',
        '- `measure.py` validates and decomposes saved exact CLI output; `audit_suffix.py` checks the compiled suffix; `monte.py` runs all requested seeds; `write_report.py` creates this report. Use the repository `.venv/bin/python`, cwd `work/lanes/PRE`, bytecode disabled, numerical threads=1, and `nice -n 5`. Main exact and MC pools used eight workers, the scheduling lane four. Caches and all writes remain inside PRE.',
        '',
        'Example exact command from PRE: `nice -n 5 /home/jihoon/competitions/quantumn/.venv/bin/python ../EVAL/exact2.py alap_best.qasm --procs 8 --top 0 --json alap_best.exact.json`. MC: `nice -n 5 /home/jihoon/competitions/quantumn/.venv/bin/python monte.py alap_best --procs 8` with `PYTHONDONTWRITEBYTECODE=1` and thread caps set.',
        '',
        'Primary implementation sources: [cultiv_port](../../cultiv_port.py), [upstream double-cat construction](../../../upstream/magic-state-cultivation/src/cultiv/_construction/_cultivation_stage.py), [judge schedule/noise](../../../upstream/snu-qff2026-problem/tprep/noise.py), [exact evaluator](../EVAL/exact2.py), and [v12 source schedule](../L5_precycle/combined_lns_0012.json). These are local source inspections and measured results; no literature-only performance claims are used.','']
(HERE/'REPORT.md').write_text('\n'.join(lines))
(HERE/'results.json').write_text(json.dumps(dict(baseline=base,valid=[summaries[n] for n in order],
     rejected=[r for r in summaries.values() if not r['passed']],monte_carlo=mcs),indent=2)+'\n')
print(f'Wrote REPORT.md: {len(order)} passing rows, {len(summaries)-len(order)} rejected, {len(mcs)} Monte Carlo confirmations')
