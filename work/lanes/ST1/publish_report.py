"""Publish the completed lane report from final receipts, preserving raw evidence."""
from pathlib import Path
import json,re,gzip,hashlib
H=Path(__file__).resolve().parent
exact=json.loads((H/'st1_final.reference_cubic.json').read_text());ao=json.loads((H/'st1_final_canonical_sparse_result.json').read_text());meta=json.loads((H/'st1_final.json').read_text());judge=(H/'st1_final.judge.log').read_text();mc=(H/'st1_final.mc3.log').read_text();assert 'passed=True'in judge
mean=float(re.search(r'st1_final mean (\S+)',mc)[1]);seeds=[(int(s),float(v),float(acc))for s,v,acc in re.findall(r'st1_final (0|1000|2000) (\S+) .*?acc (\S+)',mc)];assert [s for s,v,acc in seeds]==[0,1000,2000]
acc=float(re.search(r'acc=(\S+)',judge)[1]);seconds=float(re.search(r'\(([\d.]+)s, 1 procs\)',judge)[1]);assert exact['total']<4.8e-5 and abs(exact['c1'])<1e-12 and acc>=.5 and seconds<=20
old=(H/'REPORT.md').read_text()
if not(H/'measurements_to_final.md.gz').exists():
 with gzip.open(H/'measurements_to_final.md.gz','wt')as f:f.write(old)
if(H/'owl_measurements_0055.md').exists():
 with gzip.open(H/'owl_measurements_0055.md.gz','wb')as f:f.write((H/'owl_measurements_0055.md').read_bytes())
 (H/'owl_measurements_0055.md').unlink()
