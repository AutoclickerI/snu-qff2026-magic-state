# ST_BC report

Best: prepBC_L5_best.json = sat6_14_400_305.json, 14 layers, 82 CX, helpers reset-style (end |0>). Merged with prepA_L5_s7307 (merge.py; merged qasm cand_best.qasm):
first order 4.6e-19, 2nd 7.50e-5, 3rd 2.86e-5, 1-F to 3rd order 1.036e-4, exp(-A1) 0.546. MC (1e8 shots, p=1e-3) seeds 0/1000/2000: 1.0524e-4, 1.0381e-4, 1.0587e-4, mean 1.0497e-4 (acc 0.5463). Previous main candidate cand14 (sat4_14_4, 73 CX): 3rd 1.120e-4, MC mean 1.1532e-4.

FT rule (ft.py, corrected per main): bad X fault iff s_B==s_C and p_B==p_C and p_B==(s_B==0), checked for an X at every cell/time. sat6.py/sat7.py encode it (CEGAR, incremental CryptoMiniSat) with a real at-most-K sequential counter on CX.

Layers touching 4/6/13/19 in best:
4 [2, 5, 6, 8, 11, 13, 14]
6 [2, 6, 7, 8, 12, 14]
13 [1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 12, 13]
19 [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
14 82 [12, 11, 6, 26, 5, 17]

Helper-X-measure variant (sat7.py + merge7.py + check7.py): no helper-zero constraint, A invertibility encoded, helpers measured in X (h;measure) with their records folded into B's X-syndrome detectors via z solving G^T z = H^T m. exact2 first order ~1e-19 for all (deterministic, FT ok). Scores (3rd order): D11/88CX 1.327e-4, D13/84CX 1.233e-4, D14/86CX 1.127e-4, D12/103CX 1.623e-4, D13/111CX 2.16e-4, D14/112CX 1.72e-4, D15/132CX 2.23e-4. Not better than reset-style at equal CX; CX count dominates, and helper measurement noise adds. Full list in results.txt.
Relay-and-reset (separate C) infeasible: cells 5,17 only touch B cells; 6,11,4 only touch C cells.
Tools: proc.sh (check, ft, merge7, exact2 --third), auto.sh/wait.sh (collect finished solver files from jerry/hippo), sat5/6/7 jobs: logs log6_*,log7_*,log8_*,log9_*.

## Measure-init (minit.py) on the best
cand_best_m.qasm/.json = cand_best with first-use resets of q29, q27 measured (minpipe.sh picks sites lowering 2nd order, then --third): first order 5.1e-19, 2nd 7.333e-5, 3rd 2.856e-5, 1-F to 3rd 1.01894e-4, exp(-A1) 0.544. MC 1e8 p=1e-3 seeds 0/1000/2000: 1.0252e-4, 1.0438e-4, 1.0430e-4, mean 1.0373e-4 (cand_best: 1.0497e-4).
Pipeline: auto.sh collects every finished solver file (jerry, hippo), runs proc.sh then minpipe.sh, appends to results.txt.
