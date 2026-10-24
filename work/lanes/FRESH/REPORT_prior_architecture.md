## Architecture decision

The first proposed temporal-reuse design verifies B early, measures C, and reuses
the space. Existing R0 measurements already identify its fatal mechanism: X faults
on B between verification and data coupling are unchecked. A matched grid-free
gap sweep will quantify this before any routing effort.

The next design correlates B/C's three codeword amplitudes rather than preparing
two independent logical-zero states. Three Bell seeds followed by identical
encoders produce sum_x |x>_B |x>_C; transversal B→C gives |0_L>_B |0^7>_C.
All seven C bits become detectors. This reduces the joint resource rank from six
to three and may permit much shorter grid-native preparation. It overlaps the
algebraic rank-3 endpoint considered by BCPOL, whose code/evidence will be reused;
FRESH tests a correlated pre-verification boundary, relaxed correctable residues,
and its full-grid implementation. No performance is claimed yet.

Prior measured prices: separate standard blocks at R33 give 3.54847e-5; the same
family at R42 gives 4.48e-5. LADDER attributes 1.21098e-5 to the current joint BC
package at fixed R45. These are relaxed constructive prices, not grid bounds.

## Best built circuit

First physical rank-three resources have been synthesized, fully assembled and
priced. The relaxed correctable-residue designs give 8.86e-5–1.05e-4 at R45;
they are performance failures despite 170–185 CX and negligible c1. Allowing
accepted weight-one B residues is expensive because another late X fault completes
a logical error. A clean-residue synthesis is now testing this causal diagnosis.

The grid-free correlated construction is promising in isolation: R33 gives
3.31218273e-5 + 1.95118835e-6 = **3.50730156e-5**, exp(-A1)=0.667115;
R39=4.06175e-5, R42=4.41736e-5, R45=4.83524e-5. This is a constructive
grid-free price, with an additional three Bell-seed CX and seven literal C checks.
It improves slightly over the reproduced sep33 3.54847270e-5. The unchanged
exact2 reference is being run independently.

The early-verification design is rejected before routing: at R33, adding 1/2/4
unchecked B wait steps changes 3.54847e-5 to 4.56227e-5 / 5.80781e-5 /
8.99103e-5. Two steps already lose the target in the grid-free circuit.

Independent reference completed: unchanged `MAIN/gf/exact_gf.py --third` confirms
the correlated R33 result 3.50730156e-5 (model/singles 0.3 s, pairs 9.1 s,
triples 184.4 s at two workers). This is still adjacency-relaxed.

First full judge gate: `corr_d12_k65_s12_003_v23h_c2c9_w0` passes every unchanged
check at 1e6, seed0, acceptance **0.55659**, **2.1 s/1e6 on zebra**, **179 CX**.
Its 1e6 score is 7.18662e-5 (SEM 9.84e-6); this is a gate, not a ranking sample.
Its 6.88879e-5 cubic price improves to 6.76546e-5 with all seven available
deterministic-zero checks. Keeping only the three final checks gives 6.76559e-5
and higher acceptance (0.555699 proxy), so the marginal checks are not a
resolved performance win without higher-order sampling.

Depth/gate bounded clean-resource exclusions: SAT CEGAR returns UNSAT at
depth≤8/CX≤44, depth≤9/CX≤49 and depth≤10/CX≤55 on the fixed 14-cell L5 graph,
with three initial X pivots, no helpers and the literal seven-bit C check.
This includes the conservative clean predicate at every single-fault boundary.
It is not a lower bound for arbitrary layouts, useful non-clean resources or
measurement-assisted preparations. Depth11 clean witnesses exist (52–57 CX).

## Verified versus inferred

Read AGENTS, GOAL, CONSTRAINTS, judge/noise descriptions and the LADDER, BIRD,
ARCH, ST1, ST2, SEPBC, BCPOL and ST_TP reports. ENDSTATE report was absent.
All numerical results above are inherited receipts, not new FRESH verification.
The potential gain of rank reduction is an inference requiring complete pricing.

Completed price `gf_correlated_R33_gap0.qasm`: {"c1": 3.1826393372587325e-19, "second": 3.312182729280837e-05, "third": 1.951188347566532e-06, "total": 3.507301564037491e-05, "exp_minus_A1": 0.6671151441774321, "T3a": 4.149206818257183e-06, "t3bc": -2.198018470690651e-06, "pair_seconds": 0.24793913000030443, "seconds": 0.413992554997094, "pairs": 852, "triples": 24303, "table_keys": 7646, "stem": "work/lanes/FRESH/gf_correlated_R33_gap0.qasm", "grid_free": true, "wall_seconds": 0.7362207710393704}

Completed price `gf_correlated_R39_gap0.qasm`: {"c1": 3.1826393372587325e-19, "second": 3.554573620443704e-05, "third": 5.0717584405767366e-06, "total": 4.061749464501377e-05, "exp_minus_A1": 0.6397659538288758, "T3a": 7.488014189328634e-06, "t3bc": -2.4162557487518976e-06, "pair_seconds": 0.2640905290027149, "seconds": 0.42551088699838147, "pairs": 852, "triples": 24303, "table_keys": 7646, "stem": "work/lanes/FRESH/gf_correlated_R39_gap0.qasm", "grid_free": true, "wall_seconds": 0.5409522200352512}

Completed price `gf_correlated_R42_gap0.qasm`: {"c1": 3.1826393372587325e-19, "second": 3.67504334694245e-05, "third": 7.423197335946415e-06, "total": 4.417363080537091e-05, "exp_minus_A1": 0.6265932573217674, "T3a": 1.0014461498004304e-05, "t3bc": -2.591264162057889e-06, "pair_seconds": 0.23177204304374754, "seconds": 0.3898503130185418, "pairs": 852, "triples": 24303, "table_keys": 7646, "stem": "work/lanes/FRESH/gf_correlated_R42_gap0.qasm", "grid_free": true, "wall_seconds": 0.5075896820053458}

Completed price `gf_correlated_R45_gap0.qasm`: {"c1": 3.1826393372587325e-19, "second": 3.795031836754613e-05, "third": 1.0402064152220252e-05, "total": 4.8352382519766385e-05, "exp_minus_A1": 0.6137427898775404, "T3a": 1.3168159211259678e-05, "t3bc": -2.7660950590394273e-06, "pair_seconds": 0.24022867600433528, "seconds": 0.41633756703231484, "pairs": 852, "triples": 24303, "table_keys": 7646, "stem": "work/lanes/FRESH/gf_correlated_R45_gap0.qasm", "grid_free": true, "wall_seconds": 0.5361567820073105}

Completed price `gf_separate_R33_gap0.qasm`: {"c1": 3.1826393372587325e-19, "second": 3.33884939594737e-05, "third": 2.096233062395122e-06, "total": 3.548472702186882e-05, "exp_minus_A1": 0.6728310220865983, "T3a": 4.22965747864875e-06, "t3bc": -2.1334244162536277e-06, "pair_seconds": 0.21793937997426838, "seconds": 0.3749029999598861, "pairs": 837, "triples": 24184, "table_keys": 7646, "stem": "work/lanes/FRESH/gf_separate_R33_gap0.qasm", "grid_free": true, "wall_seconds": 0.5095744639984332}

Completed price `gf_separate_R33_gap1.qasm`: {"c1": 3.9227880203421503e-19, "second": 4.326627173725203e-05, "third": 2.3564289640709767e-06, "total": 4.562270070132301e-05, "exp_minus_A1": 0.6696984589824571, "T3a": 5.223368973174475e-06, "t3bc": -2.8669400091034983e-06, "pair_seconds": 0.22753149300115183, "seconds": 0.4013965560006909, "pairs": 837, "triples": 24184, "table_keys": 7646, "stem": "work/lanes/FRESH/gf_separate_R33_gap1.qasm", "grid_free": true, "wall_seconds": 0.5149941529962234}

Completed price `gf_separate_R33_gap2.qasm`: {"c1": 4.661949838514797e-19, "second": 5.5459547885400106e-05, "third": 2.618576346246281e-06, "total": 5.807812423164638e-05, "exp_minus_A1": 0.666584628073784, "T3a": 6.397347223345062e-06, "t3bc": -3.7787708770987813e-06, "pair_seconds": 0.21852634398965165, "seconds": 0.3903794719954021, "pairs": 837, "triples": 24184, "table_keys": 7646, "stem": "work/lanes/FRESH/gf_separate_R33_gap2.qasm", "grid_free": true, "wall_seconds": 0.5075290460372344}

Completed price `gf_separate_R33_gap4.qasm`: {"c1": 6.137318141652824e-19, "second": 8.675545232233558e-05, "third": 3.1548632941250662e-06, "total": 8.991031561646066e-05, "exp_minus_A1": 0.660412638836386, "T3a": 9.298640691312962e-06, "t3bc": -6.143777397187896e-06, "pair_seconds": 0.2595221140072681, "seconds": 0.4408616659929976, "pairs": 837, "triples": 24184, "table_keys": 7646, "stem": "work/lanes/FRESH/gf_separate_R33_gap4.qasm", "grid_free": true, "wall_seconds": 0.5631727559957653}

Native correlated resource `corr_d10_k50_s1_001`: {"target_ok": true, "bad": [], "residues": {"0": 6, "12": 12, "13": 8, "14": 5, "9": 5, "15": 4}, "cx": 50}; complete circuit price pending.

Native correlated resource `corr_d12_k60_s2_001`: {"target_ok": true, "bad": [], "residues": {"0": 8, "12": 6, "9": 12, "14": 4, "11": 4, "15": 4}, "cx": 60}; complete circuit price pending.

Native correlated resource `corr_d16_k85_s4_001`: {"target_ok": true, "bad": [], "residues": {"0": 6, "13": 12, "10": 12, "9": 5, "12": 7, "15": 2}, "cx": 76}; complete circuit price pending.

Native correlated resource `corr_d14_k70_s3_001`: {"target_ok": true, "bad": [], "residues": {"0": 6, "13": 9, "10": 5}, "cx": 61}; complete circuit price pending.

Native correlated resource `corr_d16_k85_s4_002`: {"target_ok": true, "bad": [], "residues": {"0": 6, "13": 12, "9": 6, "10": 10, "12": 7, "15": 2}, "cx": 77}; complete circuit price pending.

Native correlated resource `corr_d12_k60_s2_002`: {"target_ok": true, "bad": [], "residues": {"0": 6, "12": 6, "9": 12, "14": 4, "11": 4, "15": 4}, "cx": 58}; complete circuit price pending.

Native correlated resource `corr_d14_k70_s3_002`: {"target_ok": true, "bad": [], "residues": {"0": 7, "13": 13, "12": 12, "14": 6}, "cx": 64}; complete circuit price pending.

Native correlated resource `corr_d10_k50_s1_002`: {"target_ok": true, "bad": [], "residues": {"9": 9, "0": 6, "12": 15, "13": 6, "15": 3}, "cx": 49}; complete circuit price pending.

Assembly `corr_d16_k85_s4_001.prep.json` failed: ValueError('SCHEDULE_INFEASIBLE'). No physical score.

Assembly `corr_d16_k85_s4_002.prep.json` failed: ValueError('SCHEDULE_INFEASIBLE'). No physical score.

Completed price `corr_d10_k50_s1_001_v23h_c2c9_w0.qasm`: {"c1": 5.625129991434067e-19, "second": 8.051247518520324e-05, "third": 1.581047250585799e-05, "total": 9.632294769106122e-05, "exp_minus_A1": 0.5654545245749251, "T3a": 2.188039382740433e-05, "t3bc": -6.0699213215463395e-06, "pair_seconds": 0.2626180680235848, "seconds": 0.44375016598496586, "pairs": 846, "triples": 23655, "table_keys": 6712, "stem": "work/lanes/FRESH/corr_d10_k50_s1_001_v23h_c2c9_w0.qasm", "grid_free": false, "wall_seconds": 0.8606308070011437}

Completed price `corr_d10_k50_s1_002_v23h_c2c9_w0.qasm`: {"c1": 5.292063084046525e-19, "second": 7.987306777779405e-05, "third": 1.5368278926639367e-05, "total": 9.524134670443342e-05, "exp_minus_A1": 0.5705587449085874, "T3a": 2.115117365932926e-05, "t3bc": -5.782894732689895e-06, "pair_seconds": 0.2967200399725698, "seconds": 0.5181096200249158, "pairs": 865, "triples": 24029, "table_keys": 6712, "stem": "work/lanes/FRESH/corr_d10_k50_s1_002_v23h_c2c9_w0.qasm", "grid_free": false, "wall_seconds": 0.6933829879853874}

Completed price `corr_d12_k60_s2_001_v23h_c2c9_w0.qasm`: {"c1": 4.51490696680892e-19, "second": 8.32949111316091e-05, "third": 1.595342118982993e-05, "total": 9.924833232143903e-05, "exp_minus_A1": 0.5560367236181126, "T3a": 2.2579901948962087e-05, "t3bc": -6.626480759132157e-06, "pair_seconds": 0.25670341902878135, "seconds": 0.43783057999098673, "pairs": 845, "triples": 23678, "table_keys": 6712, "stem": "work/lanes/FRESH/corr_d12_k60_s2_001_v23h_c2c9_w0.qasm", "grid_free": false, "wall_seconds": 0.6295271189883351}

Completed price `corr_d12_k60_s2_002_v23h_c2c9_w0.qasm`: {"c1": 4.514906966808921e-19, "second": 8.329277779827604e-05, "third": 1.5833677267853164e-05, "total": 9.91264550661292e-05, "exp_minus_A1": 0.558115977734461, "T3a": 2.235465182151771e-05, "t3bc": -6.520974553664547e-06, "pair_seconds": 0.2590016340254806, "seconds": 0.4940812020213343, "pairs": 851, "triples": 23807, "table_keys": 6712, "stem": "work/lanes/FRESH/corr_d12_k60_s2_002_v23h_c2c9_w0.qasm", "grid_free": false, "wall_seconds": 0.6648041640291922}

Completed price `corr_d14_k70_s3_001_v23h_c2c9_w0.qasm`: {"c1": 3.737750849571301e-19, "second": 7.088120344088606e-05, "third": 1.7755230070948277e-05, "total": 8.863643351183434e-05, "exp_minus_A1": 0.5414601134189995, "T3a": 2.2978964299336097e-05, "t3bc": -5.22373422838782e-06, "pair_seconds": 0.2657657790114172, "seconds": 0.45443069405155256, "pairs": 873, "triples": 24344, "table_keys": 6712, "stem": "work/lanes/FRESH/corr_d14_k70_s3_001_v23h_c2c9_w0.qasm", "grid_free": false, "wall_seconds": 0.6537420490058139}

Completed price `corr_d14_k70_s3_002_v23h_c2c9_w0.qasm`: {"c1": 6.660598328022742e-19, "second": 8.661316474174823e-05, "third": 1.8353768758737778e-05, "total": 0.00010496693350048602, "exp_minus_A1": 0.544004156946271, "T3a": 2.4984045902366472e-05, "t3bc": -6.6302771436286954e-06, "pair_seconds": 0.26988205703673884, "seconds": 0.4621579149970785, "pairs": 873, "triples": 24308, "table_keys": 6712, "stem": "work/lanes/FRESH/corr_d14_k70_s3_002_v23h_c2c9_w0.qasm", "grid_free": false, "wall_seconds": 0.6404600219684653}

Native correlated resource `corr_d16_k85_s14_001`: {"target_ok": true, "bad": [], "residues": {"0": 7}, "cx": 81}; complete circuit price pending.

Native correlated resource `corr_d16_k85_s14_002`: {"target_ok": true, "bad": [], "residues": {"0": 7}, "cx": 83}; complete circuit price pending.

Native correlated resource `corr_d16_k85_s14_003`: {"target_ok": true, "bad": [], "residues": {"0": 7}, "cx": 82}; complete circuit price pending.

Native correlated resource `corr_d12_k65_s12_001`: {"target_ok": true, "bad": [], "residues": {"0": 6}, "cx": 59}; complete circuit price pending.

Native correlated resource `corr_d12_k65_s12_002`: {"target_ok": true, "bad": [], "residues": {"0": 6}, "cx": 58}; complete circuit price pending.

Native correlated resource `corr_d12_k65_s12_003`: {"target_ok": true, "bad": [], "residues": {"0": 6}, "cx": 58}; complete circuit price pending.

Native correlated resource `corr_d14_k75_s13_001`: {"target_ok": true, "bad": [], "residues": {"0": 6}, "cx": 70}; complete circuit price pending.

Native correlated resource `corr_d14_k75_s13_002`: {"target_ok": true, "bad": [], "residues": {"0": 6}, "cx": 70}; complete circuit price pending.

Native correlated resource `corr_d14_k75_s13_003`: {"target_ok": true, "bad": [], "residues": {"0": 6}, "cx": 70}; complete circuit price pending.

Assembly `corr_d16_k85_s14_001.prep.json` failed: ValueError('SCHEDULE_INFEASIBLE'). No physical score.

Assembly `corr_d16_k85_s14_002.prep.json` failed: ValueError('SCHEDULE_INFEASIBLE'). No physical score.

Assembly `corr_d16_k85_s14_003.prep.json` failed: ValueError('SCHEDULE_INFEASIBLE'). No physical score.

