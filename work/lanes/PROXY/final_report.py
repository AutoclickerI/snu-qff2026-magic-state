"""Append final measured results to the incrementally maintained lane report."""
from pathlib import Path
import json,math,runpy
H=Path(__file__).resolve().parent
runpy.run_path(str(H/'report.py'))
text=(H/'REPORT.md').read_text();text=text.split('## Part 2')[0]
v=json.loads((H/'small_validation.json').read_text())
text+=f"Additional complete small-round validation: an ideal verified Steane round plus three physical tail depolarizing channels, all 64 physical branches: brute conditional loss {v['brute_all_orders']:.12g}; all-orders X/Y {v['xy_all_orders']:.12g}; acceptance {v['acceptance']:.12g}.\n\n"
g=json.loads((H/'gmodel_reference.json').read_text())
text+='### Explicit v11/v12-family GModel comparison\n\n| Schedule | Old | Corrected order 2 | All orders | Recorded full-circuit MC |\n|---|---:|---:|---:|---:|\n'
for key,mean in [('v11',1.2189e-4),('v12_normalized',1.1327e-4)]:
 r=g[key];text+=f"| {key} | {r['old']:.9e} | {r['second']:.9e} | {r['all_orders']:.9e} | {mean:.7e} |\n"
text+='\nThe v11 MC is the FINDINGS mean over 100 redraws; v12 is the requested three-seed mean. GModel normalizes the initial Bell preparations and resets retained ancillas, so mapping the actual v12 coupling schedule into GModel discards its boundary improvements. Both old and corrected GModel proxies rank this comparison backwards. The X/Y correction fixes ambiguous logical-fault pairing; it does not repair an incomplete full-circuit noise boundary. `reference_cycle_proxy.json` uses the actual v12 boundary with an ideal noiseless pre-stage.\n\n'
errors=json.loads((H/'part1_infeasible.json').read_text())
text+=f"The additional verifier scan explicitly rejected {len(errors)} recipes whose verification gates overlap their encoders or whose probes are nondeterministic; details are in `part1_infeasible.json`. The old 6.72e-5 two-verifier summary has no uniquely recorded builder parameters; the report instead enumerates all reproducible default single- and double-verifier recipes, including the later recorded 5.55819e-5 best pair. No matching recipe is invented for that older rounded summary.\n\n"
text+='The all-orders calculation also qualifies the ST_AV claim: with standard A and D, its order-2 value stays 2.8986091e-5 as input noise increases from 0 to 0.02, but its exact all-orders loss increases from 2.94006796e-5 to 4.48388598e-5. Likewise, teleport and star rounds agree at order 2 but differ slightly at higher orders. These are finite-noise effects, not new first-order failures.\n\n'
geo=json.loads((H/'relocations.json').read_text());rs=[]
for shard in (0,1):rs+=json.loads((H/f'search_results_{shard}.json').read_text())
valid=[r for r in rs if r.get('check',{}).get('passed')]
text+='## Part 2 — completed support filtering and physical schedule search\n\n'
text+='All 28 independent X triples and 28 independent Z triples were enumerated: 784 pairs. At fixed data positions, both the original layout and A1/v12 layout admit only the original support pair. Every other weight-four Z support lacks an adjacent Bell pair reaching its four data cells. Allowing one-hop X leaves adds no new support pair.\n\n'
text+=f"Extended filter: {geo['routes']:,} collision-free one-hop data placements; {geo['layouts_with_Z_basis']} admit an adjacent Bell Z basis. Pair counts are **784 → {geo['pairs_after_Z_adjacency']} after Z adjacency → {geo['pairs_after_X_adjacency']} after X adjacency → {geo['pairs_after_ancilla']} after distinct ancilla availability → 1 after `relaxed.valid()` and Stim determinism**. The surviving pair is the original basis, with {geo['physical_placements']} physical placements. This is an exhaustive statement only for adjacent Bell pairs, one-hop X leaves and one fresh-cell hop per data qubit; arbitrary longer routes and Z-cat extensions are untested.\n\n"
text+=f"Searched {len(rs)} configurations (all 16 placements, all eight Bell readout orientations and optional X leaves). {len(valid)} produced circuits passing the full judge at 10^6 shots; all saved candidate QASM/JSON pairs contain this receipt. CP-SAT generates starts, then 3,000-proposal anneals use the exact all-orders Clifford X/Y objective. An additional 48 chains, 12,000 proposals each, refine the submitted v12 schedule and its best first continuation. Rejected nondeterministic schedules are explicitly excluded; no detector XOR relabel is counted as a support change.\n\n"
text+='The submitted `v12_L5lns12_r86.qasm` is the prefix source. Its 170 literal pre-stage lines, representing 137 native operations, keep their original native times. In particular, the three retained X measurements remain intact. Commuting Z couplings may precede final pre-stage T† gates exactly as in v12. Every saved candidate audits these native times and passes the real judge, including grid adjacency. The surrogate commutes the noiseless pre-stage earlier and omits its noise; only full-circuit exact/MC results establish performance.\n\n'
text+='All 48 refinement chains converged to the same emitted schedule. To test whether the surrogate missed a better nearby full circuit, 1,915 single-node shifts, conflict swaps and two-node swaps were enumerated. All 54 distinct feasible/deterministic neighbors passed the judge and were evaluated with the full second-order evaluator; none beat the winner. `neighbor_049` returns the original v12 physical schedule (its emitted gate order and classical bit numbering differ).\n\n'
text+='### Full-circuit finalists\n\n| Candidate | Exact order 2 | Exact through order 3 | exp(-A1) | First order |\n|---|---:|---:|---:|---:|\n'
third=[]
for p in H.glob('*.third.json'):third.append(json.loads(p.read_text()))
third.sort(key=lambda r:r['third'])
for r in third:text+=f"| {r['name']} | {r['second']:.8e} | {r['third']:.8e} | {r['exp_A1']:.5f} | {r['first']:.2g} |\n"
text+='\nThe unmodified `EVAL/exact2.py --third` CLI generated each `.third.log`; only wrapper cache paths and worker counts were configured. Order-2 screening uses the same evaluator with batched expectation caching.\n\n### Three-seed official MC\n\n| Candidate | seed 0 | seed 1000 | seed 2000 | Mean ± MC SEM | Δ vs 1.1327e-4 | Acceptance mean |\n|---|---:|---:|---:|---:|---:|---:|\n'
mcs=[]
for p in H.glob('*.mc.json'):
 r=json.loads(p.read_text());mcs.append(r)
