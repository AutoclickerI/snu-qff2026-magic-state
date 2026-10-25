"""Hash-keyed evidence ledger and bounded, explicit research coverage report."""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import json,hashlib,re
from pathlib import Path
H=Path(__file__).resolve().parent
receipts=[json.loads(p.read_text()) for p in sorted((H/'logs').glob('*.receipt.json'))]
byname={r['stem'].split('/')[-1]:r for r in receipts}
verification=json.loads((H/'verification.json').read_text())
abstract=json.loads((H/'abstract_verification.json').read_text())
audit=json.loads((H/'coefficient_audit.json').read_text())
ledger={}
for r in receipts:
    p=H/(r['stem']+'.qasm');sha=hashlib.sha256(p.read_bytes()).hexdigest();assert sha==r['sha256']
    z=ledger.setdefault(sha,dict(qasm_paths=[],experiments=[]))
    if str(p.relative_to(H)) not in z['qasm_paths']:z['qasm_paths'].append(str(p.relative_to(H)))
    z['experiments'].append(r)
for j in verification['judge']:ledger[j['sha256']]['official_grid_check']=j
for j in abstract:ledger[j['sha256']]['abstract_raw_correctness']=j
(H/'results.json').write_text(json.dumps(ledger,indent=2)+'\n')
counts=[]
for p in sorted((H/'logs').glob('search*.log')):
    m=re.search(r'COUNTS (\{[^\n]+\})',p.read_text())
    if m:counts.append(dict(file=p.name,**json.loads(m.group(1))))
canonical=sum(r['canonical'] for r in counts if 'disconnected' not in r['file'])
assignments=sum(r['measurement_assignments'] for r in counts)
oracle=[json.loads(l) for p in (H/'logs').glob('oracle*.jsonl') for l in p.read_text().splitlines() if l]
(H/'coverage.json').write_text(json.dumps(dict(encoded_counts=counts,canonical_schedules=canonical,measurement_output_assignments=assignments,oracle_bounds=oracle),indent=2)+'\n')
fmt=lambda x:f'{x:.10g}'
L=['# ENDSEARCH','',
'Verdict: **no admissible improvement over v37b**. Systematic search found a useful five-block path and a square-with-leaf round, but all three leading grid-free suffixes lose after the tested grid preparation/routing. No submission, commit, push, or other-lane modification.',
'',
f'Baseline reproduced exactly: v37b L = {byname["incumbent_v37b"]["loss"]:.17g}, A = {byname["incumbent_v37b"]["acceptance"]:.16g}. All L values below are expected conditional 1−F at p=0.001, not 1e8-shot draws.',
'',
'| Template / representative | Blocks including D | Per-index graph | Exact c2 (p²) | All-orders tail L | Tail A | First-order |',
'|---|---:|---|---:|---:|---:|---|']
for label,title,graph in [('square','Enumerated square, A→C shear','4-cycle'),('tree','New independently verified path','E–A–D–B–C'),('square_leaf','New square with B-check leaf','4-cycle + leaf'),('unmeasured','Retained helper control','triangle + two leaves; needs motion')]:
    r=byname['chosen_round_'+label];t=r['metadata']['template'];L.append(f'| {title} | {t["n"]} | {graph} | {r["exact_second_order_p2"]:.8f} | {fmt(r["loss"])} | {fmt(r["acceptance"])} | zero harmful singles |')
for n in (3,4):
    rr=[r for r in receipts if r['stem'].startswith('builds/round_') and r['metadata']['template']['n']==n and r['metadata']['template']['graph']=='tree']
    r=min(rr,key=lambda r:r['loss']);L.append(f'| Best priced {n}-block tree representative | {n} | tree | {r["exact_second_order_p2"]:.8f} | {fmt(r["loss"])} | {fmt(r["acceptance"])} | zero harmful singles |')