Completed price `corr_d12_k65_s12_001_v23h_c2c9_w0.qasm`: {"c1": 2.9235872981795294e-19, "second": 5.882327300393643e-05, "third": 1.5145503722707309e-05, "total": 7.396877672664374e-05, "exp_minus_A1": 0.5569248654603662, "T3a": 1.9119968431441943e-05, "t3bc": -3.974464708734634e-06, "pair_seconds": 0.2847595819621347, "seconds": 0.5675847989623435, "pairs": 908, "triples": 25305, "table_keys": 6712, "stem": "work/lanes/FRESH/corr_d12_k65_s12_001_v23h_c2c9_w0.qasm", "grid_free": false, "wall_seconds": 1.018761301995255}

Completed price `corr_d12_k65_s12_002_v23h_c2c9_w0.qasm`: {"c1": 2.9235872981795294e-19, "second": 5.882549522615855e-05, "third": 1.5142048082186065e-05, "total": 7.396754330834461e-05, "exp_minus_A1": 0.5573705836162253, "T3a": 1.9104901644561407e-05, "t3bc": -3.962853562375343e-06, "pair_seconds": 0.3064445800264366, "seconds": 0.5083256080397405, "pairs": 908, "triples": 25305, "table_keys": 6712, "stem": "work/lanes/FRESH/corr_d12_k65_s12_002_v23h_c2c9_w0.qasm", "grid_free": false, "wall_seconds": 0.755137428001035}

Completed price `corr_d12_k65_s12_003_v23h_c2c9_w0.qasm`: {"c1": 2.9235872981795294e-19, "second": 5.377052851261062e-05, "third": 1.5117338463377423e-05, "total": 6.888786697598804e-05, "exp_minus_A1": 0.5573705836162252, "T3a": 1.8735198412831764e-05, "t3bc": -3.61785994945434e-06, "pair_seconds": 0.2734294580295682, "seconds": 0.4736879779957235, "pairs": 908, "triples": 25305, "table_keys": 6712, "stem": "work/lanes/FRESH/corr_d12_k65_s12_003_v23h_c2c9_w0.qasm", "grid_free": false, "wall_seconds": 0.6596302659600042}

- `corr_d12_k65_s12_001_v23h_c2c9_w0_alap`: {"T3a": 1.8090538090333353e-05, "c1": 2.9235872981795294e-19, "exp_minus_A1": 0.5556807629732529, "pair_seconds": 0.3370034369872883, "pairs": 908, "second": 6.157814044320877e-05, "seconds": 0.551374722039327, "seconds_total": 0.7457469170331024, "sha256": "10ecc5452a9714d2235d9c324397b58e85e70ba5d3ec358fb9621f20174b5d9b", "t3bc": -3.914616438711269e-06, "table_keys": 6712, "third": 1.4175921651622084e-05, "total": 7.575406209483086e-05, "triples": 25305} Mechanism/scope: Rank-three resource; complete native per-wire retiming {"status": "OPTIMAL", "objective": -5633.0, "bound": -5633.0, "seconds": 0.005087657000000001, "mode": "alap", "R": 45}

- `corr_d12_k65_s12_002_v23h_c2c9_w0_alap`: {"T3a": 1.8074732392970062e-05, "c1": 2.9235872981795294e-19, "exp_minus_A1": 0.5561254854489033, "pair_seconds": 0.29053023899905384, "pairs": 908, "second": 6.15803626654316e-05, "seconds": 0.5078222380252555, "seconds_total": 0.7005662070005201, "sha256": "bb9ca96b3693adf4a73d03b40c530d912d802e976c968629e1ff3542304d99e5", "t3bc": -3.902446939037453e-06, "table_keys": 6712, "third": 1.4172285453932609e-05, "total": 7.575264811936421e-05, "triples": 25305} Mechanism/scope: Rank-three resource; complete native per-wire retiming {"status": "OPTIMAL", "objective": -5599.0, "bound": -5599.0, "seconds": 0.005220691, "mode": "alap", "R": 45}

Completed price `corr_d14_k75_s13_001_v23h_c2c9_w0.qasm`: {"c1": 2.9235872981795294e-19, "second": 5.6997498118534955e-05, "third": 1.6909851130530825e-05, "total": 7.390734924906579e-05, "exp_minus_A1": 0.5422387176398871, "T3a": 2.0727233938365614e-05, "t3bc": -3.817382807834789e-06, "pair_seconds": 0.3740936890244484, "seconds": 0.5969393030391075, "pairs": 897, "triples": 24794, "table_keys": 6712, "stem": "work/lanes/FRESH/corr_d14_k75_s13_001_v23h_c2c9_w0.qasm", "grid_free": false, "wall_seconds": 0.7828846659976989}

Completed price `corr_d14_k75_s13_002_v23h_c2c9_w0.qasm`: {"c1": 2.9235872981795294e-19, "second": 5.807189918483264e-05, "third": 1.7129096011948898e-05, "total": 7.520099519678154e-05, "exp_minus_A1": 0.5410860566644669, "T3a": 2.101065461174497e-05, "t3bc": -3.881558599796072e-06, "pair_seconds": 0.2791594120208174, "seconds": 0.47927154804347083, "pairs": 905, "triples": 25046, "table_keys": 6712, "stem": "work/lanes/FRESH/corr_d14_k75_s13_002_v23h_c2c9_w0.qasm", "grid_free": false, "wall_seconds": 0.6661374660325237}

- `corr_d12_k65_s12_003_v23h_c2c9_w0_alap`: {"T3a": 1.772331875906472e-05, "c1": 2.9235872981795294e-19, "exp_minus_A1": 0.5561254854489033, "pair_seconds": 0.2871756670065224, "pairs": 908, "second": 5.652539595188365e-05, "seconds": 0.5015936740092002, "seconds_total": 0.6992334220558405, "sha256": "1734db28ace6cc910c337af9f9e1f582d32584d0fdd46ef9ad85dee7e0ca5daa", "t3bc": -3.574240476379906e-06, "table_keys": 6712, "third": 1.4149078282684813e-05, "total": 7.067447423456847e-05, "triples": 25305} Mechanism/scope: Rank-three resource; complete native per-wire retiming {"status": "OPTIMAL", "objective": -5602.0, "bound": -5602.0, "seconds": 0.004955995, "mode": "alap", "R": 45}

Completed price `corr_d14_k75_s13_003_v23h_c2c9_w0.qasm`: {"c1": 2.9235872981795294e-19, "second": 5.807189918483264e-05, "third": 1.7129096011948898e-05, "total": 7.520099519678154e-05, "exp_minus_A1": 0.5410860566644669, "T3a": 2.101065461174497e-05, "t3bc": -3.881558599796072e-06, "pair_seconds": 0.3070653739850968, "seconds": 0.5037851709639654, "pairs": 905, "triples": 25046, "table_keys": 6712, "stem": "work/lanes/FRESH/corr_d14_k75_s13_003_v23h_c2c9_w0.qasm", "grid_free": false, "wall_seconds": 0.6934294780367054}

- `corr_d14_k75_s13_001_v23h_c2c9_w0_alap`: {"T3a": 2.1176926515361047e-05, "c1": 2.9235872981795294e-19, "exp_minus_A1": 0.5480095692632594, "pair_seconds": 0.290714945003856, "pairs": 897, "second": 5.886317823069371e-05, "seconds": 0.5043295550276525, "seconds_total": 0.709282769006677, "sha256": "2117886612f53ad964caf35c9a448a49db0cbd3b5ac99438b49b38ad17ae931e", "t3bc": -3.719539753142314e-06, "table_keys": 6712, "third": 1.7457386762218734e-05, "total": 7.632056499291244e-05, "triples": 24794} Mechanism/scope: Rank-three resource; complete native per-wire retiming {"status": "OPTIMAL", "objective": -5893.0, "bound": -5893.0, "seconds": 0.006209362, "mode": "alap", "R": 45}

- `corr_d14_k75_s13_002_v23h_c2c9_w0_alap`: {"T3a": 2.1453138912376945e-05, "c1": 2.9235872981795294e-19, "exp_minus_A1": 0.546844640931701, "pair_seconds": 0.28863817697856575, "pairs": 905, "second": 5.9937579296991824e-05, "seconds": 0.498147212958429, "seconds_total": 0.6939987090299837, "sha256": "a6e743e038f2e0431f281e0366327a365e424a917609c954baeb8d30ca11abbb", "t3bc": -3.779898785597231e-06, "table_keys": 6712, "third": 1.7673240126779716e-05, "total": 7.761081942377154e-05, "triples": 25046} Mechanism/scope: Rank-three resource; complete native per-wire retiming {"status": "OPTIMAL", "objective": -5887.0, "bound": -5887.0, "seconds": 0.0055690340000000005, "mode": "alap", "R": 45}

- `corr_d14_k75_s13_003_v23h_c2c9_w0_alap`: {"T3a": 2.1453138912376945e-05, "c1": 2.9235872981795294e-19, "exp_minus_A1": 0.546844640931701, "pair_seconds": 0.30603329197037965, "pairs": 905, "second": 5.9937579296991824e-05, "seconds": 0.524808062997181, "seconds_total": 0.7508574589737691, "sha256": "8b6cdb9d8ee56dfbab4e092bf44abdfcbdb20641898087e89d7b73fc679daae7", "t3bc": -3.779898785597231e-06, "table_keys": 6712, "third": 1.7673240126779716e-05, "total": 7.761081942377154e-05, "triples": 25046} Mechanism/scope: Rank-three resource; complete native per-wire retiming {"status": "OPTIMAL", "objective": -5887.0, "bound": -5887.0, "seconds": 0.005416454, "mode": "alap", "R": 45}

- `corr_d12_k65_s12_003_v23h_c2c9_w0_zall`: {"T3a": 1.858407184723823e-05, "c1": 2.9235872981795294e-19, "exp_minus_A1": 0.553479172044799, "pair_seconds": 0.3482090409961529, "pairs": 918, "second": 5.2608395179277995e-05, "seconds": 0.548190897970926, "seconds_total": 0.7515922200400382, "sha256": "be12b43cb6d78ae76cd5e6bf71cd903b3baec8031b4975a1584a4528b95503ff", "t3bc": -3.5378778921610153e-06, "table_keys": 6712, "third": 1.5046193955077213e-05, "total": 6.76545891343552e-05, "triples": 25408} Mechanism/scope: Deterministic-zero BC checks in available native slots; sites [(17, 35), (17, 36), (5, 38), (6, 39), (6, 40), (6, 41), (6, 42)]

- `corr_d12_k65_s12_003_v23h_c2c9_w0_zlast`: {"T3a": 1.8585283062021182e-05, "c1": 2.9235872981795294e-19, "exp_minus_A1": 0.5556990036794704, "pair_seconds": 0.3071863660006784, "pairs": 914, "second": 5.2608395179277534e-05, "seconds": 0.5005738660111092, "seconds_total": 0.6933077439898625, "sha256": "8587c5fb4eab0ff7d65dc8a86d4aa7faf935e36d6d91120437e7476a3a75382d", "t3bc": -3.5378077788094487e-06, "table_keys": 6712, "third": 1.5047475283211733e-05, "total": 6.765587046248927e-05, "triples": 25368} Mechanism/scope: Deterministic-zero BC checks in available native slots; sites [(17, 36), (5, 38), (6, 42)]

- `corr_d12_k65_s12_003_v23h_c2c9_w0_zq17t35`: {"T3a": 1.863075493469341e-05, "c1": 2.9235872981795294e-19, "exp_minus_A1": 0.556812996679923, "pair_seconds": 0.28851403697626665, "pairs": 910, "second": 5.279950629038865e-05, "seconds": 0.48838492698268965, "seconds_total": 0.6772002429934219, "sha256": "ccac17c6181566633f91be072e21c822a413d2c470ecf7d48f5e0dc5b2ae6ed7", "t3bc": -3.5509395214753937e-06, "table_keys": 6712, "third": 1.5079815413218015e-05, "total": 6.787932170360666e-05, "triples": 25326} Mechanism/scope: Deterministic-zero BC checks in available native slots; sites [(17, 35)]

- `corr_d12_k65_s12_003_v23h_c2c9_w0_zq17t36`: {"T3a": 1.8618580865384096e-05, "c1": 2.9235872981795294e-19, "exp_minus_A1": 0.556812996679923, "pair_seconds": 0.34728865802753717, "pairs": 910, "second": 5.2732839623721985e-05, "seconds": 0.5800165599794127, "seconds_total": 0.7690727990120649, "sha256": "726ca54b38311a2cd852ed97e891e809bccc33defd85cb6b83b4f4f3bf1dd447", "t3bc": -3.5463342446003803e-06, "table_keys": 6712, "third": 1.5072246620783715e-05, "total": 6.780508624450571e-05, "triples": 25326} Mechanism/scope: Deterministic-zero BC checks in available native slots; sites [(17, 36)]

- `corr_d12_k65_s12_003_v23h_c2c9_w0_zq5t38`: {"T3a": 1.8718972433565345e-05, "c1": 2.9235872981795294e-19, "exp_minus_A1": 0.556813491625029, "pair_seconds": 0.30745117098558694, "pairs": 910, "second": 5.364608406816671e-05, "seconds": 0.5416586070205085, "seconds_total": 0.7416613159584813, "sha256": "b301eac21fc55fa7bbc6d3ac543e676f361666f00e440f67297af73c41d8efce", "t3bc": -3.609263487929677e-06, "table_keys": 6712, "third": 1.5109708945635669e-05, "total": 6.875579301380237e-05, "triples": 25326} Mechanism/scope: Deterministic-zero BC checks in available native slots; sites [(5, 38)]

- `corr_d12_k65_s12_003_v23h_c2c9_w0_zq6t39`: {"T3a": 1.8726215177029247e-05, "c1": 2.9235872981795294e-19, "exp_minus_A1": 0.5568120087699271, "pair_seconds": 0.28591146296821535, "pairs": 910, "second": 5.377052851261074e-05, "seconds": 0.49375806999159977, "seconds_total": 0.6834250380052254, "sha256": "fa981ce0a5a430138acc6b74be2bdd9a0a00d502aa2abc87d3ba1ce2f2e7e45b", "t3bc": -3.6179315479428246e-06, "table_keys": 6712, "third": 1.5108283629086422e-05, "total": 6.887881214169715e-05, "triples": 25326} Mechanism/scope: Deterministic-zero BC checks in available native slots; sites [(6, 39)]

- `corr_d12_k65_s12_003_v23h_c2c9_w0_zq6t40`: {"T3a": 1.8723571964800877e-05, "c1": 2.9235872981795294e-19, "exp_minus_A1": 0.5568110195427157, "pair_seconds": 0.2878993639606051, "pairs": 910, "second": 5.377052851261118e-05, "seconds": 0.48988879896933213, "seconds_total": 0.7122253130073659, "sha256": "c0feb7a8d8b3cc7ef8a055d7f01724b67a2896dac1a5c9b1c92f11eaf501433c", "t3bc": -3.6179793121041557e-06, "table_keys": 6712, "third": 1.5105592652696721e-05, "total": 6.88761211653079e-05, "triples": 25326} Mechanism/scope: Deterministic-zero BC checks in available native slots; sites [(6, 40)]

- `corr_d12_k65_s12_003_v23h_c2c9_w0_zq6t41`: {"T3a": 1.8720876304553966e-05, "c1": 2.9235872981795294e-19, "exp_minus_A1": 0.5568110195427157, "pair_seconds": 0.28673221002100036, "pairs": 910, "second": 5.377052851261118e-05, "seconds": 0.5020851049921475, "seconds_total": 0.6913947879802436, "sha256": "766f45b3db31fc2956d8606d7a1545de645e085f1d0dd78257c9c42e46f55ed3", "t3bc": -3.6179793121041557e-06, "table_keys": 6712, "third": 1.510289699244981e-05, "total": 6.8873425505061e-05, "triples": 25326} Mechanism/scope: Deterministic-zero BC checks in available native slots; sites [(6, 41)]

- `corr_d12_k65_s12_003_v23h_c2c9_w0_zq6t42`: {"T3a": 1.871812819148983e-05, "c1": 2.9235872981795294e-19, "exp_minus_A1": 0.5568120087699272, "pair_seconds": 0.29541321797296405, "pairs": 910, "second": 5.377052851261074e-05, "seconds": 0.502082924998831, "seconds_total": 0.7303356599877588, "sha256": "252ac252c5de2b6d448a40bb8e0d9ef565d2496c337fa1fbd7bef3bf8902d62b", "t3bc": -3.617931547942819e-06, "table_keys": 6712, "third": 1.510019664354701e-05, "total": 6.887072515615775e-05, "triples": 25326} Mechanism/scope: Deterministic-zero BC checks in available native slots; sites [(6, 42)]

Native correlated resource `corr_d11_k57_s23_001`: {"target_ok": true, "bad": [], "residues": {"0": 6}, "cx": 54}; complete circuit price pending.

Native correlated resource `corr_d11_k57_s23_002`: {"target_ok": true, "bad": [], "residues": {"0": 6}, "cx": 54}; complete circuit price pending.

Native correlated resource `corr_d11_k57_s23_003`: {"target_ok": true, "bad": [], "residues": {"0": 6}, "cx": 53}; complete circuit price pending.

