# GLOBAL phase2 — active, structural tests complete, repair/funding/retiming running

User continuation supersedes the old stop. tau=3.761821654835085e-5 (MAIN/v37a); target L<tau-1e-7, exact A>=.5002, judge gates_ok at1e6. Both BC synthesis and late X-check directions need decisive tests and a finalist plateau. A finalist alone does not stop. No questions, no subagents/commits/submissions, writes only GLOBAL, no credentials/forbidden hosts/GPU/pkill; numeric-PID stops and observed exits. Thread caps1; Jerry<=24 and zebra<=8 GLOBAL allocation. POLISH owns baseline greedy edits; only structural-branch repairs here.

ACTIVE PROCESSES (tool sessions):
- Jerry session96276: integ_run.py bc2final_seed bc2finish --jobs22, GLOBAL_EVALUATOR=sparse_repair; logs/bc2_finish.txt. It continues until no J improvement >1e-13; the old loss-threshold early break was removed. Max23 Python processes.
- Local session51777: retime_run.py bc2final_seed bc2rt --jobs2, sparse_repair; logs/bc2_retime.txt.3 Python processes.
- Local session63972: buy.py bc2final_seed bc2fund --jobs4 --floor .505, sparse_repair; logs/bc2_fund.txt.5 Python processes. Combined local8.
- Local rsync session2764 (builds/states/front fromJerry) may need reaping; no researchCPU. All earlier archive, CP, phantom, nativecat, basistraining and controls have exited.

Current seed builds/bc2final_seed copied from bc2fast_003__S_minitX_21_13: L3.7432454595414016e-5, A.5011376904666599, J=-9.309231607134122e-8. Receipt logs/bc2final_seed.json. Later candidates may be better in active job logs/receipts.
Qualified continuation finalist exists: cand/global_bc2_first.{qasm,json}, SHA f0ebbcbddf046f19d13db16f3ffbde2194a571d7b02d357d9b31d2b62361efbb, L3.745714343191323e-5 A.5022835210466124 J=-8.090437207023957e-8. Actual1e6 gates_ok=True passed=True,6.5s, logs/bc2_provisional.judge1e6.txt. phase2_finalists.json records it. Newer better seeds are not yet judge-checked. Finalist alone is not a stop.

BC structural tests COMPLETE:
- bc2/ adapts BCX hard/safe and BFLAG single-C-bit robust contracts to the R46 graph and actual source/guard slots. Plain31..45 and extendedthrough46. Fixed source slots first, then delayed preparations without crossing fixed exterior ops. Warm65 fixed contract and unchanged-resource control verified; baseline reproduces L3.7618216548350836e-5 A.5007854638217538.
- Wave1:18LNS+3fresh; wave2:16LNS+2laterfreshT033/34; all single-worker600s, exits recorded. Wave1 archive1581/front214; wave2 archive3048/front363. Every front priced. Because proxy domination did not preserve exact ordering on fresh starts, EVERY archived state was priced: bc2/bc2all.front.json has archived4629, pareto563, priced4629. Final full archive process session62772 exited0. No raw state beats the8.8041715e-8 improvement: best L3.753017483332628e-5 A.5007843807028296; equivalent best bc2w1_9f9be8f222008e7a.
- Raw repaired branch started from bc2smoke_12fe838ab4679eb4. It reverses8CX orientations at31–34/42/44, changes plus-source cells23/27/28 ->17/26/29, remains65CX. Its new source bases make measured-init repairs useful. No fresh-layout change.
- v37a BC gate-only perfect counterfactual L3.3531281286016616e-5, delta4.086935262e-6. Older4.726e-6 diagnostic was bareR46;0.9e-6 gap was not currentbudget.

