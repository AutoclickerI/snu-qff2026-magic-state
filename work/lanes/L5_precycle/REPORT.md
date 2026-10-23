# Lane L5: pre-cycle optimization

Updated 2026-10-23 18:10:28 KST.

Scope: injection, double-cat check, and their boundary with the v6 final cycle. No submissions. All generated files stay in this lane. At most one parent plus seven worker processes; numerical-library threads capped at one.

Baseline reference: v6, 1-F = 0.0001310302140991363; 113 CX. Official setting is 100,000,000 shots, seed 0, unmodified real-grid STANDARD noise. A candidate is eligible only with passed=True and fault_scan c1=0. Ranking uses score rounded to 3 significant figures, then CX count.

| Change | 1-F (official) | Δ vs v6 | 2q | Acceptance | passed | c1 | Depth | Eligible win |
|---|---:|---:|---:|---:|---|---:|---:|---|
| v6_recheck | 0.0001310302141 | 0 | 113 | 0.66610591 | True | 3.700743415e-17 | 45 | False |
| boundary_unlocked | 0.0001310302141 | 0 | 113 | 0.66610591 | True | 3.700743415e-17 | 45 | False |
| all_asap | 0.0001938734874 | 6.284327333e-05 | 113 | 0.67048879 | True | 3.700743415e-17 | 45 | False |
| pre_asap_ordered | 0.0001310302141 | 0 | 113 | 0.66610591 | True | 3.700743415e-17 | 45 | False |
| pre_asap_commute | 0.0001336848871 | 2.654673011e-06 | 113 | 0.68620322 | True | 3.700743415e-17 | 42 | False |
| pre_alap_ordered | 0.0001286284176 | -2.401796474e-06 | 113 | 0.66750413 | True | 0 | 45 | True |

## Verified improvements

- [pre_alap_ordered](pre_alap_ordered.qasm), [metadata](pre_alap_ordered.json): 0.000128628417625, 113 CX, c1=0.0.