Native correlated resource `corr_d11_k57_s23_004`: {"target_ok": true, "bad": [], "residues": {"0": 6}, "cx": 53}; complete circuit price pending.

Native correlated resource `corr_d11_k57_s23_005`: {"target_ok": true, "bad": [], "residues": {"0": 6}, "cx": 52}; complete circuit price pending.

Native correlated resource `corr_d11_k57_s24_001`: {"target_ok": true, "bad": [], "residues": {"0": 7}, "cx": 57}; complete circuit price pending.

Native correlated resource `corr_d11_k57_s24_002`: {"target_ok": true, "bad": [], "residues": {"0": 7}, "cx": 56}; complete circuit price pending.

Native correlated resource `corr_d11_k57_s24_003`: {"target_ok": true, "bad": [], "residues": {"0": 7}, "cx": 56}; complete circuit price pending.

Native correlated resource `corr_d11_k57_s24_004`: {"target_ok": true, "bad": [], "residues": {"0": 7}, "cx": 57}; complete circuit price pending.

Native correlated resource `corr_d11_k57_s24_005`: {"target_ok": true, "bad": [], "residues": {"0": 7}, "cx": 57}; complete circuit price pending.

Completed price `corr_d11_k57_s23_001_freshbase_w0_mi.qasm`: {"c1": 2.6645352591003264e-19, "second": 5.062490399186198e-05, "third": 1.2780252328885113e-05, "total": 6.34051563207471e-05, "exp_minus_A1": 0.5201179869512318, "T3a": 1.6697130335308463e-05, "t3bc": -3.91687800642335e-06, "pair_seconds": 0.26233210595091805, "seconds": 0.4282152309897356, "pairs": 888, "triples": 20722, "table_keys": 4942, "stem": "work/lanes/FRESH/corr_d11_k57_s23_001_freshbase_w0_mi.qasm", "grid_free": false, "wall_seconds": 0.8627545869676396}

Completed price `corr_d11_k57_s23_002_freshbase_w0_mi.qasm`: {"c1": 2.664535259100326e-19, "second": 5.050970383383806e-05, "third": 1.2857089941225007e-05, "total": 6.336679377506307e-05, "exp_minus_A1": 0.519838356716489, "T3a": 1.6738603846607324e-05, "t3bc": -3.881513905382317e-06, "pair_seconds": 0.2747291240375489, "seconds": 0.4400315100210719, "pairs": 884, "triples": 20672, "table_keys": 4942, "stem": "work/lanes/FRESH/corr_d11_k57_s23_002_freshbase_w0_mi.qasm", "grid_free": false, "wall_seconds": 0.6702052329783328}

Completed price `corr_d11_k57_s23_003_freshbase_w0_mi.qasm`: {"c1": 2.664535259100326e-19, "second": 5.0603037167170407e-05, "third": 1.2851002508400418e-05, "total": 6.345403967557082e-05, "exp_minus_A1": 0.5199076731183754, "T3a": 1.674656169632802e-05, "t3bc": -3.895559187927599e-06, "pair_seconds": 0.2568263559951447, "seconds": 0.42524991498794407, "pairs": 884, "triples": 20672, "table_keys": 4942, "stem": "work/lanes/FRESH/corr_d11_k57_s23_003_freshbase_w0_mi.qasm", "grid_free": false, "wall_seconds": 0.6569318359834142}

- `corr_d11_k57_s23_001_freshbase_w0_mi_alap`: {"T3a": 1.8482972412513684e-05, "c1": 2.664535259100326e-19, "exp_minus_A1": 0.5289437649602738, "pair_seconds": 0.2918155649676919, "pairs": 888, "second": 5.289446028825945e-05, "seconds": 0.4709044229821302, "seconds_total": 0.7097029180149548, "sha256": "08ee95667f8e466b1f70e652292b92df1358a8892502abf6e0fffc3319962a8b", "t3bc": -4.034454903118514e-06, "table_keys": 4942, "third": 1.4448517509395171e-05, "total": 6.734297779765462e-05, "triples": 20722} Mechanism/scope: Rank-three resource; complete native per-wire retiming {"status": "OPTIMAL", "objective": -5865.0, "bound": -5865.0, "seconds": 0.004689675, "mode": "alap", "R": 48}

Completed price `corr_d11_k57_s23_004_freshbase_w0_mi.qasm`: {"c1": 2.664535259100326e-19, "second": 5.1083037167171466e-05, "third": 1.286038026786562e-05, "total": 6.394341743503709e-05, "exp_minus_A1": 0.5202543937945048, "T3a": 1.6776509432913483e-05, "t3bc": -3.9161291650478645e-06, "pair_seconds": 0.2869092100299895, "seconds": 0.4677484590210952, "pairs": 884, "triples": 20672, "table_keys": 4942, "stem": "work/lanes/FRESH/corr_d11_k57_s23_004_freshbase_w0_mi.qasm", "grid_free": false, "wall_seconds": 0.7033571799984202}

- `corr_d11_k57_s23_002_freshbase_w0_mi_alap`: {"T3a": 1.8528956658388337e-05, "c1": 2.6645352591003264e-19, "exp_minus_A1": 0.5286593897360511, "pair_seconds": 0.2648865620139986, "pairs": 884, "second": 5.2779260130235546e-05, "seconds": 0.45748626498971134, "seconds_total": 0.6974700629943982, "sha256": "c1db0def79c762c2064ba9a83721f7fee9e08e8bd48e00ed26ce4dc749f4b245", "t3bc": -3.997885410133293e-06, "table_keys": 4942, "third": 1.4531071248255045e-05, "total": 6.731033137849058e-05, "triples": 20672} Mechanism/scope: Rank-three resource; complete native per-wire retiming {"status": "OPTIMAL", "objective": -5861.0, "bound": -5861.0, "seconds": 0.004951746, "mode": "alap", "R": 48}

Completed price `corr_d11_k57_s23_005_freshbase_w0_mi.qasm`: {"c1": 2.664535259100326e-19, "second": 5.1020814944948034e-05, "third": 1.284964782384777e-05, "total": 6.38704627687958e-05, "exp_minus_A1": 0.5206707638353504, "T3a": 1.6750719796402285e-05, "t3bc": -3.901071972554515e-06, "pair_seconds": 0.2783080509980209, "seconds": 0.46898432599846274, "pairs": 884, "triples": 20672, "table_keys": 4942, "stem": "work/lanes/FRESH/corr_d11_k57_s23_005_freshbase_w0_mi.qasm", "grid_free": false, "wall_seconds": 0.7318663999903947}

- `corr_d11_k57_s23_003_freshbase_w0_mi_alap`: {"T3a": 1.8537273900591853e-05, "c1": 2.664535259100326e-19, "exp_minus_A1": 0.528729882354086, "pair_seconds": 0.25259060703683645, "pairs": 884, "second": 5.28725934635679e-05, "seconds": 0.41948665701784194, "seconds_total": 0.6640690409694798, "sha256": "f311ff5f63cb0dbac6dbe76fca718261a70e6f490f93f6ad2f1f5631ba5116d8", "t3bc": -4.012233300184794e-06, "table_keys": 4942, "third": 1.4525040600407058e-05, "total": 6.739763406397495e-05, "triples": 20672} Mechanism/scope: Rank-three resource; complete native per-wire retiming {"status": "OPTIMAL", "objective": -5822.0, "bound": -5822.0, "seconds": 0.005382410000000001, "mode": "alap", "R": 48}

Completed price `corr_d11_k57_s24_001_freshbase_w0_mi.qasm`: {"c1": 2.6645352591003264e-19, "second": 5.010549630791264e-05, "third": 1.196516829180645e-05, "total": 6.207066459971908e-05, "exp_minus_A1": 0.5294121578038079, "T3a": 1.696137851912504e-05, "t3bc": -4.996210227318589e-06, "pair_seconds": 0.2785541160264984, "seconds": 0.45350747398333624, "pairs": 884, "triples": 20621, "table_keys": 4942, "stem": "work/lanes/FRESH/corr_d11_k57_s24_001_freshbase_w0_mi.qasm", "grid_free": false, "wall_seconds": 0.6887481599696912}

- `corr_d11_k57_s23_004_freshbase_w0_mi_alap`: {"T3a": 1.856709921731844e-05, "c1": 2.664535259100326e-19, "exp_minus_A1": 0.5290824864639659, "pair_seconds": 0.24375834804959595, "pairs": 884, "second": 5.335259346356896e-05, "seconds": 0.43768694304162636, "seconds_total": 0.6515179279958829, "sha256": "4ddf20623e494b0b7d077706d08f2802de736c39c7fc1c1826560c08929bc448", "t3bc": -4.032046758539555e-06, "table_keys": 4942, "third": 1.4535052458778885e-05, "total": 6.788764592234784e-05, "triples": 20672} Mechanism/scope: Rank-three resource; complete native per-wire retiming {"status": "OPTIMAL", "objective": -5824.0, "bound": -5824.0, "seconds": 0.004285378, "mode": "alap", "R": 48}

Completed price `corr_d11_k57_s24_002_freshbase_w0_mi.qasm`: {"c1": 2.6645352591003264e-19, "second": 5.02254963079127e-05, "third": 1.196080580138363e-05, "total": 6.218630210929634e-05, "exp_minus_A1": 0.529835856987127, "T3a": 1.6959098830573054e-05, "t3bc": -4.998293029189424e-06, "pair_seconds": 0.26717930199811235, "seconds": 0.4425120839732699, "pairs": 884, "triples": 20621, "table_keys": 4942, "stem": "work/lanes/FRESH/corr_d11_k57_s24_002_freshbase_w0_mi.qasm", "grid_free": false, "wall_seconds": 0.674474672996439}

- `corr_d11_k57_s23_005_freshbase_w0_mi_alap`: {"T3a": 1.8540817812896835e-05, "c1": 2.6645352591003264e-19, "exp_minus_A1": 0.5295059218046901, "pair_seconds": 0.3458123999880627, "pairs": 884, "second": 5.329037124134553e-05, "seconds": 0.5225499660009518, "seconds_total": 0.7656887040357105, "sha256": "b821d1336afac97343eb94744b9bc1f9894a6d4b8046660b00fca10ab60af3df", "t3bc": -4.0165356547869245e-06, "table_keys": 4942, "third": 1.4524282158109911e-05, "total": 6.781465339945544e-05, "triples": 20672} Mechanism/scope: Rank-three resource; complete native per-wire retiming {"status": "OPTIMAL", "objective": -5786.0, "bound": -5786.0, "seconds": 0.004988818, "mode": "alap", "R": 48}

Completed price `corr_d11_k57_s24_003_freshbase_w0_mi.qasm`: {"c1": 2.6645352591003264e-19, "second": 4.9954385196800885e-05, "third": 1.1957652345655505e-05, "total": 6.19120375424564e-05, "exp_minus_A1": 0.5294827507976101, "T3a": 1.6945250985870496e-05, "t3bc": -4.987598640214991e-06, "pair_seconds": 0.29239747702376917, "seconds": 0.464530598022975, "pairs": 885, "triples": 20640, "table_keys": 4942, "stem": "work/lanes/FRESH/corr_d11_k57_s24_003_freshbase_w0_mi.qasm", "grid_free": false, "wall_seconds": 0.6986105090472847}

- `corr_d11_k57_s24_001_freshbase_w0_mi_alap`: {"T3a": 1.7003633209952784e-05, "c1": 2.664535259100326e-19, "exp_minus_A1": 0.5260584063429137, "pair_seconds": 0.23769857396837324, "pairs": 884, "second": 5.175043519420059e-05, "seconds": 0.3971884889760986, "seconds_total": 0.6076400620513596, "sha256": "cdebf86bf093b811f2c3e30e2c43abbc46ec42a2e3180554bfe8361cb1c7a6c2", "t3bc": -4.24920304361814e-06, "table_keys": 4942, "third": 1.2754430166334645e-05, "total": 6.450486536053524e-05, "triples": 20621} Mechanism/scope: Rank-three resource; complete native per-wire retiming {"status": "OPTIMAL", "objective": -6077.0, "bound": -6077.0, "seconds": 0.004506198, "mode": "alap", "R": 48}

Completed price `corr_d11_k57_s24_004_freshbase_w0_mi.qasm`: {"c1": 2.664535259100326e-19, "second": 4.995438519680152e-05, "third": 1.1945051703899393e-05, "total": 6.189943690070092e-05, "exp_minus_A1": 0.5283548612555427, "T3a": 1.70242375536738e-05, "t3bc": -5.079185849774405e-06, "pair_seconds": 0.28556510398630053, "seconds": 0.4533336739987135, "pairs": 885, "triples": 20640, "table_keys": 4942, "stem": "work/lanes/FRESH/corr_d11_k57_s24_004_freshbase_w0_mi.qasm", "grid_free": false, "wall_seconds": 0.6895595940295607}

- `corr_d11_k57_s24_002_freshbase_w0_mi_alap`: {"T3a": 1.6999373291771966e-05, "c1": 2.664535259100326e-19, "exp_minus_A1": 0.5264794214515773, "pair_seconds": 0.2392023730208166, "pairs": 884, "second": 5.1870435194200734e-05, "seconds": 0.39604277297621593, "seconds_total": 0.6738084399839863, "sha256": "20211c154d1bea55ce34bdf10e6368027c4e67b6852c73cbcd87c37050b5e63c", "t3bc": -4.248988532986173e-06, "table_keys": 4942, "third": 1.2750384758785792e-05, "total": 6.462081995298653e-05, "triples": 20621} Mechanism/scope: Rank-three resource; complete native per-wire retiming {"status": "OPTIMAL", "objective": -6041.0, "bound": -6041.0, "seconds": 0.004355989, "mode": "alap", "R": 48}

Completed price `corr_d11_k57_s24_005_freshbase_w0_mi.qasm`: {"c1": 2.664535259100326e-19, "second": 5.010549630791196e-05, "third": 1.1957721281885648e-05, "total": 6.20632175897976e-05, "exp_minus_A1": 0.5280050862492441, "T3a": 1.7069067106540243e-05, "t3bc": -5.111345824654595e-06, "pair_seconds": 0.285944183007814, "seconds": 0.46550812997156754, "pairs": 884, "triples": 20621, "table_keys": 4942, "stem": "work/lanes/FRESH/corr_d11_k57_s24_005_freshbase_w0_mi.qasm", "grid_free": false, "wall_seconds": 0.7070704030338675}

- `corr_d11_k57_s24_003_freshbase_w0_mi_alap`: {"T3a": 1.6990163716323015e-05, "c1": 2.6645352591003264e-19, "exp_minus_A1": 0.526128552140042, "pair_seconds": 0.25195934996008873, "pairs": 885, "second": 5.159932408308946e-05, "seconds": 0.41074800898786634, "seconds_total": 0.616671719995793, "sha256": "2a87fafec23e5c25d15f8ed06251433a3a8fe256379529c1c556a0a1c91e00e8", "t3bc": -4.243289412835487e-06, "table_keys": 4942, "third": 1.2746874303487528e-05, "total": 6.434619838657698e-05, "triples": 20640} Mechanism/scope: Rank-three resource; complete native per-wire retiming {"status": "OPTIMAL", "objective": -6038.0, "bound": -6038.0, "seconds": 0.004258507, "mode": "alap", "R": 48}

- `corr_d11_k57_s24_004_freshbase_w0_mi_alap`: {"T3a": 1.7036995275597822e-05, "c1": 2.6645352591003264e-19, "exp_minus_A1": 0.5246693935950835, "pair_seconds": 0.23977326904423535, "pairs": 885, "second": 5.1599324083090034e-05, "seconds": 0.39444530400214717, "seconds_total": 0.6281421860330738, "sha256": "fc135bfcef2144b7170a8692c62adf4305fb48cbd0df982a0b8265d8954038c9", "t3bc": -4.304621423005542e-06, "table_keys": 4942, "third": 1.273237385259228e-05, "total": 6.433169793568232e-05, "triples": 20640} Mechanism/scope: Rank-three resource; complete native per-wire retiming {"status": "OPTIMAL", "objective": -6074.0, "bound": -6074.0, "seconds": 0.004236081, "mode": "alap", "R": 48}

- `corr_d11_k57_s24_005_freshbase_w0_mi_alap`: {"T3a": 1.707983333956501e-05, "c1": 2.664535259100326e-19, "exp_minus_A1": 0.5243220583968924, "pair_seconds": 0.2635164320236072, "pairs": 884, "second": 5.175043519420232e-05, "seconds": 0.44315135304350406, "seconds_total": 0.6519773989566602, "sha256": "a6f5e6e505c41c3b4b8d2d7f0ef2217aba6c319e74335654ff77ae64bbf3158a", "t3bc": -4.334749992290693e-06, "table_keys": 4942, "third": 1.2745083347274318e-05, "total": 6.449551854147664e-05, "triples": 20621} Mechanism/scope: Rank-three resource; complete native per-wire retiming {"status": "OPTIMAL", "objective": -6074.0, "bound": -6074.0, "seconds": 0.0042288510000000005, "mode": "alap", "R": 48}

