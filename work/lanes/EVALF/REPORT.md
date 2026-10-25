# EVALF: analytic channel factors for the all-orders evaluator (PLAN P87, reviewer 11 Task 1)

Result: **swapped into `MAIN/sparse` and `ACCBUY/sparse40` on 2026-10-25 14:20 KST.** End to end 4.3–5.7× faster
(v36h 3.96 → 0.91 s at 16 processes, 38.05 → 6.85 s at 1; v29c 3.26 → 0.57 s), `adjoint_ablation.py` 4,817 → 45 s on v36g;
13 circuits agree within 9e-16 per moment. Main-session check after the swap: v36h 3.815473322483099e-5 (1.27 s),
v29c 6.34391366984215e-5 (0.77 s), v36h adjoint 56 s.

## Changes
1. Each channel is a character table on a basis of its full signature image (uniform Pauli channels: two levels);
   channels with the same image multiply; each merged entry keeps its sources' tables for per-channel attribution
   (v36g: 692 channels → 439 entries). Non-uniform channels (AENC's class-distribution channel, IDEAS/BFLAG filtered
   faults) use the same general table, so there is one code path and no raise.
2. One factor per elimination bucket, built on one representative per distinct parity pattern (≤ 2^9 rows).
3. Contraction on 2-D factors with cached column maps, 256 selector rows per chunk (cache-resident).
4. Kernel as one matrix multiply over 1,024-row blocks; Walsh transform through BLAS in ≤ 6-bit blocks.
5. `prepare`/`compile_best`: `psi` by row doubling (bit-identical), fault signatures as linear maps, bitset min-fill.
6. `adjoint_ablation.py` uses `compile_best`'s basis and recovers each channel's derivative from its merged factor.

## Profile on v36h (in-process)
| Stage | before 1 proc | after 1 proc | before 16 | after 16 |
|---|---:|---:|---:|---:|
| prepare | 1.26 s | 0.12 s | 0.60 s | 0.14 s |
| compile_best | 0.68 s | 0.09 s | 0.28 s | 0.11 s |
| rows (pool wall at 16) | 34.4 s | 5.2 s | 2.78 s | 0.58 s |
| factor construction (summed) | 14.7 s | 1.7 s | 16.4 s | 2.3 s |
| contraction (summed) | 15.9 s | 2.3 s | 17.2 s | 3.4 s |

## Validation (`validate.py`, `validation_final.json`)
v29c, v36a–v36h, INTEG2 `integ2_g1`, v36h minus each of three guards: max |Δ moment| 5.6e-16–8.9e-16, Δ loss
+3.3e-16 to +9.8e-16, identical fault signatures, elimination orders, widths and scopes; every official channel uniform
(levels agree to 1.1e-16). sparse40 on two phantom circuits Δ ≤ 9.5e-16; `region.py` Δ ≤ 7.7e-16; v36g adjoint
derivatives within 2.8e-17 of the old file, top 50 in identical order. The positive Δ loss (≈ 2.5e-11 relative) is
roundoff around the 1e-12 kernel drop threshold; the reported omission bound rises 1.2e-14 → 3.7e-14.

## Consumers changed at the swap
Channel entries are now `(scope, chi, gens, sources)` with 2-D factors; `minfill` no longer returns `bucket_sizes`.
`IDEAS/abl.py` and `BFLAG/sparse/abl.py` build filtered channels through `sw.compile_channels`; `INTEG2/ev2.py` reads
scopes as `e[0]`; `BFLAG/sparse` gained `fastfill.py`/`basis_warm.json` links. All four reproduce v36h after the swap.
`region.py`, `AENC/evalx.py`, `TERM/m08/boundary_moments.py` unchanged.

## Not done
Precomputing the moment-independent part of factor construction (≈ 7% at 1 process); dropping the dense min-fill used
only for `dense_width`; a message-passing contraction (cost model 1.7× on contraction only).

## Files
`validate.py`, `timing.py`, `abtest.py`, `prof.py`, `adjcompare.py`, `modelcheck.py`, `fwcheck.py`, bench scripts,
`timing{1,16}.json`, `validation_final.json`, `cands/` (edited circuits), `logs/`. The new evaluator files live in
`MAIN/sparse` and `ACCBUY/sparse40`. (Written by the main session from the lane's final message.)
