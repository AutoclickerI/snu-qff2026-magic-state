# ST_BC report

Best: prepBC_L5_best.json (= sat4_16_2.json): 16 layers, 89 CX, verified by check.py (linear algebra, adjacency, helpers end |0>).
FT check (ft.py: every single X fault at every cell/time, bad iff syn(e_B)=syn(e_C) and e_B coset weight>=2): 0 bad faults.
Merged with prepA_L5_s7307 via DR/merge.py + EVAL/exact2.py: first order 5.0e-19, 1-F (2nd order) 9.16e-5, exp(-A1)=0.528, round starts at step 53.
Other FT-valid: sat4_16_1 (16 L, 88 CX, 9.76e-5), sat4_15_1 (15 L, 126 CX, 1.37e-4: worse, CX count dominates), sat4_18_1 (18 L, 101 CX, 1.33e-4).
Not FT (c1=7.7e-4): prepBC_noFT_L13.json (13 L, 72 CX); plain SAT found depth 14 (18 s), 13 (442 s); depth<=12 undecided (no SAT/UNSAT in ~1 h on 1 thread each), so min depth is unproven (light-cone bound 6).

Layers touching (1-indexed, best file):
4 [1, 8, 13, 14, 15, 16]
6 [3, 7, 9, 11, 15]
13 [1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 13, 14, 15, 16]
19 [1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 16]
16 89 [11, 29, 4, 13, 5, 28]

Method: sat.py = CryptoMiniSat (pycryptosat, native XOR) model of the CP-SAT problem; sat4.py = CEGAR: solve, ft.py finds bad single X faults, encode only those fault propagations (incremental), repeat. Helpers [18,24,30..35] allowed; FT needed them (D=14..16 solutions use them).
Jobs may still run on jerry/tom (log4_*, files sat4_*.json in ST_BC dirs on each host; tom's path is /data2/jihoon/home/... mirror).