- `corr_d11_k57_s24_004_freshbase_w0_mi_zall`: {"T3a": 1.6934257496125192e-05, "c1": 2.6645352591003264e-19, "exp_minus_A1": 0.5251932898054443, "pair_seconds": 0.3149205180234276, "pairs": 894, "second": 4.950348149309686e-05, "seconds": 0.49721365101868287, "seconds_total": 0.74879514798522, "sha256": "3b9c00dd14fd78bcb14f910a1b297bdd32b336fbbdefa54632f6b1fd0200f5a6", "t3bc": -5.033082564287362e-06, "table_keys": 4942, "third": 1.1901174931837831e-05, "total": 6.14046564249347e-05, "triples": 20695} Mechanism/scope: Deterministic-zero BC checks in available native slots; sites [(6, 38), (6, 40), (11, 40), (6, 41), (5, 42), (5, 43)]

- `corr_d11_k57_s24_004_freshbase_w0_mi_zlast`: {"T3a": 1.6934361199828904e-05, "c1": 2.6645352591003264e-19, "exp_minus_A1": 0.5267712354098082, "pair_seconds": 0.26630415802355856, "pairs": 890, "second": 4.950348149309681e-05, "seconds": 0.44177223701262847, "seconds_total": 0.6851282470161095, "sha256": "6bbe9893a388c86d388541a03f196d8776dfcd1af812367289fe78ad7ed6b140", "t3bc": -5.033082564287236e-06, "table_keys": 4942, "third": 1.1901278635541669e-05, "total": 6.140476012863847e-05, "triples": 20666} Mechanism/scope: Deterministic-zero BC checks in available native slots; sites [(6, 41), (11, 40), (5, 43)]

- `corr_d11_k57_s24_004_freshbase_w0_mi_zq6t38`: {"T3a": 1.7003801397499302e-05, "c1": 2.664535259100326e-19, "exp_minus_A1": 0.5278267704836805, "pair_seconds": 0.26091907802037895, "pairs": 887, "second": 4.995438519680152e-05, "seconds": 0.43855274602537975, "seconds_total": 0.6804747399874032, "sha256": "1b9975b259cae7663317ede95b1637863229c3f1a43108108c2cd69c61026f74", "t3bc": -5.079185849774405e-06, "table_keys": 4942, "third": 1.1924615547724896e-05, "total": 6.187900074452641e-05, "triples": 20655} Mechanism/scope: Deterministic-zero BC checks in available native slots; sites [(6, 38)]

- `corr_d11_k57_s24_004_freshbase_w0_mi_zq6t40`: {"T3a": 1.6995293864759104e-05, "c1": 2.664535259100326e-19, "exp_minus_A1": 0.5278263013045377, "pair_seconds": 0.26202539302175865, "pairs": 887, "second": 4.995438519680085e-05, "seconds": 0.4703913580160588, "seconds_total": 0.7106404539663345, "sha256": "619aff30afc101a4f9a0f81eb39cf6176518bfa4ca270c0fef76561cd6e04283", "t3bc": -5.079208051723437e-06, "table_keys": 4942, "third": 1.1916085813035667e-05, "total": 6.187047100983651e-05, "triples": 20655} Mechanism/scope: Deterministic-zero BC checks in available native slots; sites [(6, 40)]

- `corr_d11_k57_s24_004_freshbase_w0_mi_zq11t40`: {"T3a": 1.7023674333920706e-05, "c1": 2.664535259100326e-19, "exp_minus_A1": 0.5278267704836807, "pair_seconds": 0.2630496600177139, "pairs": 886, "second": 4.995438519680152e-05, "seconds": 0.43506331101525575, "seconds_total": 0.6728168060071766, "sha256": "6527b4ba49d17dffec64cdaaf1113bc91b18e390259117decaf4488bdc7e222a", "t3bc": -5.0791858497743866e-06, "table_keys": 4942, "third": 1.194448848414632e-05, "total": 6.189887368094784e-05, "triples": 20636} Mechanism/scope: Deterministic-zero BC checks in available native slots; sites [(11, 40)]

- `corr_d11_k57_s24_004_freshbase_w0_mi_zq6t41`: {"T3a": 1.6988774072166517e-05, "c1": 2.664535259100326e-19, "exp_minus_A1": 0.5278263013045377, "pair_seconds": 0.2584877379704267, "pairs": 887, "second": 4.995438519680085e-05, "seconds": 0.4261496419785544, "seconds_total": 0.6642269319854677, "sha256": "1629ec069f716457b11ea6f51db1134caea4a1374c541130775d4aa7330c8c37", "t3bc": -5.079208051723437e-06, "table_keys": 4942, "third": 1.190956602044308e-05, "total": 6.186395121724393e-05, "triples": 20655} Mechanism/scope: Deterministic-zero BC checks in available native slots; sites [(6, 41)]

- `corr_d11_k57_s24_004_freshbase_w0_mi_zq5t42`: {"T3a": 1.6988231399542584e-05, "c1": 2.664535259100326e-19, "exp_minus_A1": 0.5278263013045376, "pair_seconds": 0.2627216589753516, "pairs": 887, "second": 4.9659037048653486e-05, "seconds": 0.44752397999400273, "seconds_total": 0.6859857639647089, "sha256": "437164bc58c3538610947dfb4f3cf6f8f66ed4dd5a62a34432fb1d457151df97", "t3bc": -5.049087924106886e-06, "table_keys": 4942, "third": 1.1939143475435699e-05, "total": 6.159818052408918e-05, "triples": 20645} Mechanism/scope: Deterministic-zero BC checks in available native slots; sites [(5, 42)]

- `corr_d11_k57_s24_004_freshbase_w0_mi_zq5t43`: {"T3a": 1.696994399285038e-05, "c1": 2.664535259100326e-19, "exp_minus_A1": 0.5278263013045377, "pair_seconds": 0.25745783001184464, "pairs": 887, "second": 4.950348149309793e-05, "seconds": 0.4309618379920721, "seconds_total": 0.6901699320296757, "sha256": "38b69eabd24a782d5976dd94bcc3b94c8ba187c54b84bd21e1416a8322f88423", "t3bc": -5.033060562740003e-06, "table_keys": 4942, "third": 1.1936883430110377e-05, "total": 6.14403649232083e-05, "triples": 20645} Mechanism/scope: Deterministic-zero BC checks in available native slots; sites [(5, 43)]

Native correlated resource `corr_d11_k57_s32_001`: {"target_ok": true, "bad": [], "residues": {"0": 6}, "cx": 57}; complete circuit price pending.

Native correlated resource `corr_d11_k57_s32_002`: {"target_ok": true, "bad": [], "residues": {"0": 6}, "cx": 57}; complete circuit price pending.

Native correlated resource `corr_d11_k57_s32_003`: {"target_ok": true, "bad": [], "residues": {"0": 6}, "cx": 56}; complete circuit price pending.

Native correlated resource `corr_d11_k57_s32_004`: {"target_ok": true, "bad": [], "residues": {"0": 6}, "cx": 56}; complete circuit price pending.

Completed price `corr_d11_k57_s32_001_freshbase_w0_mi.qasm`: {"c1": 2.664535259100326e-19, "second": 5.3121051863467746e-05, "third": 1.2253970364378732e-05, "total": 6.537502222784648e-05, "exp_minus_A1": 0.5254043431937678, "T3a": 1.762929611859361e-05, "t3bc": -5.37532575421488e-06, "pair_seconds": 0.24294224905315787, "seconds": 0.40052519604796544, "pairs": 879, "triples": 20523, "table_keys": 4942, "stem": "/home/jihoon/competitions/quantumn/work/lanes/FRESH/corr_d11_k57_s32_001_freshbase_w0_mi.qasm", "grid_free": false, "wall_seconds": 0.8146773140178993}

Completed price `corr_d11_k57_s32_002_freshbase_w0_mi.qasm`: {"c1": 2.6645352591003264e-19, "second": 5.26517185301344e-05, "third": 1.2224348303006097e-05, "total": 6.48760668331405e-05, "exp_minus_A1": 0.5254050437333592, "T3a": 1.755091829634726e-05, "t3bc": -5.326569993341164e-06, "pair_seconds": 0.26461664598900825, "seconds": 0.4233476499794051, "pairs": 883, "triples": 20589, "table_keys": 4942, "stem": "/home/jihoon/competitions/quantumn/work/lanes/FRESH/corr_d11_k57_s32_002_freshbase_w0_mi.qasm", "grid_free": false, "wall_seconds": 0.6311364829889499}

Completed price `corr_d11_k57_s32_003_freshbase_w0_mi.qasm`: {"c1": 2.664535259100326e-19, "second": 5.231171853013609e-05, "third": 1.2218186638062454e-05, "total": 6.452990516819855e-05, "exp_minus_A1": 0.5258255359428033, "T3a": 1.7499456052266805e-05, "t3bc": -5.281269414204351e-06, "pair_seconds": 0.23719370702747256, "seconds": 0.3948285260121338, "pairs": 883, "triples": 20589, "table_keys": 4942, "stem": "/home/jihoon/competitions/quantumn/work/lanes/FRESH/corr_d11_k57_s32_003_freshbase_w0_mi.qasm", "grid_free": false, "wall_seconds": 0.601073378988076}

Completed price `corr_d11_k57_s32_004_freshbase_w0_mi.qasm`: {"c1": 2.664535259100326e-19, "second": 5.231171853013609e-05, "third": 1.2218186638062454e-05, "total": 6.452990516819855e-05, "exp_minus_A1": 0.5258255359428033, "T3a": 1.7499456052266805e-05, "t3bc": -5.281269414204351e-06, "pair_seconds": 0.27107405598508194, "seconds": 0.4621022070059553, "pairs": 883, "triples": 20589, "table_keys": 4942, "stem": "/home/jihoon/competitions/quantumn/work/lanes/FRESH/corr_d11_k57_s32_004_freshbase_w0_mi.qasm", "grid_free": false, "wall_seconds": 0.6716290669864975}

Native correlated resource `corr_d11_k57_s35_001`: {"target_ok": true, "bad": [], "residues": {"0": 6}, "cx": 54}; complete circuit price pending.

Native correlated resource `corr_d11_k57_s33_001`: {"target_ok": true, "bad": [], "residues": {"0": 6}, "cx": 57}; complete circuit price pending.

Native correlated resource `corr_d11_k57_s31_001`: {"target_ok": true, "bad": [], "residues": {"0": 6}, "cx": 57}; complete circuit price pending.

Native correlated resource `corr_d11_k57_s31_002`: {"target_ok": true, "bad": [], "residues": {"0": 6}, "cx": 57}; complete circuit price pending.

Native correlated resource `corr_d11_k57_s31_003`: {"target_ok": true, "bad": [], "residues": {"0": 6}, "cx": 57}; complete circuit price pending.

Native correlated resource `corr_d11_k57_s31_004`: {"target_ok": true, "bad": [], "residues": {"0": 6}, "cx": 57}; complete circuit price pending.

Completed price `corr_d11_k57_s31_001_freshbase_w0_mi.qasm`: {"c1": 2.664535259100326e-19, "second": 5.0548474085689906e-05, "third": 1.2031620654006508e-05, "total": 6.258009473969642e-05, "exp_minus_A1": 0.5295528824905564, "T3a": 1.579298781408421e-05, "t3bc": -3.7613671600777004e-06, "pair_seconds": 0.2957949979463592, "seconds": 0.5176466119592078, "pairs": 904, "triples": 21072, "table_keys": 4942, "stem": "/home/jihoon/competitions/quantumn/work/lanes/FRESH/corr_d11_k57_s31_001_freshbase_w0_mi.qasm", "grid_free": false, "wall_seconds": 1.0580332999816164}

Completed price `corr_d11_k57_s31_002_freshbase_w0_mi.qasm`: {"c1": 2.664535259100326e-19, "second": 5.1004029641245447e-05, "third": 1.2039355377684936e-05, "total": 6.304338501893038e-05, "exp_minus_A1": 0.5295528824905564, "T3a": 1.5835221256509808e-05, "t3bc": -3.7958658788248716e-06, "pair_seconds": 0.3063286039978266, "seconds": 0.49433932796819136, "pairs": 901, "triples": 21018, "table_keys": 4942, "stem": "/home/jihoon/competitions/quantumn/work/lanes/FRESH/corr_d11_k57_s31_002_freshbase_w0_mi.qasm", "grid_free": false, "wall_seconds": 0.7156500669661909}

Completed price `corr_d11_k57_s31_003_freshbase_w0_mi.qasm`: {"c1": 2.664535259100326e-19, "second": 5.1004029641245447e-05, "third": 1.2039355377684926e-05, "total": 6.304338501893038e-05, "exp_minus_A1": 0.5295528824905564, "T3a": 1.5835221256509797e-05, "t3bc": -3.795865878824872e-06, "pair_seconds": 0.24865369900362566, "seconds": 0.4409722720156424, "pairs": 901, "triples": 21018, "table_keys": 4942, "stem": "/home/jihoon/competitions/quantumn/work/lanes/FRESH/corr_d11_k57_s31_003_freshbase_w0_mi.qasm", "grid_free": false, "wall_seconds": 0.6584969100076705}

Completed price `corr_d11_k57_s31_004_freshbase_w0_mi.qasm`: {"c1": 2.664535259100326e-19, "second": 5.0548474085689906e-05, "third": 1.2031620654006498e-05, "total": 6.258009473969641e-05, "exp_minus_A1": 0.5295528824905564, "T3a": 1.57929878140842e-05, "t3bc": -3.7613671600777004e-06, "pair_seconds": 0.330912868026644, "seconds": 0.5260971629759297, "pairs": 904, "triples": 21072, "table_keys": 4942, "stem": "/home/jihoon/competitions/quantumn/work/lanes/FRESH/corr_d11_k57_s31_004_freshbase_w0_mi.qasm", "grid_free": false, "wall_seconds": 0.7470565930125304}

Native correlated resource `corr_d11_k57_s34_001`: {"target_ok": true, "bad": [], "residues": {"0": 9}, "cx": 51}; complete circuit price pending.

Native correlated resource `corr_d11_k57_s34_002`: {"target_ok": true, "bad": [], "residues": {"0": 6}, "cx": 55}; complete circuit price pending.

Native correlated resource `corr_d11_k57_s34_003`: {"target_ok": true, "bad": [], "residues": {"0": 6}, "cx": 54}; complete circuit price pending.

Native correlated resource `corr_d11_k57_s34_004`: {"target_ok": true, "bad": [], "residues": {"0": 6}, "cx": 54}; complete circuit price pending.

Completed price `corr_d11_k57_s34_001_freshbase_w0_mi.qasm`: {"c1": 2.664535259100326e-19, "second": 5.6598518530132876e-05, "third": 1.2074424981705057e-05, "total": 6.867294351183794e-05, "exp_minus_A1": 0.5294140376525152, "T3a": 1.650345855047838e-05, "t3bc": -4.429033568773325e-06, "pair_seconds": 0.3022994250059128, "seconds": 0.49724127701483667, "pairs": 889, "triples": 20844, "table_keys": 4942, "stem": "/home/jihoon/competitions/quantumn/work/lanes/FRESH/corr_d11_k57_s34_001_freshbase_w0_mi.qasm", "grid_free": false, "wall_seconds": 1.0768999410211109}

Completed price `corr_d11_k57_s34_002_freshbase_w0_mi.qasm`: {"c1": 2.664535259100326e-19, "second": 5.0850488900504014e-05, "third": 1.2264913991084199e-05, "total": 6.311540289158821e-05, "exp_minus_A1": 0.5278983226827049, "T3a": 1.6143627341943717e-05, "t3bc": -3.8787133508595175e-06, "pair_seconds": 0.3176189010264352, "seconds": 0.5240497860359028, "pairs": 909, "triples": 21258, "table_keys": 4942, "stem": "/home/jihoon/competitions/quantumn/work/lanes/FRESH/corr_d11_k57_s34_002_freshbase_w0_mi.qasm", "grid_free": false, "wall_seconds": 0.7725465949624777}

Completed price `corr_d11_k57_s34_003_freshbase_w0_mi.qasm`: {"c1": 2.664535259100326e-19, "second": 4.93438222338373e-05, "third": 1.224283608752327e-05, "total": 6.158665832136056e-05, "exp_minus_A1": 0.5286731416176316, "T3a": 1.59783261014395e-05, "t3bc": -3.73549001391623e-06, "pair_seconds": 0.2756342130014673, "seconds": 0.481013716023881, "pairs": 909, "triples": 21258, "table_keys": 4942, "stem": "/home/jihoon/competitions/quantumn/work/lanes/FRESH/corr_d11_k57_s34_003_freshbase_w0_mi.qasm", "grid_free": false, "wall_seconds": 0.7255089330137707}

Completed price `corr_d11_k57_s34_004_freshbase_w0_mi.qasm`: {"c1": 2.664535259100326e-19, "second": 5.078826667828255e-05, "third": 1.2254109176190967e-05, "total": 6.304237585447352e-05, "exp_minus_A1": 0.5297287232354919, "T3a": 1.6050254497350254e-05, "t3bc": -3.7961453211592857e-06, "pair_seconds": 0.3584225899539888, "seconds": 0.5793921559816226, "pairs": 909, "triples": 21258, "table_keys": 4942, "stem": "/home/jihoon/competitions/quantumn/work/lanes/FRESH/corr_d11_k57_s34_004_freshbase_w0_mi.qasm", "grid_free": false, "wall_seconds": 0.8268808000138961}

Native correlated resource `corr_d11_k57_s35_002`: {"target_ok": true, "bad": [], "residues": {"0": 6}, "cx": 57}; complete circuit price pending.