Late X direction decisive scoped tests COMPLETE:
- True free lifetimes39..46: onlyq13@39 touches idledata19. Idle-looking A/B/C neighbours are live states. No freshcat covers4data in unchangedlifetimes.
- Borrow-control models0/1/2/all12eligibleguarddrops+Tretiming:UNSAT. Canonicalizing separableplus guard22->21@41 expands22to30slots, stillUNSAT.
- chain_cp.py:179 potentialnewdirectedCX slots,26symbolicvars, <=12dataCX, fixedA/BC cores/exactsourceinterfaces/endpoints. drops2/anc4 and drops29/anc100 bothINFEASIBLE. Source-interface domain is explicit; no globalimpossibility claimed.
- All21 single-role empty-destination intersections empty; all210pair swaps failadjacency.
- Built/priced7 earliest nativefreshcats +7matchedcontrols, and same14 withbothgaphelpersretired. Shortestends52(+4ticks), others53. Retiredhelpers don'tshorten. Reusing an existing finalMX ascatroot also tested (cat_native --reuse-root):7checks+7controls; S3 thenalsoends52; minimumstill+4ticks. Nativecatmodels/proofs inlx2/.
- ShortestS2 fullL9.775353309153167e-4 A.4932937427347392; matchedcontrolL3.640350824151622e-4 A.49750149469921934. Single-channel diagnostic7.666666667e-4 (R15@48 alone5e-4, spreadsXto2data). Idealaddedcat (datawaitnoise retained) S2L1.2433160174013205e-4, S12L1.713656638618752e-4, S23L1.7981157714197895e-4: waitingalone sinks schedules. lx2/cat_ideal_results.json hashashes/specs.
- All7R46phantomXchecks andmatchedguard/Ttrimcontrols built/priced onJerry; lx2_ph_s1..s7, phantom=True onlychecks. Need finalmatchedsummary fromreceipts/logs; meaningfulprizes butnogeometricroom.

Repair evidence and remaining:
- Local bc2fix and bc2fast runs progressed through measuredpreps,guards,identitypairs. Stopped byPID/exitobserved to migrate toJerry/newbasis; completedprices retained. Tightened J stoppingepsilon from5e-11 to1e-13 (above numericalerrorbound) so cheapacceptance gains aren't omitted; removed target-basedearlybreaks inINTEG andretime.
- bundle_repair.py onbc2fix003 produced14jointprices, allbelowacceptancefloor; noeligiblewinner. Preserved evidence. Sourcebyproducts are recomputed sequentially, not additive.
- Finish activeINTEG, buyer andretime. Compose measuredsuccessfuledits andpricefulljointcircuits; repairfundedbranch andretimedbranch asneeded. Need a finalfullmenu plateau, not justqualifiedscore. If differentBC timingwins, rechecklatefreeroom. No more structuralarchives pending.

Infrastructure/audit:
- price.py writes atomicpriced/<SHA>.json receipts +candidateJSON/logs, no giantledger rewriteperprice. results.json is MATERIALIZED bycollect.py, stale duringactivebatches. Forcurrentbest scanreceipts/recentlogs and RECOMPUTE J withnewtau (oldphase1receipts carryoldJ). collect.py normalizesJtau andretainsJ_v36h, verifiesQASMhashes. Includes sparse_mi/sparse_bc/sparse_repair rawoutputs. Finalsync/collectmandatory.
- Immutable equivalentbases: sparse_mi, sparse_bc (freshresourcewidth8;43s->7s Jerrycontrol), sparse_repair (repairwidth8). basis_equivalence.json records samecorehashes, invertiblerow-XOR proof and savedcontrols within1.2e-16. price cachecanreuse certified equivalentbasisresults while retainingactualevaluatedhashes. Latestproof includesmi<->repair, copiedtoJerry beforeactiveINTEG.
- SerialCLI price --jobs1 --workers1 nowcalls evaluatorin-process; controlmatches. Correction:twoauxiliaryserialbatches brieflyhad9Pythonprocessesincllauncheronzebra; reportedincommentary andREPORT. Futureserialauxuses1, caprestored. Do not addresearchprocesseswhilelocal2+4jobrunners active(total8).
- REPORT.md compact(<100lines,each<2000); report.py writesseparatepriced_circuits.md fulltable. Priorphaseinphase1/. Rootfinalist.json isoldphase1; usephase2_finalists.json untilfinalrewrite.
- Need finalsyncJerry builds/logs/priced/sparse outputs, states/runs/lx2 artifacts withoutoverwritinglocalledger blindly. Remote snapshottoresults.jerry.snapshot.json thencollect. Allcollectreceiptsatomically; preservelocalunique logs. Currentlocalbasiscontrolsamefilenameasremoteold mayhavedifferentroundoff; receiptsretainactualevaluator provenance, comparewithnumericaltolerance andrecordcontrol logs.
- Final: choosebestfeasibleJ, judgegates_ok1e6,currentcandJSON withtau/newSHA/receipts, oldqualifiedcandkept. Auditallhashes/data/L/A/J/tablecount/reportlimits andjudgehash; cleanstaleinheritedmetadata. StopownworkersbyPID,waitexit. Setphase2statuscomplete onlyafterbothdirections+repairplateau. Finalconciseverdict,bestpathL/A/J,whatmoved,verifiedvsinferred; no submission/commit.
