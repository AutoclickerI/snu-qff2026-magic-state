# BCFB — A decoder on v34m

Status: completed carryover sweep (400 queued jobs, zero evaluator errors). All work remains in BCFB. No submissions, credentials, commits, pushes, or subagents.

Verified improvements over v34m (baseline supplied: 4.66293e-5, acceptance 0.50120). Rank is all-orders loss.

| Candidate | All-orders loss | Acceptance | CX | XTIM s/1e6 | MC seeds 0 / 1000 / 2000 | MC mean |
|---|---:|---:|---:|---:|---|---:|
| [zreuse_00006](a34/candidates/zreuse_00006.qasm) | 4.622113038816e-05 | 0.501686185123 | 207 | 11.133 | 4.645723e-05 / 4.519288e-05 / 4.690626e-05 | 4.6185457e-05 |
| [zreuse_00010](a34/candidates/zreuse_00010.qasm) | 4.622708420647e-05 | 0.502522970720 | 207 | 13.614 | 4.606432e-05 / 4.583197e-05 / 4.679833e-05 | 4.623154e-05 |
| [earlyflags_00003](a34/candidates/earlyflags_00003.qasm) | 4.626904458176e-05 | 0.503195717485 | 207 | 7.765 | 4.619289e-05 / 4.667779e-05 / 4.83201e-05 | 4.7063593e-05 |
| [encoders_00013](a34/candidates/encoders_00013.qasm) | 4.63635152318e-05 | 0.502998420495 | 207 | 5.161 | 4.738281e-05 / 4.740832e-05 / 4.710053e-05 | 4.729722e-05 |
| [encoders_00014](a34/candidates/encoders_00014.qasm) | 4.650193980923e-05 | 0.505522732439 | 207 | 6.995 | 4.859908e-05 / 4.674919e-05 / 4.628809e-05 | 4.721212e-05 |
| [encoders_00004](a34/candidates/encoders_00004.qasm) | 4.650946485522e-05 | 0.504006831695 | 207 | 8.938 | 4.665008e-05 / 4.756201e-05 / 4.703281e-05 | 4.7081633e-05 |
| [encoders_00009](a34/candidates/encoders_00009.qasm) | 4.650946485522e-05 | 0.504006831695 | 207 | 5.706 | 4.709269e-05 / 4.571283e-05 / 4.640485e-05 | 4.6403457e-05 |
| [encoders_00000](a34/candidates/encoders_00000.qasm) | 4.655288147445e-05 | 0.504679442285 | 207 | 8.021 | 4.650571e-05 / 4.677746e-05 / 4.638453e-05 | 4.65559e-05 |
| [encoders_00005](a34/candidates/encoders_00005.qasm) | 4.655288147445e-05 | 0.504679442285 | 207 | 8.318 | 4.702396e-05 / 4.538282e-05 / 4.636683e-05 | 4.625787e-05 |
| [encoders_00002](a34/candidates/encoders_00002.qasm) | 4.661944598688e-05 | 0.504512988201 | 207 | 8.723 | 4.701415e-05 / 4.553393e-05 / 4.617231e-05 | 4.624013e-05 |
| [encoders_00007](a34/candidates/encoders_00007.qasm) | 4.661944598688e-05 | 0.504512988201 | 207 | 6.174 | 4.525385e-05 / 4.726883e-05 / 4.538583e-05 | 4.5969503e-05 |

Prior v30f A-side search: [REPORT_a30_completed.md](REPORT_a30_completed.md).

Source v34m metadata contained inherited v31s counts and verdicts. Frozen input metadata records only measured v34m structure; new candidates carry independent receipts.