Native correlated resource `corr_d11_k57_s35_003`: {"target_ok": true, "bad": [], "residues": {"0": 6}, "cx": 55}; complete circuit price pending.

Native correlated resource `corr_d11_k57_s35_004`: {"target_ok": true, "bad": [], "residues": {"0": 6}, "cx": 54}; complete circuit price pending.

Completed price `corr_d11_k57_s35_001_freshbase_w0_mi.qasm`: {"c1": 2.664535259100326e-19, "second": 5.2500357700081945e-05, "third": 1.2198928064484404e-05, "total": 6.469928576456636e-05, "exp_minus_A1": 0.5272021824808698, "T3a": 1.6287863598194623e-05, "t3bc": -4.088935533710218e-06, "pair_seconds": 0.24434551200829446, "seconds": 0.40622816601535305, "pairs": 900, "triples": 21115, "table_keys": 4942, "stem": "/home/jihoon/competitions/quantumn/work/lanes/FRESH/corr_d11_k57_s35_001_freshbase_w0_mi.qasm", "grid_free": false, "wall_seconds": 0.838309625047259}

Completed price `corr_d11_k57_s35_002_freshbase_w0_mi.qasm`: {"c1": 2.664535259100326e-19, "second": 4.629377905316981e-05, "third": 1.2055023927991721e-05, "total": 5.8348802981161534e-05, "exp_minus_A1": 0.5282156249901628, "T3a": 1.5560030016306118e-05, "t3bc": -3.505006088314398e-06, "pair_seconds": 0.2687484929920174, "seconds": 0.435146194009576, "pairs": 918, "triples": 21407, "table_keys": 4942, "stem": "/home/jihoon/competitions/quantumn/work/lanes/FRESH/corr_d11_k57_s35_002_freshbase_w0_mi.qasm", "grid_free": false, "wall_seconds": 0.6483225210104138}

Completed price `corr_d11_k57_s35_003_freshbase_w0_mi.qasm`: {"c1": 2.664535259100326e-19, "second": 5.0959644456060285e-05, "third": 1.2177671371394553e-05, "total": 6.313731582745483e-05, "exp_minus_A1": 0.5295533522630108, "T3a": 1.602120171611463e-05, "t3bc": -3.8435303447200785e-06, "pair_seconds": 0.24212269397685304, "seconds": 0.40670786798000336, "pairs": 905, "triples": 21154, "table_keys": 4942, "stem": "/home/jihoon/competitions/quantumn/work/lanes/FRESH/corr_d11_k57_s35_003_freshbase_w0_mi.qasm", "grid_free": false, "wall_seconds": 0.6172743900096975}

Completed price `corr_d11_k57_s35_004_freshbase_w0_mi.qasm`: {"c1": 2.6645352591003264e-19, "second": 5.089973334494946e-05, "third": 1.2161992521910898e-05, "total": 6.306172586686035e-05, "exp_minus_A1": 0.5306838002474674, "T3a": 1.5956968566572365e-05, "t3bc": -3.7949760446614675e-06, "pair_seconds": 0.2672524959780276, "seconds": 0.4272881539654918, "pairs": 905, "triples": 21154, "table_keys": 4942, "stem": "/home/jihoon/competitions/quantumn/work/lanes/FRESH/corr_d11_k57_s35_004_freshbase_w0_mi.qasm", "grid_free": false, "wall_seconds": 0.6384541449951939}

Native correlated resource `corr_d11_k57_s37_001`: {"target_ok": true, "bad": [], "residues": {"0": 6}, "cx": 57}; complete circuit price pending.

Native correlated resource `corr_d11_k57_s37_002`: {"target_ok": true, "bad": [], "residues": {"0": 6}, "cx": 56}; complete circuit price pending.

Native correlated resource `corr_d11_k57_s37_003`: {"target_ok": true, "bad": [], "residues": {"0": 6}, "cx": 56}; complete circuit price pending.

Native correlated resource `corr_d11_k57_s37_004`: {"target_ok": true, "bad": [], "residues": {"0": 6}, "cx": 55}; complete circuit price pending.

Native correlated resource `corr_d11_k57_s33_002`: {"target_ok": true, "bad": [], "residues": {"0": 6}, "cx": 54}; complete circuit price pending.

Completed price `corr_d11_k57_s37_001_freshbase_w0_mi.qasm`: {"c1": 2.664535259100326e-19, "second": 5.202604445605962e-05, "third": 1.2286824088637734e-05, "total": 6.431286854469736e-05, "exp_minus_A1": 0.5253751424334944, "T3a": 1.63709787644973e-05, "t3bc": -4.084154675859566e-06, "pair_seconds": 0.26434437197167426, "seconds": 0.43621463398449123, "pairs": 898, "triples": 20946, "table_keys": 4942, "stem": "/home/jihoon/competitions/quantumn/work/lanes/FRESH/corr_d11_k57_s37_001_freshbase_w0_mi.qasm", "grid_free": false, "wall_seconds": 0.9033462359802797}

Completed price `corr_d11_k57_s37_002_freshbase_w0_mi.qasm`: {"c1": 2.664535259100326e-19, "second": 5.346826667828224e-05, "third": 1.2282218423698537e-05, "total": 6.575048510198077e-05, "exp_minus_A1": 0.526496671111029, "T3a": 1.6435130392048722e-05, "t3bc": -4.1529119683501845e-06, "pair_seconds": 0.28486355004133657, "seconds": 0.4568477010470815, "pairs": 897, "triples": 20920, "table_keys": 4942, "stem": "/home/jihoon/competitions/quantumn/work/lanes/FRESH/corr_d11_k57_s37_002_freshbase_w0_mi.qasm", "grid_free": false, "wall_seconds": 0.6933884989703074}

Completed price `corr_d11_k57_s37_003_freshbase_w0_mi.qasm`: {"c1": 2.664535259100326e-19, "second": 5.2197155567171844e-05, "third": 1.2270671161172589e-05, "total": 6.446782672834444e-05, "exp_minus_A1": 0.5278959789749349, "T3a": 1.6253992150228844e-05, "t3bc": -3.983320989056255e-06, "pair_seconds": 0.2586862409953028, "seconds": 0.43310009100241587, "pairs": 898, "triples": 20946, "table_keys": 4942, "stem": "/home/jihoon/competitions/quantumn/work/lanes/FRESH/corr_d11_k57_s37_003_freshbase_w0_mi.qasm", "grid_free": false, "wall_seconds": 0.6705308689852245}

Completed price `corr_d11_k57_s37_004_freshbase_w0_mi.qasm`: {"c1": 2.664535259100326e-19, "second": 5.3639377789393186e-05, "third": 1.226512693820895e-05, "total": 6.590450472760215e-05, "exp_minus_A1": 0.5290228889319482, "T3a": 1.6313893708358862e-05, "t3bc": -4.048766770149913e-06, "pair_seconds": 0.2889632409787737, "seconds": 0.4664695480023511, "pairs": 897, "triples": 20920, "table_keys": 4942, "stem": "/home/jihoon/competitions/quantumn/work/lanes/FRESH/corr_d11_k57_s37_004_freshbase_w0_mi.qasm", "grid_free": false, "wall_seconds": 0.7197099339682609}

Native correlated resource `corr_d11_k57_s33_003`: {"target_ok": true, "bad": [], "residues": {"0": 6}, "cx": 54}; complete circuit price pending.

Native correlated resource `corr_d11_k57_s33_004`: {"target_ok": true, "bad": [], "residues": {"0": 6}, "cx": 53}; complete circuit price pending.

Completed price `corr_d11_k57_s33_001_freshbase_w0_mi.qasm`: {"c1": 2.664535259100326e-19, "second": 5.118154087087507e-05, "third": 1.2051356867424485e-05, "total": 6.323289773829956e-05, "exp_minus_A1": 0.5295542936920294, "T3a": 1.5860266807160747e-05, "t3bc": -3.808909939736261e-06, "pair_seconds": 0.241184187005274, "seconds": 0.3974623180110939, "pairs": 904, "triples": 21111, "table_keys": 4942, "stem": "/home/jihoon/competitions/quantumn/work/lanes/FRESH/corr_d11_k57_s33_001_freshbase_w0_mi.qasm", "grid_free": false, "wall_seconds": 0.8274683709605597}

Completed price `corr_d11_k57_s33_002_freshbase_w0_mi.qasm`: {"c1": 2.6645352591003264e-19, "second": 5.3322207833837985e-05, "third": 1.228434662977197e-05, "total": 6.560655446360995e-05, "exp_minus_A1": 0.5269503665193416, "T3a": 1.636316773895173e-05, "t3bc": -4.078821109179759e-06, "pair_seconds": 0.2512297289795242, "seconds": 0.401568878965918, "pairs": 883, "triples": 20625, "table_keys": 4942, "stem": "/home/jihoon/competitions/quantumn/work/lanes/FRESH/corr_d11_k57_s33_002_freshbase_w0_mi.qasm", "grid_free": false, "wall_seconds": 0.607774677046109}

Completed price `corr_d11_k57_s33_003_freshbase_w0_mi.qasm`: {"c1": 2.6645352591003264e-19, "second": 4.8783496465936745e-05, "third": 1.2250241205191655e-05, "total": 6.103373767112841e-05, "exp_minus_A1": 0.5261455642445629, "T3a": 1.595193054911635e-05, "t3bc": -3.701689343924694e-06, "pair_seconds": 0.23730472900206223, "seconds": 0.39320336398668587, "pairs": 894, "triples": 20928, "table_keys": 4942, "stem": "/home/jihoon/competitions/quantumn/work/lanes/FRESH/corr_d11_k57_s33_003_freshbase_w0_mi.qasm", "grid_free": false, "wall_seconds": 0.6011994450236671}

Completed price `corr_d11_k57_s33_004_freshbase_w0_mi.qasm`: {"c1": 2.6645352591003264e-19, "second": 4.887682979926994e-05, "third": 1.2286946709103019e-05, "total": 6.116377650837297e-05, "exp_minus_A1": 0.5261104890427996, "T3a": 1.599258869751967e-05, "t3bc": -3.7056419884166504e-06, "pair_seconds": 0.2558773059863597, "seconds": 0.4112772499793209, "pairs": 894, "triples": 20928, "table_keys": 4942, "stem": "/home/jihoon/competitions/quantumn/work/lanes/FRESH/corr_d11_k57_s33_004_freshbase_w0_mi.qasm", "grid_free": false, "wall_seconds": 0.6177809489890933}

Native correlated resource `corr_d12_k62_s39_001`: {"target_ok": true, "bad": [], "residues": {"0": 6}, "cx": 59}; complete circuit price pending.

Native correlated resource `corr_d12_k62_s39_002`: {"target_ok": true, "bad": [], "residues": {"0": 6}, "cx": 58}; complete circuit price pending.

Native correlated resource `corr_d12_k62_s39_003`: {"target_ok": true, "bad": [], "residues": {"0": 6}, "cx": 58}; complete circuit price pending.

Native correlated resource `corr_d12_k62_s39_004`: {"target_ok": true, "bad": [], "residues": {"0": 6}, "cx": 57}; complete circuit price pending.

Native correlated resource `corr_d11_k57_s38_001`: {"target_ok": true, "bad": [], "residues": {"0": 6}, "cx": 57}; complete circuit price pending.

Native correlated resource `corr_d11_k57_s38_002`: {"target_ok": true, "bad": [], "residues": {"0": 6}, "cx": 57}; complete circuit price pending.

Native correlated resource `corr_d11_k57_s38_003`: {"target_ok": true, "bad": [], "residues": {"0": 6}, "cx": 57}; complete circuit price pending.

Completed price `corr_d12_k62_s39_001_freshbase_w0_mi.qasm`: {"c1": 2.664535259100326e-19, "second": 5.1670148159762946e-05, "third": 1.266830220769189e-05, "total": 6.433845036745483e-05, "exp_minus_A1": 0.5215360262570561, "T3a": 1.665488600090665e-05, "t3bc": -3.986583793214762e-06, "pair_seconds": 0.24355619098059833, "seconds": 0.40819585701683536, "pairs": 897, "triples": 20894, "table_keys": 4942, "stem": "/home/jihoon/competitions/quantumn/work/lanes/FRESH/corr_d12_k62_s39_001_freshbase_w0_mi.qasm", "grid_free": false, "wall_seconds": 0.8158340909867547}

Native correlated resource `corr_d11_k57_s38_004`: {"target_ok": true, "bad": [], "residues": {"0": 6}, "cx": 57}; complete circuit price pending.

Completed price `corr_d12_k62_s39_002_freshbase_w0_mi.qasm`: {"c1": 2.664535259100326e-19, "second": 5.051903704865283e-05, "third": 1.2647825140322659e-05, "total": 6.316686218897549e-05, "exp_minus_A1": 0.522301506977542, "T3a": 1.651714977139425e-05, "t3bc": -3.869324631071589e-06, "pair_seconds": 0.26669690100243315, "seconds": 0.4331556499819271, "pairs": 898, "triples": 20906, "table_keys": 4942, "stem": "/home/jihoon/competitions/quantumn/work/lanes/FRESH/corr_d12_k62_s39_002_freshbase_w0_mi.qasm", "grid_free": false, "wall_seconds": 0.649591394001618}

Native correlated resource `corr_d11_k57_s36_001`: {"target_ok": true, "bad": [], "residues": {"0": 7}, "cx": 54}; complete circuit price pending.

Completed price `corr_d12_k62_s39_003_freshbase_w0_mi.qasm`: {"c1": 2.664535259100326e-19, "second": 5.179459260420865e-05, "third": 1.2670757927621515e-05, "total": 6.446535053183017e-05, "exp_minus_A1": 0.5229955866226014, "T3a": 1.6605090062727798e-05, "t3bc": -3.934332135106283e-06, "pair_seconds": 0.23973439499968663, "seconds": 0.4268853039829992, "pairs": 896, "triples": 20879, "table_keys": 4942, "stem": "/home/jihoon/competitions/quantumn/work/lanes/FRESH/corr_d12_k62_s39_003_freshbase_w0_mi.qasm", "grid_free": false, "wall_seconds": 0.6424448090256192}

Native correlated resource `corr_d12_k62_s40_001`: {"target_ok": true, "bad": [], "residues": {"0": 6}, "cx": 60}; complete circuit price pending.

Completed price `corr_d11_k57_s38_001_freshbase_w0_mi.qasm`: {"c1": 2.664535259100326e-19, "second": 4.828408890050488e-05, "third": 1.2117197702929371e-05, "total": 6.040128660343424e-05, "exp_minus_A1": 0.5276492159694122, "T3a": 1.6914472397748656e-05, "t3bc": -4.7972746948192855e-06, "pair_seconds": 0.35213569801999256, "seconds": 0.5391500160330907, "pairs": 902, "triples": 21025, "table_keys": 4942, "stem": "/home/jihoon/competitions/quantumn/work/lanes/FRESH/corr_d11_k57_s38_001_freshbase_w0_mi.qasm", "grid_free": false, "wall_seconds": 1.0774336410104297}

Completed price `corr_d12_k62_s39_004_freshbase_w0_mi.qasm`: {"c1": 2.664535259100326e-19, "second": 5.0643481493096875e-05, "third": 1.2650228860252583e-05, "total": 6.329371035334946e-05, "exp_minus_A1": 0.5237632096022293, "T3a": 1.6468613729276535e-05, "t3bc": -3.818384869023951e-06, "pair_seconds": 0.43165805999888107, "seconds": 0.7442699199891649, "pairs": 897, "triples": 20898, "table_keys": 4942, "stem": "/home/jihoon/competitions/quantumn/work/lanes/FRESH/corr_d12_k62_s39_004_freshbase_w0_mi.qasm", "grid_free": false, "wall_seconds": 1.1260031079873443}

Completed price `corr_d11_k57_s38_002_freshbase_w0_mi.qasm`: {"c1": 2.664535259100326e-19, "second": 5.003244445605967e-05, "third": 1.2285049736662412e-05, "total": 6.231749419272208e-05, "exp_minus_A1": 0.5281419184630474, "T3a": 1.6073338779618955e-05, "t3bc": -3.7882890429565434e-06, "pair_seconds": 0.3337736619869247, "seconds": 0.6732553190086037, "pairs": 900, "triples": 21017, "table_keys": 4942, "stem": "/home/jihoon/competitions/quantumn/work/lanes/FRESH/corr_d11_k57_s38_002_freshbase_w0_mi.qasm", "grid_free": false, "wall_seconds": 0.927781154983677}

Native correlated resource `corr_d12_k62_s40_002`: {"target_ok": true, "bad": [], "residues": {"0": 6}, "cx": 58}; complete circuit price pending.

Completed price `corr_d11_k57_s38_003_freshbase_w0_mi.qasm`: {"c1": 2.664535259100326e-19, "second": 4.9154725937541156e-05, "third": 1.2250311676581634e-05, "total": 6.14050376141228e-05, "exp_minus_A1": 0.5281419184630474, "T3a": 1.597105048600784e-05, "t3bc": -3.720738809426206e-06, "pair_seconds": 0.3118600460002199, "seconds": 0.5497903090436012, "pairs": 901, "triples": 21018, "table_keys": 4942, "stem": "/home/jihoon/competitions/quantumn/work/lanes/FRESH/corr_d11_k57_s38_003_freshbase_w0_mi.qasm", "grid_free": false, "wall_seconds": 0.9780631120083854}