for r in sorted(mcs,key=lambda x:x['mean']):
 scores=[x['score'] for x in r['rows']];acc=sum(x['acceptance'] for x in r['rows'])/3
 text+=f"| {r['name']} | {scores[0]:.9e} | {scores[1]:.9e} | {scores[2]:.9e} | {r['mean']:.9e} ± {r['sem_mean']:.2g} | {(r['mean']/1.1327e-4-1)*100:+.3f}% | {acc:.7f} |\n"
text+='\nEach MC row uses `fast_check.check(text, data_qubits, shots=10**8, seed=s, procs=N)` for seeds 0/1000/2000: N=3 on zebra for `cycle_0058`, N=15 in owl Docker for the two neighbors. Separate `tprep.check` receipts at 10^6 shots are retained. No credentials were read and no submissions were made. All created scripts, candidates, caches and receipts are confined to this lane.\n\n'
assert {r['name'] for r in mcs}=={'cycle_0058','neighbor_006','neighbor_049'}
byname={r['name']:r for r in mcs};best=byname['cycle_0058']
text+='### Result and limits\n\n'
text+=f"The best new schedule moves **`cx q[4],q[10]` from native step 37 to 35**, commuting it ahead of the fixed `tdg q[4]` at step 36. Everything in the pre-stage remains fixed. Its measured three-seed mean is **{best['mean']:.9e}**, {(best['mean']/1.1327e-4-1)*100:+.3f}% versus the requested 1.1327e-4 target, so **there is no demonstrated improvement over v12**. The difference is smaller than MC uncertainty. Its seed-0 score is {best['rows'][0]['score']:.9e}, versus submitted r86's 1.126891519e-4. Third order predicts a small physical gain, which these three seeds do not establish.\n\n"
text+='`cycle_0058` and `neighbor_006` are the two best distinct new physical schedules by third order. The better-ranked `neighbor_049` is the original physical v12 schedule re-emitted with different simultaneous-gate order and classical labels, and is included as a baseline control, not claimed as a new cycle. The original r86 remains the preferred submitted text on the requested metric.\n\n'
text+='The retained five QASM/JSON pairs were rechecked at 10^6 shots and audited against their saved schedule and the submitted prefix (`artifact_audit.json`). All 2,564 other generated candidate files are preserved in the byte-verified `generated_candidates.tar.gz`; screening results remain directly readable. Searches are heuristic over schedules and exhaustive only over the stated local geometry/filter model. Longer routing, Z-only cat extensions and global schedule optimality remain unverified.\n\n'
text+='Primary implementation sources: [judge](../../../docs/reference/judge.md), [paired proxy](../../proxy2.py), [GModel](../me_layout/gmodel.py), [ordering validity](../DR/relaxed.py), [full exact evaluator](../EVAL/exact2.py), and [submitted v12](../../submissions/v12_L5lns12_r86.qasm). Results above are local measurements or enumerations; no literature-only performance claim is used.\n\n'
text+='Evidence: `part1_validation.json`, `small_validation.json`, `part1_rows.json`, `schedules_rescored.json`, `topology.json`, `relocations.json`, `prefix_audit.json`, `search_results_*.json`, `refine_results_*.json`, candidate `.json`, `.screen.json`, `.third.log` and `.mc.json`.\n'
(H/'REPORT.md').write_text(text)