(H/'st1_final.allorders.json').write_text(json.dumps(ao,indent=2))
result=dict(stem='st1_final',sha256=hashlib.sha256((H/'st1_final.qasm').read_bytes()).hexdigest(),exact=exact,allorders={k:ao[k]for k in('loss','acceptance','conditional_loss_kernel_omission_bound')},judge=dict(passed=True,shots=1000000,seed=0,acceptance=acc,seconds=seconds),mc3=dict(shots_per_seed=100000000,seeds=[dict(seed=s,loss=v,acceptance=a)for s,v,a in seeds],mean=mean),native=dict(R_A=meta['R_A'],R_BC=meta['R_BC'],R_BD=meta['R_BD'],depth=meta['native_depth'],cx=meta['cx']))
(H/'st1_final.result.json').write_text(json.dumps(result,indent=2))
report=f'''# ST1

Status: **SUCCESS — the strict4.8e-5 exact screen, judge/acceptance/runtime gates and MC3 are complete.** Final delivery: `st1_final`. No submission, commit or push. No global optimum is claimed.

## Best complete circuit

[QASM](st1_final.qasm) · [judge metadata](st1_final.json) · [native operation plan](st1_final.plan.json) · [combined receipt](st1_final.result.json).

| Quantity | Verified result |
|---|---:|
| Exact second order | {exact['second']:.15g} |
| Exact cubic correction | {exact['third']:.15g} |
| Exact total | **{exact['total']:.15g}** |
| c1 | {exact['c1']:.6g} |
| exp(-A1) | {exact['exp_minus_A1']:.12f} |
| All-orders loss | **{ao['loss']:.15g}** |
| All-orders acceptance | {ao['acceptance']:.12f} |
| Unchanged1e6-shot seed0 judge | **PASS**, acceptance {acc:.6f} |
| Zebra single-process speed | **{seconds:.1f}s /1e6** |
| MC1e8 seeds0/1000/2000 | {' / '.join(f'{v:.6e}'for s,v,a in seeds)} |
| MC3 mean | **{mean:.6e}** |
| Native B verification / B→D / final readout | **38 /39 /40** |
| Native depth / CX | **41 /212** |

The requested threshold is met by the exact third-order screen. The all-orders expectation is slightly above4.8e-5. Final ranking is consistent across exact cubic and all orders; individual Monte Carlo draws retain their sampling noise. [Independent cubic](st1_final.reference_cubic.json), [all orders](st1_final.allorders.json), [judge](st1_final.judge.log), [MC3](st1_final.mc3.log). The independent exclusive-channel enumeration agrees with Fourier moments within{abs(exact['moment_difference']):.2g}; all producing processes exited successfully.

## What changed and provenance

The winning branch reuses [ENDSTATE's complete new geometry](../ENDSTATE/REPORT.md), then applies ST1 full-objective timing, physical echoed checks, measured-Z initializations and terminal readout synthesis. It keeps the logical cultivation construction and its checks. The imported v30f prefix already contained the blue XZ check; no duplicate blue check was added. Credit for the new placement and56-CX correlated B/C resource belongs to ENDSTATE.

Versus v23h_c2c9, the prefix embedding, data routes, A/B/C placement/preparation and complete schedule change. The round advances from45 to38. Nine coherent data hops lead to a native9-CX A and the56-CX B/C resource. The final count is78 prefix +18 hops +9 A +56 B/C +21 round +26 echo +4 terminal CX =212.

Final D/A/B/C in code order:

- D: `[8,26,19,22,10,28,16]`
- A: `[14,20,13,21,9,27,15]`
- B: `[2,32,25,23,4,34,17]`
- C: `[3,33,31,29,5,35,11]`

All seven D→A and B→C contacts are at38, B→D at39. Terminal CX35→29,5→11,33→27 and A13→q7 copy fit at39; involved Z readouts move to40. Every detector parity is conjugated exactly, and the copy adds a consistency detector. The final data tail gains no step.

The last gain is an interaction between edits: removing the weak q26–q32 Z echo frees q32 from an X-basis helper lifetime, permitting a checked measured-Z B initialization. This improves4.8006975e-5 to4.7844375e-5 while retaining acceptance margin. Thirteen echoed checks and eleven measured-Z initialization edits remain. The native plan contains actual timings; intermediate descriptor times are proposal provenance.

## Model and exact objective loop

`redesign.py`/`c4_design.py` use CP-SAT variables for all48 prefix embeddings, independent reset-segment cells, operation times, code automorphisms, per-wire paths, encoder stages and round contacts. Explicit2D nonoverlap covers complete reset-to-release lifetimes. Prefix relocation macros move data before late cultivation contacts and retarget later CX/T-dagger operations. Data hops use two CX plus source checking; block teleports use one CX and exact record-frame transport. Prefix releases and A/B/C roles/cells are joint variables within each recorded model's bounds.

Every proposed complete circuit is emitted and priced by exact2's full physical fault model and exact second+cubic contraction. Only deterministic noiseless acceptance and |c1|<1e-12 receive a cubic rank. No incompatible boundary cache is reused. Depth/CX/exposure objectives generate geometric proposals only; complete physical loss ranks them.

`moments_gradient.py` differentiates the complete conditional cubic objective. `zero_idle.py` includes zero-probability channels for newly opened waits. `gradient_retime.py` converts pair/triple sensitivities into a trust-region CP-SAT timing objective and reprices every emitted proposal. Twelve finite-difference checks agree within2.23e-14; the Euler identity and all existing channels are verified. Radius-five feedback finds no improving move on the final circuit within its fixed per-wire order and tail.

`echo_search.py`, `watch_search.py`, `readout_search.py` and `repair_acceptance.py` enumerate physical instrument edits, evaluate full circuits, compose measured improvements and reprice acceptance repairs. Measured/reused states retain2p/3 noise. The final protocol does not use acceptance as a ranking reward.

`synth_a_decoder.py` jointly synthesizes A's initial X/Z basis, native CX layers and destructive X flag. Binary state matrices constrain its rank-four X space to Steane |+L>; source releases, data contacts, nonoverlap and readout deadlines are explicit. The expanded model retimes the complete fixed-route incoming boundary within±3 steps. All returned circuits receive full exact fault pricing.

Final gates use unchanged tprep/fast_check and the prescribed MC3 script; its snapshot hash matches MAIN. The sparse all-orders evaluator is a byte-identical MAIN snapshot, with only output/cache paths redirected inside ST1. All-used-qubit barriers and no FRAME/POSTSELECT satisfy its scope.

## Searched families and measured mechanisms

| Bounded family | Result and scope |
|---|---|
| ENDSTATE new R38 import | 5.57724343e-5 exact; source all orders5.61375002e-5. |
| Full exact timing | 5.42299221e-5 exact; all orders5.46065202e-5; MC3 mean5.376741e-5; judge PASS/.576983/3.0s. |
| First protected redesign, `st1_r38_a` | 4.95554025e-5 exact; all orders4.98241246e-5; MC3 mean4.989109e-5; judge PASS/.526458/3.6s. |
| More protection, `st1_r38_b` | 4.93919346e-5 exact; all orders4.96468091e-5; MC3 mean4.943747e-5; judge PASS/.509509/2.9s. |
| Transported-T boundary, `st1_boundary_d` | 4.91080882e-5 exact; all orders4.93392204e-5; MC3 mean5.014853e-5; judge PASS/.502472/3.6s. Native round38. Its precursor failed measured acceptance .499855; reverting a weak q25 initialization repaired it. |
| Terminal readout and initialization co-design | Final result above. Weak protection removal opens the better q32 initialization; the full composition is measured. |
| Native9-CX B +two transfers +two four-body checks | Ideal encoded Bell/stabilizers and harmful encoder X singles pass. Complete circuits have c1≈0 but lose badly from their realized preparation/movement exposure. |
| Two-check package, fixed cats13 prefix, A8, ≤3 A moves, ≤5 data hops, nine package translations/all48 prefix embeddings | OPTIMAL minimumR48 within model. Best exact3.436799e-4, proxy .462392: acceptance failure. |
| Two-check package with early q20→26/release20 and A9 | OPTIMAL minimumR48 within model; best exact2.657416e-4 atR55, proxy .464938. Timing optimum is not an exact-loss optimum. |
| Two-check package with free reset-segment prefix cells, R≤55 | UNKNOWN600s, no witness; no infeasibility claim. |
| C4 staggered B/data contacts | 1.199375e-3 →1.101055e-3 after timing; judge correctness passes, acceptance .495053 fails,4.0s. Post-A output-data waiting is the measured failure. Removing that idle counterfactually gives9.83855e-5, not a physical gain. |
| C4 one-endpoint neighbourhood | Best exact5.721380e-4, proxy .478228;32 exact-priced witnesses. The tested neighbourhood improves but still fails. |
| Twelve-CX path B, top-edge endpoints, ≤4 B moves/≤5 data hops, final window2,R≤60 | Solver INFEASIBLE64.66s for that fixed path/end geometry. Interior/release26 variants UNKNOWN600s. |
| Separate C7 catalog label0, all48/free reset-segment prefix,≤6 data hops,one block move | OPTIMAL minimumR69; representative6.953857e-4, proxy .263710, measured acceptance .264044 fails. No pre-round idle gives6.69457e-5; also removing move noise4.58351e-5. These are overlapping counterfactuals. |
| Direct-C preparation on final cells | OPTIMAL minimumR55 in the fixed catalog; best after timing2.436781e-4, proxy .404938. Saves six transfers; exposure still loses. |
| Existing A encoder +two-CX X flag | Seven corrected one-step-delayed orientations lose; best6.35461e-5, after timing5.88918e-5. Extra waiting outweighs the tested flag. |
| Joint A/decoder synthesis atR38, cap12, fixed routes and±3 incoming timing | Both tested logical-X supports return INFEASIBLE. No-decoder control is SAT with9CX,c1≈0,exact4.96532e-5. Scope excludes different routes/roles/prefix topology. |
| Joint A/decoder synthesis at realR39 |24 complete feasible9-CX encoder witnesses, all above the R38 finalist. Their extra waiting prevents a win; no universal decoder closure is claimed. |
| Proposed6→7 and14→15 terminal cat/hop fusions | Construction rejected: the final cultivation interactions use different cat cells and the required MX/reset pattern is absent. No scored circuit and no physical family closure. |

The output-idle pair polynomial is independently checked:0.0008801937654966753 versus full propagation0.0008801937654966752. This informed synchronous contacts/final-window cuts; it never replaced full-circuit ranking.

## Verification corrections and limits

- Beyond signed64 detector bits, `detector_order.py` applies ST2's verified reference-only ordering. It checks the complete physical fault-mask permutation, probabilities/channels/rotations/output signatures, commuting projectors, ideal acceptance and every single table. Physical QASM remains unchanged. A68-detector redundant-row control exactly matches the48-detector control. The final independent channel-tuple enumeration confirms the moment result.
- Initial A-decoder models confused sorted occupancy qubits with directed CX operands. Their infeasibilities are invalid controls. Directed operands were fixed. An intrusive diagnostic affected one orientation; it is excluded from physical certificates and the diagnostic is removed.
- The imported transported-T plan did not reproduce its QASM, so it was rebuilt from authoritative QASM with exact-score equality. Its R37 metadata was also stale: native A/B verification is38. This report uses verified native contacts; no R37 full-round gain is claimed.
- A tail-only delay compressed away an empty layer and was not an R39 circuit. The realR39 control moves the last resource layer as well. Save-time checks now validate the stated round against actual A and B contacts.
- Direct `flag12` fails native adjacency and is excluded. Prefix relocation ideal certificates alone do not establish noisy performance.

Verified: final physical circuits, exact coefficients, independent enumeration, applicable all orders, completed judge/speed/MC3, stated ideal checks and narrowly scoped solver receipts. Inferred: broader mechanisms beyond the measured ablations and which untested design may improve. UNKNOWN is never a closure. No global optimum or sub-percent Monte Carlo ordering is claimed.

## Retained evidence and earlier work

The final QASM/JSON/plan and all receipts share `st1_final`. Earlier fully checked finalists `st1_r38_a`, `st1_r38_b`, `st1_boundary_d` remain. Nonfinal circuit witnesses are compressed in the `inactive_circuit_witnesses*.tar.gz` and `owl_inactive_circuit_witnesses*.tar.gz` archives; SHA256 manifests verify every member before loose files were removed. Solver models and witnesses remain compressed; raw reports are `measurements_to_final.md.gz`, `measurements_to_r38_a.md.gz`, and `owl_measurements_0055.md.gz`.

Before TOTAL REDESIGN, `combined_endpoint_instrument15_alap` achieved6.26263311786e-5 exact,proxy .507576599,judge PASS/.507146/4.5s,MC3 mean6.345139e-5. The older exchange was consumed by ST2 for v27x. These historical delivered files and compressed records remain; no further v25-lineage editing was performed under the redesign mandate.

Only ST1 paths were written. Computation stayed within the stated zebra/owl allocations, owl through Docker, with thread caps and pre-launch capacity checks. All lane processes were collected. No credentials, submissions, commits, pushes, other-lane writes or collaboration tools were used.
'''
report=re.sub(r'\b(strict|Unchanged|MC|seeds|seed|above|within|and|from|to|native|the|is|at|improves|all|Explicit|retain|with|cap|mean|loss|signed)(?=\d)',r'\1 ',report)
report=report.replace('MC 3','MC3')
report=re.sub(r'\bexact(?=[3-9]\.)','exact ',report)
report=re.sub(r'(?<=\d)(s|CX)\b',r' \1',report)
report=re.sub(r'[,;](?=[A-Za-z0-9≤])',lambda m:m[0]+' ',report)
report=report.replace('/1e6','/ 1e6').replace('/39','/ 39').replace('/40','/ 40').replace('/212','/ 212').replace('CX35','CX 35')
(H/'REPORT.md').write_text(report)
print(json.dumps(dict(total=exact['total'],allorders=ao['loss'],mc3_mean=mean,acceptance=acc,seconds=seconds,sha256=result['sha256'])))