Native correlated resource `corr_d12_k62_s40_003`: {"target_ok": true, "bad": [], "residues": {"0": 6}, "cx": 59}; complete circuit price pending.

Native correlated resource `corr_d12_k62_s40_004`: {"target_ok": true, "bad": [], "residues": {"0": 6}, "cx": 58}; complete circuit price pending.

Completed price `corr_d11_k57_s38_004_freshbase_w0_mi.qasm`: {"c1": 2.664535259100326e-19, "second": 4.9972503715318787e-05, "third": 1.2279984813794472e-05, "total": 6.225248852911327e-05, "exp_minus_A1": 0.5277899411895328, "T3a": 1.6080400902141503e-05, "t3bc": -3.800416088347031e-06, "pair_seconds": 0.41911050700582564, "seconds": 0.7187881419667974, "pairs": 900, "triples": 21017, "table_keys": 4942, "stem": "/home/jihoon/competitions/quantumn/work/lanes/FRESH/corr_d11_k57_s38_004_freshbase_w0_mi.qasm", "grid_free": false, "wall_seconds": 1.1050471269991249}

Completed price `corr_d12_k62_s40_001_freshbase_w0_mi.qasm`: {"c1": 2.664535259100326e-19, "second": 5.443320277704696e-05, "third": 1.2701495360172084e-05, "total": 6.713469813721904e-05, "exp_minus_A1": 0.5206318916203383, "T3a": 1.691070538444691e-05, "t3bc": -4.209210024274827e-06, "pair_seconds": 0.2465461990213953, "seconds": 0.40975878899917006, "pairs": 894, "triples": 20839, "table_keys": 4942, "stem": "/home/jihoon/competitions/quantumn/work/lanes/FRESH/corr_d12_k62_s40_001_freshbase_w0_mi.qasm", "grid_free": false, "wall_seconds": 0.8324101540492848}

Completed price `corr_d12_k62_s40_002_freshbase_w0_mi.qasm`: {"c1": 2.664535259100326e-19, "second": 5.209671216963974e-05, "third": 1.280503504673137e-05, "total": 6.49017472163711e-05, "exp_minus_A1": 0.5226486669662125, "T3a": 1.6776551660554508e-05, "t3bc": -3.971516613823137e-06, "pair_seconds": 0.26518017100170255, "seconds": 0.42371926602208987, "pairs": 891, "triples": 20818, "table_keys": 4942, "stem": "/home/jihoon/competitions/quantumn/work/lanes/FRESH/corr_d12_k62_s40_002_freshbase_w0_mi.qasm", "grid_free": false, "wall_seconds": 0.6295578029821627}

Completed price `corr_d12_k62_s40_003_freshbase_w0_mi.qasm`: {"c1": 2.664535259100326e-19, "second": 5.635200331038038e-05, "third": 1.2790424366879564e-05, "total": 6.914242767725994e-05, "exp_minus_A1": 0.5202155526648291, "T3a": 1.716017241964199e-05, "t3bc": -4.369748052762427e-06, "pair_seconds": 0.25113667198456824, "seconds": 0.4377613230026327, "pairs": 894, "triples": 20839, "table_keys": 4942, "stem": "/home/jihoon/competitions/quantumn/work/lanes/FRESH/corr_d12_k62_s40_003_freshbase_w0_mi.qasm", "grid_free": false, "wall_seconds": 0.6501177970203571}

Native correlated resource `corr_d12_k62_s41_001`: {"target_ok": true, "bad": [], "residues": {"0": 6}, "cx": 62}; complete circuit price pending.

Native correlated resource `corr_d12_k62_s41_002`: {"target_ok": true, "bad": [], "residues": {"0": 6}, "cx": 59}; complete circuit price pending.

Native correlated resource `corr_d12_k62_s41_003`: {"target_ok": true, "bad": [], "residues": {"0": 6}, "cx": 58}; complete circuit price pending.

Native correlated resource `corr_d12_k62_s41_004`: {"target_ok": true, "bad": [], "residues": {"0": 6}, "cx": 58}; complete circuit price pending.

Completed price `corr_d12_k62_s40_004_freshbase_w0_mi.qasm`: {"c1": 2.6645352591003264e-19, "second": 5.6056447754823974e-05, "third": 1.2789904408143939e-05, "total": 6.884635216296792e-05, "exp_minus_A1": 0.5202849193628615, "T3a": 1.7143799305842043e-05, "t3bc": -4.353894897698105e-06, "pair_seconds": 0.26298096298705786, "seconds": 0.4210954529698938, "pairs": 894, "triples": 20839, "table_keys": 4942, "stem": "/home/jihoon/competitions/quantumn/work/lanes/FRESH/corr_d12_k62_s40_004_freshbase_w0_mi.qasm", "grid_free": false, "wall_seconds": 0.6620100750005804}

Completed price `corr_d12_k62_s41_001_freshbase_w0_mi.qasm`: {"c1": 2.664535259100326e-19, "second": 5.017688937441959e-05, "third": 1.2924263795083559e-05, "total": 6.310115316950315e-05, "exp_minus_A1": 0.5173431351895283, "T3a": 1.6790588730926884e-05, "t3bc": -3.866324935843324e-06, "pair_seconds": 0.24234534002607688, "seconds": 0.3991154209943488, "pairs": 910, "triples": 21218, "table_keys": 4942, "stem": "/home/jihoon/competitions/quantumn/work/lanes/FRESH/corr_d12_k62_s41_001_freshbase_w0_mi.qasm", "grid_free": false, "wall_seconds": 0.8013732630060986}

Completed price `corr_d12_k62_s41_002_freshbase_w0_mi.qasm`: {"c1": 2.664535259100326e-19, "second": 5.0433200683061704e-05, "third": 1.312947716797141e-05, "total": 6.356267785103312e-05, "exp_minus_A1": 0.5170038657089483, "T3a": 1.6980078628432463e-05, "t3bc": -3.850601460461053e-06, "pair_seconds": 0.25511279300553724, "seconds": 0.414717763022054, "pairs": 906, "triples": 21169, "table_keys": 4942, "stem": "/home/jihoon/competitions/quantumn/work/lanes/FRESH/corr_d12_k62_s41_002_freshbase_w0_mi.qasm", "grid_free": false, "wall_seconds": 0.629655027994886}

Native correlated resource `corr_d12_k62_s42_001`: {"target_ok": true, "bad": [], "residues": {"0": 6}, "cx": 62}; complete circuit price pending.

Native correlated resource `corr_d12_k62_s42_002`: {"target_ok": true, "bad": [], "residues": {"0": 6}, "cx": 61}; complete circuit price pending.

Completed price `corr_d12_k62_s41_003_freshbase_w0_mi.qasm`: {"c1": 2.664535259100326e-19, "second": 4.990653401639581e-05, "third": 1.3124022635552658e-05, "total": 6.303055665194846e-05, "exp_minus_A1": 0.5170732637739783, "T3a": 1.6940318901933778e-05, "t3bc": -3.81629626638112e-06, "pair_seconds": 0.23543711297679693, "seconds": 0.39154674200108275, "pairs": 906, "triples": 21169, "table_keys": 4942, "stem": "/home/jihoon/competitions/quantumn/work/lanes/FRESH/corr_d12_k62_s41_003_freshbase_w0_mi.qasm", "grid_free": false, "wall_seconds": 0.6321495919837616}

Native correlated resource `corr_d12_k62_s42_003`: {"target_ok": true, "bad": [], "residues": {"0": 6}, "cx": 61}; complete circuit price pending.

Native correlated resource `corr_d12_k62_s42_004`: {"target_ok": true, "bad": [], "residues": {"0": 6}, "cx": 60}; complete circuit price pending.

Completed price `corr_d12_k62_s41_004_freshbase_w0_mi.qasm`: {"c1": 2.664535259100326e-19, "second": 5.015103772010019e-05, "third": 1.3113604497215184e-05, "total": 6.326464221731537e-05, "exp_minus_A1": 0.5177626943836559, "T3a": 1.6915615233481388e-05, "t3bc": -3.802010736266204e-06, "pair_seconds": 0.2579259159974754, "seconds": 0.4175850279862061, "pairs": 906, "triples": 21169, "table_keys": 4942, "stem": "/home/jihoon/competitions/quantumn/work/lanes/FRESH/corr_d12_k62_s41_004_freshbase_w0_mi.qasm", "grid_free": false, "wall_seconds": 0.6318663519923575}

Completed price `corr_d12_k62_s42_001_freshbase_w0_mi.qasm`: {"c1": 2.664535259100326e-19, "second": 5.991004266880416e-05, "third": 1.2797574363114337e-05, "total": 7.270761703191849e-05, "exp_minus_A1": 0.5201149802955605, "T3a": 1.8845619694330467e-05, "t3bc": -6.048045331216131e-06, "pair_seconds": 0.2444523989688605, "seconds": 0.4020216839853674, "pairs": 908, "triples": 21243, "table_keys": 4942, "stem": "/home/jihoon/competitions/quantumn/work/lanes/FRESH/corr_d12_k62_s42_001_freshbase_w0_mi.qasm", "grid_free": false, "wall_seconds": 0.8049942270154133}

Completed price `corr_d12_k62_s42_002_freshbase_w0_mi.qasm`: {"c1": 2.664535259100326e-19, "second": 5.4872444456059744e-05, "third": 1.2422929658479365e-05, "total": 6.72953741145391e-05, "exp_minus_A1": 0.5246326827893656, "T3a": 1.7789687487432504e-05, "t3bc": -5.366757828953139e-06, "pair_seconds": 0.3015117979957722, "seconds": 0.4603361620102078, "pairs": 914, "triples": 21302, "table_keys": 4942, "stem": "/home/jihoon/competitions/quantumn/work/lanes/FRESH/corr_d12_k62_s42_002_freshbase_w0_mi.qasm", "grid_free": false, "wall_seconds": 0.7012222530320287}

Completed price `corr_d12_k62_s42_003_freshbase_w0_mi.qasm`: {"c1": 2.6645352591003264e-19, "second": 5.320108149309823e-05, "third": 1.2468770286835605e-05, "total": 6.566985177993383e-05, "exp_minus_A1": 0.5238295608678032, "T3a": 1.769446129396672e-05, "t3bc": -5.2256910071311155e-06, "pair_seconds": 0.24304726300761104, "seconds": 0.45870347099844366, "pairs": 914, "triples": 21302, "table_keys": 4942, "stem": "/home/jihoon/competitions/quantumn/work/lanes/FRESH/corr_d12_k62_s42_003_freshbase_w0_mi.qasm", "grid_free": false, "wall_seconds": 0.6816058920230716}

Completed price `corr_d12_k62_s42_004_freshbase_w0_mi.qasm`: {"c1": 2.664535259100326e-19, "second": 5.29366370486529e-05, "third": 1.2437936189584802e-05, "total": 6.53745732382377e-05, "exp_minus_A1": 0.5245984079070818, "T3a": 1.7609082682831742e-05, "t3bc": -5.171146493246941e-06, "pair_seconds": 0.2880772980279289, "seconds": 0.4667079609935172, "pairs": 914, "triples": 21302, "table_keys": 4942, "stem": "/home/jihoon/competitions/quantumn/work/lanes/FRESH/corr_d12_k62_s42_004_freshbase_w0_mi.qasm", "grid_free": false, "wall_seconds": 0.6937424640054815}

Completed price `corr_d11_k57_s35_002_freshbase_w0_fast`: {"c1": 2.664535259100326e-19, "second": 4.629377905316981e-05, "third": 1.2055023927991721e-05, "total": 5.8348802981161534e-05, "exp_minus_A1": 0.5282156249901628, "T3a": 1.5560030016306118e-05, "t3bc": -3.505006088314398e-06, "pair_seconds": 0.2482573669985868, "seconds": 0.4107622109586373, "pairs": 918, "triples": 21407, "table_keys": 4942, "stem": "work/lanes/FRESH/corr_d11_k57_s35_002_freshbase_w0_fast", "grid_free": false, "wall_seconds": 0.831241070991382}

Native correlated resource `corr_d13_k67_s44_001`: {"target_ok": true, "bad": [], "residues": {"0": 7}, "cx": 65}; complete circuit price pending.

Native correlated resource `corr_d13_k67_s44_002`: {"target_ok": true, "bad": [], "residues": {"0": 7}, "cx": 66}; complete circuit price pending.

Native correlated resource `corr_d13_k67_s44_003`: {"target_ok": true, "bad": [], "residues": {"0": 7}, "cx": 65}; complete circuit price pending.

- `corr_d11_k57_s35_002_freshbase_w0_fast_zall`: {"T3a": 1.553675857834495e-05, "c1": 2.664535259100326e-19, "exp_minus_A1": 0.5271597808808168, "pair_seconds": 0.2846992110135034, "pairs": 921, "second": 4.620053460872483e-05, "seconds": 0.4503112320089713, "seconds_total": 0.6840245440253057, "sha256": "d2c63c78f03c9f3bdfe6ec23594a9d2f5b99ca100f791296e8b6a5d81053c77d", "t3bc": -3.4979616728689437e-06, "table_keys": 4942, "third": 1.2038796905476006e-05, "total": 5.823933151420083e-05, "triples": 21429} Mechanism/scope: Deterministic-zero BC checks in available native slots; sites [(13, 39), (13, 40)]

Native correlated resource `corr_d13_k67_s44_004`: {"target_ok": true, "bad": [], "residues": {"0": 7}, "cx": 65}; complete circuit price pending.

- `corr_d11_k57_s35_002_freshbase_w0_fast_zlast`: {"T3a": 1.5536758578344967e-05, "c1": 2.664535259100326e-19, "exp_minus_A1": 0.52768720432947, "pair_seconds": 0.24137680500280112, "pairs": 920, "second": 4.620053460872558e-05, "seconds": 0.4097860240144655, "seconds_total": 0.6302543200436048, "sha256": "1cca56a2400030e25ae4210b0669092028a3f2e04e1118c912a03c0e6f5e621c", "t3bc": -3.4979616728689877e-06, "table_keys": 4942, "third": 1.2038796905475979e-05, "total": 5.8239331514201564e-05, "triples": 21422} Mechanism/scope: Deterministic-zero BC checks in available native slots; sites [(13, 40)]

Native correlated resource `corr_d13_k67_s45_001`: {"target_ok": true, "bad": [], "residues": {"0": 7}, "cx": 63}; complete circuit price pending.

- `corr_d11_k57_s35_002_freshbase_w0_fast_zq13t39`: {"T3a": 1.5546862962186027e-05, "c1": 2.664535259100326e-19, "exp_minus_A1": 0.52768720432947, "pair_seconds": 0.2416902960394509, "pairs": 920, "second": 4.6267201275392243e-05, "seconds": 0.405964688048698, "seconds_total": 0.6243697439786047, "sha256": "b7c43207ae32ecd3eb3df97bc318c139257107b07091ad66c8ea5f6892681249", "t3bc": -3.503108043634175e-06, "table_keys": 4942, "third": 1.2043754918551853e-05, "total": 5.8310956193944095e-05, "triples": 21422} Mechanism/scope: Deterministic-zero BC checks in available native slots; sites [(13, 39)]

Completed price `corr_d13_k67_s44_001_freshbase_w0_mi.qasm`: {"c1": 2.6645352591003264e-19, "second": 5.71608445745775e-05, "third": 1.2774718180095055e-05, "total": 6.993556275467255e-05, "exp_minus_A1": 0.5187987890023594, "T3a": 1.7347439903089557e-05, "t3bc": -4.572721722994501e-06, "pair_seconds": 0.24629235896281898, "seconds": 0.3970418729586527, "pairs": 886, "triples": 20657, "table_keys": 4942, "stem": "/home/jihoon/competitions/quantumn/work/lanes/FRESH/corr_d13_k67_s44_001_freshbase_w0_mi.qasm", "grid_free": false, "wall_seconds": 0.8007822450017557}

Native correlated resource `corr_d13_k67_s45_002`: {"target_ok": true, "bad": [], "residues": {"0": 6}, "cx": 63}; complete circuit price pending.

- `corr_d11_k57_s35_002_freshbase_w0_fast_zq13t40`: {"T3a": 1.5536758578344967e-05, "c1": 2.664535259100326e-19, "exp_minus_A1": 0.52768720432947, "pair_seconds": 0.2574581450317055, "pairs": 920, "second": 4.620053460872558e-05, "seconds": 0.4469785320106894, "seconds_total": 0.7659196180175059, "sha256": "1cca56a2400030e25ae4210b0669092028a3f2e04e1118c912a03c0e6f5e621c", "t3bc": -3.4979616728689877e-06, "table_keys": 4942, "third": 1.2038796905475979e-05, "total": 5.8239331514201564e-05, "triples": 21422} Mechanism/scope: Deterministic-zero BC checks in available native slots; sites [(13, 40)]

Native correlated resource `corr_d13_k67_s45_003`: {"target_ok": true, "bad": [], "residues": {"0": 6}, "cx": 62}; complete circuit price pending.