r=byname['physical_5_1'];L.append(f'| Physical GHZ checker variant | 5 | path | {r["exact_second_order_p2"]:.8f} | {fmt(r["loss"])} | {fmt(r["acceptance"])} | zero harmful singles |')
L+=['','The new path uses A,E = |+_L>, B,C = |0_L>: tick 0 D→A ∥ B→C; tick 1 A→E ∥ B→D. Read C in Z at tick 1 and A,B in X plus E in Z at tick 2. Use all read-block syndrome rows, logical X_A and logical Z_C. It catches every single-block logical resource Pauli and needs no separate logical verification helper.','',
'| Full v37b-prefix experiment | Grid-free L | A | Gain vs v37b | Best tested grid L | Grid A | Official gates |',
'|---|---:|---:|---:|---:|---:|---|']
for label in ('square','tree','square_leaf'):
    r=min((byname['suffix_'+label],byname['suffix_'+label+'_jit']),key=lambda r:r['loss'])
    g=byname['grid_square_v37b'] if label=='square' else min((r for name,r in byname.items() if name.startswith('grid_'+label+'_')),key=lambda r:r['loss'])
    L.append(f'| {label} | {fmt(r["loss"])} | {fmt(r["acceptance"])} | {fmt(byname["incumbent_v37b"]["loss"]-r["loss"])} | {fmt(g["loss"])} | {fmt(g["acceptance"])} | format/class/correctness pass; acceptance fails |')