Completed price `corr_d13_k67_s44_002_freshbase_w0_mi.qasm`: {"c1": 2.664535259100326e-19, "second": 4.7301688900504506e-05, "third": 1.2271814601162263e-05, "total": 5.957350350166677e-05, "exp_minus_A1": 0.5195249241903633, "T3a": 1.606427529616093e-05, "t3bc": -3.792460694998666e-06, "pair_seconds": 0.2675686800503172, "seconds": 0.4333428040263243, "pairs": 893, "triples": 20835, "table_keys": 4942, "stem": "/home/jihoon/competitions/quantumn/work/lanes/FRESH/corr_d13_k67_s44_002_freshbase_w0_mi.qasm", "grid_free": false, "wall_seconds": 0.6470416890224442}

Native correlated resource `corr_d13_k67_s45_004`: {"target_ok": true, "bad": [], "residues": {"0": 6}, "cx": 62}; complete circuit price pending.

Completed price `corr_d13_k67_s44_003_freshbase_w0_mi.qasm`: {"c1": 2.664535259100326e-19, "second": 4.742391112272549e-05, "third": 1.2275852930748147e-05, "total": 5.969976405347363e-05, "exp_minus_A1": 0.5206339642916415, "T3a": 1.6037205848905063e-05, "t3bc": -3.7613529181569164e-06, "pair_seconds": 0.2387207300052978, "seconds": 0.3957393770106137, "pairs": 893, "triples": 20835, "table_keys": 4942, "stem": "/home/jihoon/competitions/quantumn/work/lanes/FRESH/corr_d13_k67_s44_003_freshbase_w0_mi.qasm", "grid_free": false, "wall_seconds": 0.6479943229933269}

Completed price `corr_d13_k67_s44_004_freshbase_w0_mi.qasm`: {"c1": 2.664535259100326e-19, "second": 4.759724445605891e-05, "third": 1.2259327330311504e-05, "total": 5.985657178637041e-05, "exp_minus_A1": 0.5216707214003249, "T3a": 1.598732809853044e-05, "t3bc": -3.7280007682189347e-06, "pair_seconds": 0.2579591419780627, "seconds": 0.4100316949770786, "pairs": 892, "triples": 20820, "table_keys": 4942, "stem": "/home/jihoon/competitions/quantumn/work/lanes/FRESH/corr_d13_k67_s44_004_freshbase_w0_mi.qasm", "grid_free": false, "wall_seconds": 0.621543029032182}

Completed price `corr_d13_k67_s45_001_freshbase_w0_mi.qasm`: {"c1": 2.6645352591003264e-19, "second": 5.220817778939316e-05, "third": 1.2654832218737363e-05, "total": 6.486301000813053e-05, "exp_minus_A1": 0.5174167095380527, "T3a": 1.7719605158648342e-05, "t3bc": -5.064772939910978e-06, "pair_seconds": 0.256865170027595, "seconds": 0.4223799540195614, "pairs": 926, "triples": 21707, "table_keys": 4942, "stem": "/home/jihoon/competitions/quantumn/work/lanes/FRESH/corr_d13_k67_s45_001_freshbase_w0_mi.qasm", "grid_free": false, "wall_seconds": 0.8420216160011478}

Completed price `corr_d13_k67_s45_002_freshbase_w0_mi.qasm`: {"c1": 2.664535259100326e-19, "second": 5.284275687008508e-05, "third": 1.2893653670172613e-05, "total": 6.57364105402577e-05, "exp_minus_A1": 0.5145368660397072, "T3a": 1.8040341307233225e-05, "t3bc": -5.146687637060612e-06, "pair_seconds": 0.27024029596941546, "seconds": 0.4326169599662535, "pairs": 916, "triples": 21405, "table_keys": 4942, "stem": "/home/jihoon/competitions/quantumn/work/lanes/FRESH/corr_d13_k67_s45_002_freshbase_w0_mi.qasm", "grid_free": false, "wall_seconds": 0.65575447503943}

Native correlated resource `corr_d13_k67_s43_001`: {"target_ok": true, "bad": [], "residues": {"0": 6}, "cx": 67}; complete circuit price pending.

Completed price `corr_d13_k67_s45_003_freshbase_w0_mi.qasm`: {"c1": 2.664535259100326e-19, "second": 5.284275687008504e-05, "third": 1.2890062794123464e-05, "total": 6.573281966420851e-05, "exp_minus_A1": 0.5156352580348811, "T3a": 1.799097686089972e-05, "t3bc": -5.100914066776254e-06, "pair_seconds": 0.24364422704093158, "seconds": 0.4044332890189253, "pairs": 916, "triples": 21405, "table_keys": 4942, "stem": "/home/jihoon/competitions/quantumn/work/lanes/FRESH/corr_d13_k67_s45_003_freshbase_w0_mi.qasm", "grid_free": false, "wall_seconds": 0.6322550930199213}

Native correlated resource `corr_d13_k67_s43_002`: {"target_ok": true, "bad": [], "residues": {"0": 6}, "cx": 67}; complete circuit price pending.

Native correlated resource `corr_d13_k67_s43_003`: {"target_ok": true, "bad": [], "residues": {"0": 6}, "cx": 67}; complete circuit price pending.

Native correlated resource `corr_d13_k67_s43_004`: {"target_ok": true, "bad": [], "residues": {"0": 6}, "cx": 67}; complete circuit price pending.

Native correlated resource `corr_d11_k57_s36_002`: {"target_ok": true, "bad": [], "residues": {"0": 6}, "cx": 51}; complete circuit price pending.

Native correlated resource `corr_d11_k57_s36_003`: {"target_ok": true, "bad": [], "residues": {"0": 6}, "cx": 51}; complete circuit price pending.

Completed price `corr_d13_k67_s45_004_freshbase_w0_mi.qasm`: {"c1": 2.6645352591003264e-19, "second": 5.284720131452966e-05, "third": 1.2873817113526085e-05, "total": 6.572101842805574e-05, "exp_minus_A1": 0.5149486602282519, "T3a": 1.8010373945189377e-05, "t3bc": -5.136556831663293e-06, "pair_seconds": 0.2595536740263924, "seconds": 0.4183861170313321, "pairs": 916, "triples": 21405, "table_keys": 4942, "stem": "/home/jihoon/competitions/quantumn/work/lanes/FRESH/corr_d13_k67_s45_004_freshbase_w0_mi.qasm", "grid_free": false, "wall_seconds": 0.6442527050385252}

Native correlated resource `corr_d11_k57_s36_004`: {"target_ok": true, "bad": [], "residues": {"0": 6}, "cx": 51}; complete circuit price pending.

Completed price `corr_d13_k67_s43_001_freshbase_w0_mi.qasm`: {"c1": 2.6645352591003264e-19, "second": 5.0454503715318305e-05, "third": 1.2883471006257226e-05, "total": 6.333797472157553e-05, "exp_minus_A1": 0.5174162496122932, "T3a": 1.6828159596889654e-05, "t3bc": -3.944688590632428e-06, "pair_seconds": 0.2522985130199231, "seconds": 0.4106366049963981, "pairs": 916, "triples": 21477, "table_keys": 4942, "stem": "/home/jihoon/competitions/quantumn/work/lanes/FRESH/corr_d13_k67_s43_001_freshbase_w0_mi.qasm", "grid_free": false, "wall_seconds": 0.8842156199971214}

Completed price `corr_d11_k57_s36_001_freshbase_w0_mi.qasm`: {"c1": 2.664535259100326e-19, "second": 4.804850371531952e-05, "third": 1.1945259422086293e-05, "total": 5.9993763137405814e-05, "exp_minus_A1": 0.5302947751016376, "T3a": 1.5584554813554035e-05, "t3bc": -3.639295391467742e-06, "pair_seconds": 0.2419982409919612, "seconds": 0.3973566530039534, "pairs": 900, "triples": 21073, "table_keys": 4942, "stem": "/home/jihoon/competitions/quantumn/work/lanes/FRESH/corr_d11_k57_s36_001_freshbase_w0_mi.qasm", "grid_free": false, "wall_seconds": 0.7972896990249865}

Completed price `corr_d13_k67_s43_002_freshbase_w0_mi.qasm`: {"c1": 2.6645352591003264e-19, "second": 5.5143940752356383e-05, "third": 1.2918712563307774e-05, "total": 6.806265331566417e-05, "exp_minus_A1": 0.5182433962736037, "T3a": 1.7215078693598062e-05, "t3bc": -4.296366130290288e-06, "pair_seconds": 0.26885448896791786, "seconds": 0.48953358695143834, "pairs": 915, "triples": 21470, "table_keys": 4942, "stem": "/home/jihoon/competitions/quantumn/work/lanes/FRESH/corr_d13_k67_s43_002_freshbase_w0_mi.qasm", "grid_free": false, "wall_seconds": 0.7392744320095517}

Completed price `corr_d11_k57_s36_002_freshbase_w0_mi.qasm`: {"c1": 2.664535259100326e-19, "second": 4.896825186346906e-05, "third": 1.227904100523602e-05, "total": 6.124729286870508e-05, "exp_minus_A1": 0.5295895984884225, "T3a": 1.592367156603059e-05, "t3bc": -3.6446305607945695e-06, "pair_seconds": 0.2968112489907071, "seconds": 0.5895072420244105, "pairs": 894, "triples": 20943, "table_keys": 4942, "stem": "/home/jihoon/competitions/quantumn/work/lanes/FRESH/corr_d11_k57_s36_002_freshbase_w0_mi.qasm", "grid_free": false, "wall_seconds": 0.8339038679841906}

Completed price `corr_d13_k67_s43_003_freshbase_w0_mi.qasm`: {"c1": 2.6645352591003264e-19, "second": 5.131949630791062e-05, "third": 1.2874571883786135e-05, "total": 6.419406819169676e-05, "exp_minus_A1": 0.5185890070619151, "T3a": 1.68512329041674e-05, "t3bc": -3.976661020381266e-06, "pair_seconds": 0.3060216740122996, "seconds": 0.5357944190036505, "pairs": 915, "triples": 21470, "table_keys": 4942, "stem": "/home/jihoon/competitions/quantumn/work/lanes/FRESH/corr_d13_k67_s43_003_freshbase_w0_mi.qasm", "grid_free": false, "wall_seconds": 0.828175631002523}

Completed price `corr_d11_k57_s36_003_freshbase_w0_mi.qasm`: {"c1": 2.664535259100326e-19, "second": 4.896825186346906e-05, "third": 1.227904100523602e-05, "total": 6.124729286870508e-05, "exp_minus_A1": 0.5295895984884225, "T3a": 1.592367156603059e-05, "t3bc": -3.6446305607945695e-06, "pair_seconds": 0.2792406149674207, "seconds": 0.48732781095895916, "pairs": 894, "triples": 20943, "table_keys": 4942, "stem": "/home/jihoon/competitions/quantumn/work/lanes/FRESH/corr_d11_k57_s36_003_freshbase_w0_mi.qasm", "grid_free": false, "wall_seconds": 0.7277190220193006}

Completed price `corr_d13_k67_s43_004_freshbase_w0_mi.qasm`: {"c1": 2.6645352591003264e-19, "second": 5.307949630791061e-05, "third": 1.2885787663788146e-05, "total": 6.596528397169876e-05, "exp_minus_A1": 0.5185890070619151, "T3a": 1.7001117159874943e-05, "t3bc": -4.1153294960867985e-06, "pair_seconds": 0.3354396040085703, "seconds": 0.6362402770319022, "pairs": 915, "triples": 21470, "table_keys": 4942, "stem": "/home/jihoon/competitions/quantumn/work/lanes/FRESH/corr_d13_k67_s43_004_freshbase_w0_mi.qasm", "grid_free": false, "wall_seconds": 0.8930901460116729}

Completed price `corr_d11_k57_s36_004_freshbase_w0_mi.qasm`: {"c1": 2.6645352591003264e-19, "second": 4.940380741902461e-05, "third": 1.2280036435535142e-05, "total": 6.168384385455975e-05, "exp_minus_A1": 0.5295888923694285, "T3a": 1.5957680174217737e-05, "t3bc": -3.6776437386825953e-06, "pair_seconds": 0.31251666095340624, "seconds": 0.5027192839770578, "pairs": 894, "triples": 20943, "table_keys": 4942, "stem": "/home/jihoon/competitions/quantumn/work/lanes/FRESH/corr_d11_k57_s36_004_freshbase_w0_mi.qasm", "grid_free": false, "wall_seconds": 0.7321951229823753}

Native correlated resource `corr_d13_k67_s46_001`: {"target_ok": true, "bad": [], "residues": {"0": 6}, "cx": 64}; complete circuit price pending.

Native correlated resource `corr_d13_k67_s46_002`: {"target_ok": true, "bad": [], "residues": {"0": 8}, "cx": 67}; complete circuit price pending.

Native correlated resource `corr_d13_k67_s46_003`: {"target_ok": true, "bad": [], "residues": {"0": 8}, "cx": 66}; complete circuit price pending.

Native correlated resource `corr_d13_k67_s46_004`: {"target_ok": true, "bad": [], "residues": {"0": 8}, "cx": 66}; complete circuit price pending.

Completed price `corr_d13_k67_s46_001_freshbase_w0_mi.qasm`: {"c1": 2.6645352591003264e-19, "second": 4.97440000116162e-05, "third": 1.2769178778855898e-05, "total": 6.25131787904721e-05, "exp_minus_A1": 0.5191037124359681, "T3a": 1.7699738653012685e-05, "t3bc": -4.930559874156787e-06, "pair_seconds": 0.42047438700683415, "seconds": 0.7369392029941082, "pairs": 935, "triples": 22110, "table_keys": 4942, "stem": "/home/jihoon/competitions/quantumn/work/lanes/FRESH/corr_d13_k67_s46_001_freshbase_w0_mi.qasm", "grid_free": false, "wall_seconds": 1.381682338018436}

Completed price `corr_d13_k67_s46_002_freshbase_w0_mi.qasm`: {"c1": 2.664535259100326e-19, "second": 5.037208925606045e-05, "third": 1.2569710874148147e-05, "total": 6.29418001302086e-05, "exp_minus_A1": 0.5207346391680928, "T3a": 1.6527819293580596e-05, "t3bc": -3.958108419432449e-06, "pair_seconds": 0.44415616896003485, "seconds": 0.7502537759719416, "pairs": 910, "triples": 21325, "table_keys": 4942, "stem": "/home/jihoon/competitions/quantumn/work/lanes/FRESH/corr_d13_k67_s46_002_freshbase_w0_mi.qasm", "grid_free": false, "wall_seconds": 1.1426249869982712}

Completed price `corr_d13_k67_s46_003_freshbase_w0_mi.qasm`: {"c1": 2.6645352591003264e-19, "second": 4.947066667828149e-05, "third": 1.2535565844572459e-05, "total": 6.200623252285396e-05, "exp_minus_A1": 0.5221933474455254, "T3a": 1.636352569379182e-05, "t3bc": -3.827959849219361e-06, "pair_seconds": 0.40681984700495377, "seconds": 0.7320503870141692, "pairs": 910, "triples": 21325, "table_keys": 4942, "stem": "/home/jihoon/competitions/quantumn/work/lanes/FRESH/corr_d13_k67_s46_003_freshbase_w0_mi.qasm", "grid_free": false, "wall_seconds": 1.1341570939985104}

Completed price `corr_d13_k67_s46_004_freshbase_w0_mi.qasm`: {"c1": 2.6645352591003264e-19, "second": 5.021208925605892e-05, "third": 1.256467605460584e-05, "total": 6.277676531066476e-05, "exp_minus_A1": 0.5218462616717908, "T3a": 1.646650173396784e-05, "t3bc": -3.901825679362e-06, "pair_seconds": 0.3172620249679312, "seconds": 0.4896139479824342, "pairs": 910, "triples": 21325, "table_keys": 4942, "stem": "/home/jihoon/competitions/quantumn/work/lanes/FRESH/corr_d13_k67_s46_004_freshbase_w0_mi.qasm", "grid_free": false, "wall_seconds": 0.8892222950235009}

- `corr_d11_k57_s35_002_freshbase_w0_fast_zlast_i15_near`: {"T3a": 1.543442133014882e-05, "c1": 3.1826393372587325e-19, "exp_minus_A1": 0.5273911444761419, "pair_seconds": 0.29693409899482504, "pairs": 922, "second": 4.6200534608724556e-05, "seconds": 0.4761892799870111, "seconds_total": 0.7147094040410593, "sha256": "6842d1735810e6bb6b4aade569db49d16fe8aeeb851360b70f6fc1ccfc7f8ae3", "t3bc": -3.5195219223529794e-06, "table_keys": 4942, "third": 1.1914899407795841e-05, "total": 5.81154340165204e-05, "triples": 21447} Mechanism/scope: Rank-three BC plus imported ST1 q15 instrument; {"status": "OPTIMAL", "objective": 11.0, "bound": 11.0, "seconds": 0.006638483000000001, "mode": "near", "R": 48}