r=min((byname['suffix_unmeasured'],byname['suffix_unmeasured_jit']),key=lambda r:r['loss']);h=byname['hop_unmeasured'];L += ['',f'Unmeasured-helper full suffix: L = {fmt(r["loss"])}, A = {fmt(r["acceptance"])}; fails the grid gate. A concrete one-cell helper move reusing the measured A block costs two CXs, reset and a zero read: tail c2 = {h["exact_second_order_p2"]:.8f} p², L = {fmt(h["loss"])}, A = {fmt(h["acceptance"])}; three extra native ticks. It fits 35 qubits and changes the triangle into a square-with-leaf interaction graph.','',
'The table uses the better original/JIT preparation schedule per family. JIT prepares each block immediately before its first coupling, instead of waiting for all blocks before starting the round. It improves the square-with-leaf from 3.551030177e-5 to 3.394450812e-5 and the path from 3.518330590e-5 to 3.407979867e-5. These improvements and their grid variants were implemented and priced.',
'Grid facts: seven disjoint path gadgets need ≥1 data hop from v37b; square-with-leaf gadgets need ≥3 when each data qubit moves at most one grid edge (CP-SAT OPTIMAL in that domain). The original global preparations finish at R104/R120 in the shallowest builds. Eight GF(2)/Steiner syntheses per layout were built; the two shallowest and their JIT variants were priced. These are failed constructions, not lower bounds on optimal routed preparations.',
'The square grid test reuses SQUARE’s completed routing and storage guards, replaces its prefix by v37b’s causal prefix, and changes the square shear/readout. SQUARE and TERMINAL stayed read only.','',
'Coverage and bounds:','',
f'- Encoded space: {canonical:,} symmetry-reduced schedules; {assignments:,} measurement/output assignments. All nonempty directed-CX matchings of depth 2–4 on 2–5 blocks; every output choice; X/Z/unmeasured endings; earliest final reads; connected AND disconnected interaction graphs. All pure logical CSS resources (2,5,16,67 subspaces for 1–4 ancillas), including encoded Bell/GHZ. Full-rank candidates receive the ideal Choi/detector/frame solve or an exact-c2 pruning test. Rank-0/3 assignments are counted but remain outside this frontier, under the universal bound below. Pauli signs/cosets are noise-covariant representatives.',
'- Physical resources: all products of encoded 0/+, literal 0^7/+^7, Z/X GHZ, plus disjoint physical Bell-paired blocks; connected 3-block templates through four ticks and 4–5-block templates through two ticks, with D retained. Full physical CSS stabilizers derive every deterministic detector and frame. Counts and survivors are in physical_*.log/jsonl.',
'- The larger physical-resource remainder is bounded by the enumerated zero-record-fault oracle, independent of resource type/entanglement: every pair of zero-record faults must pass any deterministic detector and any affine frame. Their positive c2 contribution bounds every first-order-safe implementation from below (MODEL.md). All connected/disconnected graphs and output choices through four CX ticks are included in the bound.',
'- In the full-rank uniform-transversal family the oracle minimum is 25.66666667 p²; every tree is ≥27.20666667 p² and every unmeasured-partner ending is ≥28.74666667 p². Thus no tree reaches the requested ≤26.7 p² target, even with arbitrary perfect resources. These are second-order bounds, not finite-p optimality certificates.',
'- Scope of that terminal bound: every resource is present before tick 0, with idle noise charged from tick 0. It does not bound interleaved just-in-time nontransversal preparation. The full-suffix JIT prices include that preparation and can improve the realizable circuit without contradicting the terminal bound.',
'- Every stored connected frontier graph was tested for fixed-cell grid embedding and one initially-empty-cell move. None of the ≤26.7 p² representatives requires a hop: they contain a unit-square core. Splitting one square vertex by one move creates an odd five-cycle, so it cannot remove that core on a bipartite grid. The separate reusable-cell hop above is explicitly priced.',
'- Space 3 includes all retained-helper CX/affine-frame endings in the exhaustive sweep and physical-resource tests. General Clifford+T/nonlinear lookup/coherent syndrome recovery, nonuniform cross-index gadgets, intermediate read/reset reuse beyond the priced hop, and partial-rank checks are not enumerated or excluded. They retain BOUND’s certified all-orders L ≥1.3657850790536654e-5; measured-partner cases retain ≥2.2742699650371855e-5. Their local/interaction search becomes much larger and the per-index Pauli-rate reduction no longer applies. A bound below v37b leaves these families open.',
'- The search frontier is exact at second order for the stated family; finite-p prices are for saved frontier representatives and selected ties, not a proof of global all-orders optimality. The real-input prefix was cut before tick 44, and physical preparations were assigned to released cells and scheduled as late as dependencies allow.','',
'Verified versus inferred:','',
f'- Verified: {sum(x["model_difference"] is not None for x in audit)} independent explicit fault-pair Taylor coefficients agree with the search model within {max(abs(x["model_difference"]) for x in audit if x["model_difference"] is not None):.3g}; the hop coefficient is computed separately, for {len(audit)} audited tails in total. All scored tail/frontier representatives have zero harmful singles. Idle derivatives and FRAME records are included. The finite-p hop pair sum was corrected during this audit; its all-orders price did not change.',
'- Verified: organizer tprep.exact.verify gives raw noiseless infidelity 0 for all four full-suffix families, their JIT variants, and the hop, over every measurement branch. For abstract grid-free circuits this is a correctness test only, not a format-pass claim.',
'- Verified: three complete grid circuits pass official format/class/correctness at 1e6 shots and fail acceptance; their sampled losses agree with the all-orders prices within sampling uncertainty. Hashes and ordered outputs are recorded. v37b reproduces the supplied exact L/A.',
'- Inferred: a better local preparation/layout could recover a grid-free gain. No admissible finalist or complete preparation near the universal floor was found; no grid-optimality claim is made. No 1e8-shot run or official submission was warranted.',
'',
'Files: results.json is keyed by QASM SHA256, with multiple experiments per circuit; cand/ contains the four full-suffix families, their JIT variants and tested grid finalists. manifest.json, choices.json, coverage.json, geometry.json, grid_manifest.json and coefficient_audit.json expose search coverage. logs/ contains process receipts, all-orders prices, counts and failures; builds/ saves every priced witness. MODEL.md gives the terminal-model derivation and explicit open families. src/search.cpp, src/physical.cpp, build_candidates.py, grid_new.py, price.py and audit_coeff.py reproduce the work.',
'Execution: all research computation ran on tom, OMP/BLAS/MKL threads = 1, at most three simultaneous compute workers; capacity waits used existing process exits. No subagents, GPUs, credentials, commits, pushes or submissions.']
assert len(L)<=100 and all(len(s)<2000 for s in L),(len(L),max(map(len,L)))
(H/'REPORT.md').write_text('\n'.join(L)+'\n')
print(json.dumps(dict(report_lines=len(L),hashes=len(ledger),receipts=len(receipts),canonical=canonical,assignments=assignments)),flush=True)