- `corr_d11_k57_s35_002_freshbase_w0_fast_zlast_i15_alap`: {"T3a": 1.6700459561648704e-05, "c1": 2.7940612786399276e-19, "exp_minus_A1": 0.5342395190082858, "pair_seconds": 0.2563525110017508, "pairs": 922, "second": 4.829338616549519e-05, "seconds": 0.4275925559923053, "seconds_total": 0.6611201599589549, "sha256": "4ee664d9d3ccb6d1ac0cbc79824afe5221006fbee84e8cdada33b2993a67b1b0", "t3bc": -3.6225854899120487e-06, "table_keys": 4942, "third": 1.3077874071736655e-05, "total": 6.137126023723185e-05, "triples": 21447} Mechanism/scope: Rank-three BC plus imported ST1 q15 instrument; {"status": "OPTIMAL", "objective": -6136.0, "bound": -6136.0, "seconds": 0.005186789000000001, "mode": "alap", "R": 48}

## Candidate receipts

The current best is `corr_d11_k57_s35_002_freshbase_w0_fast_zlast` (QASM and JSON
in this directory). It uses the older cultivation prefix, a 57-CX clean rank-three
BC resource on the L5 grid cells, the q19 measured initialization repair and the
q13 zero-check repair. It has 189 CX, round start R48, native depth 51, 57
detectors and data cells from its metadata. The unmodified exact2 cubic result is
**4.62005346e-5 + 1.20387969e-5 = 5.82393315e-5**, c1=2.66e-19 and
exp(-A1)=0.52769. A moments-only screen on an imported instrument rewrite gave
5.8115e-5, but exact2 superseded it and that rewrite is discarded from ranking.

The unchanged judge gate passes: 1e6 seed0 **5.77834e-5**, acceptance **0.527833**,
189 CX, **2.8 s/1e6** single process on zebra. Independent 1e8 results so far:
seed0 **5.90419220e-5** (acceptance 0.52751), seed1000 **5.88640000e-5**
(acceptance 0.52749), seed2000 **5.89256e-5** (acceptance 0.5275, 4-process
fast_check 66.3 s). Mean = **5.89438407e-5**.

The final unmodified exact2 `--third` receipt is `winner_exact.log`; no all-orders Walsh result is claimed because the validated five-projector evaluator scope was not established for this candidate.

## Designs tried and mechanisms

- Temporal early B verification: measured grid-free gap sweep R33, 1/2/4 extra wait steps: 4.56227e-5 / 5.80781e-5 / 8.99103e-5. Mechanism is unchecked B X exposure after C verification; rejected before grid routing.
- Correlated rank-three BC, relaxed residues: grid-free R33 3.50730e-5, but first physical builds 8.86e-5–1.05e-4. Accepted B residue plus a later fault is the dominant failure; not a viable endpoint.
- Correlated rank-three BC with literal C checks: fixed-L5 CEGAR clean synthesis UNSAT at depth/CX (8,44), (9,49), (10,55); depth11 witnesses exist. This reduces accepted single-fault residue but increases preparation cost.
- Deterministic-zero checks: inserting all seven available checks on the current native schedule gives 6.76546e-5 cubic; the best useful final subset gives 6.76559e-5. The checks are legal but do not bridge the gap.
- Imported three-wire q15 instrument: its moments-only screen looked lower, but the unmodified exact2 receipt did not confirm that gain; it is rejected from ranking.
- SAT portfolio: independent clean rank-three seeds at d11/CX57, d12/CX62 and d13/CX67 were emitted and full-priced. Best exact screen is the retained d11 seed35 build; all stayed above 5e-5.

## Verification status

Checked: every retained QASM's no-noise detector/class path through `exact2`/Stim construction,
nearest-neighbour CX emission, c1 < 1e-12 for all cubic prices, unchanged judge format/class/
correctness/acceptance at 1e6 for the retained circuit, seed-0 speed, direct seed-2000 1e8
receipt, the unmodified exact2 third-order result, and the three-wire instrument algebraic contract. Inferred: no global optimum,
all-orders score, or server runtime is claimed. The candidate is below 6e-5 but did not meet the
requested 5e-5 target.

## Final exact receipt

Unmodified `work/lanes/EVAL/exact2.py --third --procs 8` completed for the retained
stem: second **4.62005346e-5**, third **1.20387969e-5**, total **5.82393315e-5**,
c1 **2.6645e-19**, exp(-A1) **0.52769**; model 0.5 s, pairs 7.4 s, triples
180.9 s. The leading pair mechanism is q7 idle (t20–23) × q20 idle (t40–46)
at 7.731e-7, followed by q10 idle (t34–47) with final round gates at 3.084e-7.
This exact receipt supersedes the earlier moments-only 5.8115e-5 screen.

Native correlated resource `corr_d11_k57_s101_001`: {"target_ok": true, "bad": [], "residues": {"0": 6}, "cx": 48}; complete circuit price pending.

Native correlated resource `corr_d11_k57_s101_002`: {"target_ok": true, "bad": [], "residues": {"0": 6}, "cx": 49}; complete circuit price pending.

Native correlated resource `corr_d11_k57_s101_003`: {"target_ok": true, "bad": [], "residues": {"0": 6}, "cx": 48}; complete circuit price pending.

Completed price `corr_d11_k57_s35_002_v23h_c2c9_w0_fast`: {"c1": 2.9235872981795294e-19, "second": 4.836933570823589e-05, "third": 1.4528891066352398e-05, "total": 6.289822677458829e-05, "exp_minus_A1": 0.559113049586619, "T3a": 1.8078609336213074e-05, "t3bc": -3.549718269860676e-06, "pair_seconds": 0.37656356097431853, "seconds": 0.6245903340168297, "pairs": 913, "triples": 25181, "table_keys": 6712, "stem": "work/lanes/FRESH/corr_d11_k57_s35_002_v23h_c2c9_w0_fast", "grid_free": false, "wall_seconds": 1.5794728740002029}

Native correlated resource `corr_d10_k50_s102_001`: {"target_ok": true, "bad": [], "residues": {"0": 9, "9": 10, "14": 8, "10": 2}, "cx": 41}; complete circuit price pending.

Native correlated resource `corr_d10_k50_s102_002`: {"target_ok": true, "bad": [], "residues": {"0": 9, "14": 8, "9": 8, "10": 2}, "cx": 40}; complete circuit price pending.

Assembly `corr_d10_k50_s102_002.prep.json` failed: AssertionError({'stim_target_pass': False, 'policy_pass': True, 'policy_faults': 0, 'clean_pass': False, 'residual_classes': {10: 1, 15: 1}, 'cx': 47, 'depth': 11}). No physical score.

Native correlated resource `corr_d8_k44_s201_001`: {"target_ok": true, "bad": [], "residues": {"0": 6}, "cx": 32}; complete circuit price pending.

Native correlated resource `corr_d8_k44_s201_002`: {"target_ok": true, "bad": [], "residues": {"0": 6}, "cx": 34}; complete circuit price pending.

Assembly `corr_d8_k44_s201_002.prep.json` failed: AssertionError({'stim_target_pass': False, 'policy_pass': True, 'policy_faults': 0, 'clean_pass': False, 'residual_classes': {10: 1, 15: 1}, 'cx': 41, 'depth': 9}). No physical score.

## Continuation: early-round integration attempt

After MAIN accepted the original FRESH circuit as v30f, I tested earlier correlated-BC
round boundaries using the ENDSTATE geometry and compact prefix schedules.

- Rebuilt the clean rank-three resource on ENDSTATE's B/C final geometry. The local
  SAT screen found depth-8/CX-44 witnesses, but the full BCPOL endpoint contract
  rejected them: the individual codeword target/detector contract was not
  deterministic (`stim_target_pass=False`, eight policy faults for the first
  witness). These are algebraic combined-signature witnesses only, not usable
  preparation circuits.
- The valid FRESH resource on the original grid cells remains depth 11/CX57.
  Replacing the v23h suffix with this resource gives R45 and exact cubic
  **6.28982268e-5**. The older v23 prefix is therefore worse than the accepted
  v30f/v25 lineage for this resource.
- I attached the same correlated suffix to
  `TREP2/joint21_compact_reuse10_alap_two_moves` using a native per-wire CP-SAT
  retimer. It reaches **R44**, not R40, and scores
  **5.04546130e-5 + 1.73202588e-5 = 6.77748718e-5**. The compact prefix changes
  the cross-region fault distribution enough to lose despite the one-step gain.
- `SEPBC/endstate_w12_v23_c0` was independently checked as a complete routed
  witness: R75, cubic **9.87309e-4**, exp(-A1)=0.2879. Its no-pre-round-idle
  counterfactual is 6.29043e-5, confirming that live-state exposure and block
  moves, rather than the final round alone, cause the failure.

Mechanism: the correlated resource is not the only timing constraint. The v23h
terminal T†/release chain and the data-hop/readout order leave no legal schedule
below R45 without changing the cultivation prefix itself. The compact prefix
removes one step but introduces larger correlated idle/prefix exposure. A true
R<=40 result requires a new jointly synthesized prefix/data placement and a full
endpoint-valid BC instrument; no such circuit was verified in this continuation.

## Global prefix/data placement continuation

I ran a separate whole-circuit CP-SAT redesign using ST1's logical-prefix emitter
(`cultivation19`/cats13), with prefix cell placement, per-operation native times,
per-wire lifetimes, data routes, block routes, encoder-stage locations, and round
start in one model. This is a global placement model; it does not reuse ST1's local
prefix macros.

- Model G0: free prefix placement, cats13 cultivation, s34c15/s13c8/s13c8
  block encoders, two moves per block wire, three data moves, `30<=R<=40`.
  Result: **UNKNOWN after 300.1 s**, 216,790 conflicts, no witness. This is not
  an infeasibility certificate.
- Model G1: relaxed to l3_10 encoders, three moves per block wire, five data
  moves, `30<=R<=50`. Result: **UNKNOWN after 240.1 s**, 282,332 conflicts,
  no witness. This is also not an infeasibility certificate.
- The solver model was retained in ST1's `fresh_global_cats13.model.json`; the
  FRESH receipts are `fresh_global_cats13.log` and `fresh_global_relaxed.log`.
  No circuit was emitted by either run, so there is no score to promote.

The verified continuation therefore remains the R48 FRESH circuit. The global
model's unresolved search space is the next durable route: the solver did not
prove R<=40 impossible, and both relaxations still stopped before a complete
placement witness.

## Warm-started global optimization (2026-10-24)

I added `warm_redesign.py` in FRESH. It imports the global CP-SAT placement
object read-only, transfers every primary placement, prefix-time/location,
route, permutation, endpoint, and encoder-job value from a compatible solver
witness as a deduplicated `AddHint`, and has a fixed-hint validation mode.
The catalog-compatible fixed check (`warm_cdirect_fix`) returned **OPTIMAL** at
R55 with zero conflicts and objective 55,005,759. The direct encoder variant
(`warm_direct_fix`) also returned **OPTIMAL** at the same R55 assignment.

The required long run was then:

```
warm_redesign.py --out warm_direct_long \
  --hint ST1/catalog_cdirect_freeprefix_w30.solver.json \
  --direct-encoder ST1/inputs/endstate12_cdirect.json \
  --moves 1 --data-moves 6 --min-round 30 --max-round 55 \
  --free-prefix --workers 16 --seconds 3600 --progress
```

This is the global placement model with the direct 10/11/11-CX encoder family;
all cells, prefix placement and times, routes, permutations, endpoints, and
encoder-job times remained free. CP-SAT ran 3,601.4 s and produced six
incumbents, all R55. The best objective improved from 55,005,759 to 55,005,718;
the best bound rose from 29,997,420 to 36,002,320. The run is **FEASIBLE**, not
optimal and not an infeasibility certificate. Its incumbent/bound trace is
`warm_direct_long.progress.jsonl`, and the full receipt is
`warm_direct_long.receipt.json`.

I emitted the final incumbent as
`warm_direct_long_incumbent.qasm` and priced it with unchanged exact2 through
third order: second **1.837478e-4**, third **1.171556e-4**, total
**3.009034e-4**, exp(-A1) **0.419531**. It is therefore rejected by the
acceptance gate and is far worse than v30f. The mechanism is the model's
independent A/B/C resource plus R55 exposure; it is a placement-model witness,
not a correlated rank-three candidate. No R<55 incumbent was emitted or
priced. The correlated v30f resource is not represented by this independent
encoder model, so it was not falsely claimed as a hint for that resource.

### Region LNS and R40 scope

Starting from the same verified direct-encoder assignment, I fixed all primary
variables outside one region at a time and minimized the same lexicographic
objective. Every single-region neighborhood returned OPTIMAL at R55:

| neighborhood freed | time | objective | result |
|---|---:|---:|---|
| resource cells/stages and resource jobs | 5.9 s | 55,005,731 | R55 optimal |
| data routes/jobs | 0.25 s | 55,005,740 | R55 optimal |
| prefix units (all) | 0.09 s | 55,005,759 | R55 optimal |
| late prefix units (indices >=90) | 0.03 s | 55,005,759 | R55 optimal |
| endpoints/permutations | 0.06 s | 55,005,759 | R55 optimal |

These are certificates only for the stated one-region neighborhoods with all
other incumbent values fixed; they show that a simultaneous change is required.
The receipts and progress traces are `lns_resource.*`, `lns_data.*`,
`lns_prefix.*`, `lns_late_prefix.*`, and `lns_endpoints.*`.

Finally, the unconstrained direct-encoder model with `30<=R<=40`, 16 workers,
and the warm values that remain in range ran 600.6 s. It had **no feasible
incumbent**; its objective upper value was 40,005,719 and its lower bound was
35,002,207. This is an UNKNOWN search result, not an R40 infeasibility proof.
Receipt: `joint_r40_direct_retry.receipt.json`.

The nearest relaxation `30<=R<=45` for the same direct global model also ran
600.5 s with no feasible witness (UNKNOWN); its lower bound was 34,002,286 and
its objective upper value 45,006,684. This model therefore cannot reproduce the
known R45/R48 lineages within the cats13/base logical prefix and direct
10/11/11 encoder abstraction, so that absence is a model-coverage result, not a
claim that the physical contest problem is infeasible. Receipt:
`joint_r45_direct.receipt.json`.

The first v29c transplant attempt used the stale 11-layer prep file and failed
BCPOL's endpoint contract (stim target/policy); the corrected 12-layer resource
embedded in the v30f plan was used for the verified v29c result below.


## v29c prefix with correlated rank-three resource

I re-synthesized the complete transplant on COMP29's newer v29c cultivation
prefix rather than using the direct-encoder abstraction. v29c has two fewer old
B/C operations than the original BCPOL 96-operation pattern, so the FRESH-local
`v29_assemble.py` relaxes only that historical count assertion; all endpoint
verification, detector frame propagation, and nearest-neighbour checks remain
unchanged. A four-tick retime window is required for schedule feasibility; the
zero-window model is infeasible because the v29c local edits occupy two of the
old B/C slots.

Best stem: `corr_d11_k57_s35_002_v29c_w4_fast` (the `fast` and reset files are
byte-identical). It has R48, native depth51, 190 CX, and data qubits
[0,20,7,10,3,22,21]. Verification receipts:

- `exact2.py --third`: c1 **2.4055e-19**, second **4.58341e-5**, third
  **1.19605e-5**, total **5.77946e-5**, exp(-A1) **0.52393**.
- `fast_check.py` at 1e6: **PASS**, acceptance **0.522492**, score
  **7.36853e-5**, 190 CX, **3.5 s** single-process (FAST).
- `MAIN/spec/mc3.py --procs 8`: seed0 **6.052211e-5**, seed1000
  **5.742665e-5**, seed2000 **5.853172e-5**, mean **5.882683e-5**,
  seed-0 acceptance **0.52378**.

The exact loss split is flip **1.050e-6**, gate **2.144e-5**, idle
**2.335e-5**. The leading pair remains q7 X idle t20--23 × q20 Y idle t40--46
(**7.731e-7**); v29c's two-slot local edits do not remove that cross-region
exposure, but they reduce the total gate/idle interaction enough to beat v30f by
**4.447e-7**. This is a complete physical grid circuit and is the current FRESH
best; it is still above the 5e-5 target.

### v29c resource sweep and retiming controls

I transplanted the other endpoint-valid d11 resources onto v29c at the smallest
feasible retime windows. Their exact third-order totals were:

| resource | v29c window | total | mechanism |
|---|---:|---:|---|
| s33_001 | 8 | 6.30960e-5 | larger flip/idle exposure |
| s33_002 | 4 | 6.47894e-5 | gate and idle terms both increase |
| s33_003 | 4 | 6.00773e-5 | lower than v30f but above s35 |
| s33_004 | 4 | 6.02044e-5 | same cross-region idle pair remains |

The s34/s35 alternative resources were assembled successfully where the window
allowed; the priced s34_001 control is 6.83734e-5, while the remaining assembled
controls are not yet exact-priced. On the current best resource,
`timing=asap` gives **4.93011e-4** because it exposes live blocks for many extra
steps, and `timing=project` gives **8.09005e-5** from incompatible release
alignment. ALAP remains the correct schedule for this endpoint and prefix.

A direct round-shift probe on the v29c+correlated assembly (`round_shift=-1,-2,-3`,
retime window4, ALAP) is schedule-infeasible in BCPOL's native per-wire model.
This closes only the fixed v29c/resource placement and release model; it is not a
bound on a new joint re-embedding.

The assembled s34_001 v29c control was exact-priced as a negative result:
second 5.63944e-5 + third 1.19789e-5 = **6.83734e-5**, exp(-A1)=0.52512;
its mechanism is the extra flip exposure (4.816e-6) and larger gate/idle terms.
