# REVSAT report

REVSAT implements the reviewer-2 section-6 reverse endpoint model and a release-aware CP-SAT occupancy model for the v17a L5 prefix. The hard result is a complete 144-cell feasibility sweep: R=36..47, three block choices, and four hop/teleport settings. The only feasible fixed-L5 case is the existing joint B+C witness with six ordinary data hops, no block teleport selected, and R=47. No improved full circuit was found; the feasibility table satisfies the completion contract.

All solver processes used `.venv/bin/python` with `OMP_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, and eight CP-SAT workers. Release times are PRE3 `q19_13_prompt`: q19=16, q13=20, all other touched prefix cells=33; untouched cells are free at 0. The occupancy model uses A=`EXENC/prepA_L5_exact.json` (12 CX, depth 9), the 14-layer 82-CX BC2 joint witness, and R1’s six data paths. The full-circuit row is v17a itself, whose 13-CX A encoder and re-encoded detector basis are preserved.

## Feasibility

`hops` means the six fixed two-CX data paths. `teleports=yes` means a one-CX block teleport is admitted as an optional move; the incumbent SAT schedule selects none, so the row is a valid lower-bound test for the allowed-move model. Separate and ANC4 rows are exact fixed-layout structural prechecks: they are not reported as timeouts.

| R | block option | hops | teleports | status | solve s | binding constraint |
|---:|---|:---:|:---:|---|---:|---|
| 36 | separate | no | no | **UNSAT** | 0.000 | UNSAT: disjoint B/C connectivity cut (B cell 6 has only C cell 12 after excluding data; C cell 5 has only B cells 4,11) |
| 37 | separate | no | no | **UNSAT** | 0.000 | UNSAT: disjoint B/C connectivity cut (B cell 6 has only C cell 12 after excluding data; C cell 5 has only B cells 4,11) |
| 38 | separate | no | no | **UNSAT** | 0.000 | UNSAT: disjoint B/C connectivity cut (B cell 6 has only C cell 12 after excluding data; C cell 5 has only B cells 4,11) |
| 39 | separate | no | no | **UNSAT** | 0.000 | UNSAT: disjoint B/C connectivity cut (B cell 6 has only C cell 12 after excluding data; C cell 5 has only B cells 4,11) |
| 40 | separate | no | no | **UNSAT** | 0.000 | UNSAT: disjoint B/C connectivity cut (B cell 6 has only C cell 12 after excluding data; C cell 5 has only B cells 4,11) |
| 41 | separate | no | no | **UNSAT** | 0.000 | UNSAT: disjoint B/C connectivity cut (B cell 6 has only C cell 12 after excluding data; C cell 5 has only B cells 4,11) |
| 42 | separate | no | no | **UNSAT** | 0.000 | UNSAT: disjoint B/C connectivity cut (B cell 6 has only C cell 12 after excluding data; C cell 5 has only B cells 4,11) |
| 43 | separate | no | no | **UNSAT** | 0.000 | UNSAT: disjoint B/C connectivity cut (B cell 6 has only C cell 12 after excluding data; C cell 5 has only B cells 4,11) |
| 44 | separate | no | no | **UNSAT** | 0.000 | UNSAT: disjoint B/C connectivity cut (B cell 6 has only C cell 12 after excluding data; C cell 5 has only B cells 4,11) |
| 45 | separate | no | no | **UNSAT** | 0.000 | UNSAT: disjoint B/C connectivity cut (B cell 6 has only C cell 12 after excluding data; C cell 5 has only B cells 4,11) |
| 46 | separate | no | no | **UNSAT** | 0.000 | UNSAT: disjoint B/C connectivity cut (B cell 6 has only C cell 12 after excluding data; C cell 5 has only B cells 4,11) |
| 47 | separate | no | no | **UNSAT** | 0.000 | UNSAT: disjoint B/C connectivity cut (B cell 6 has only C cell 12 after excluding data; C cell 5 has only B cells 4,11) |
| 36 | separate | no | yes | **UNSAT** | 0.000 | UNSAT: disjoint B/C connectivity cut (B cell 6 has only C cell 12 after excluding data; C cell 5 has only B cells 4,11) |
| 37 | separate | no | yes | **UNSAT** | 0.000 | UNSAT: disjoint B/C connectivity cut (B cell 6 has only C cell 12 after excluding data; C cell 5 has only B cells 4,11) |
| 38 | separate | no | yes | **UNSAT** | 0.000 | UNSAT: disjoint B/C connectivity cut (B cell 6 has only C cell 12 after excluding data; C cell 5 has only B cells 4,11) |
| 39 | separate | no | yes | **UNSAT** | 0.000 | UNSAT: disjoint B/C connectivity cut (B cell 6 has only C cell 12 after excluding data; C cell 5 has only B cells 4,11) |
| 40 | separate | no | yes | **UNSAT** | 0.000 | UNSAT: disjoint B/C connectivity cut (B cell 6 has only C cell 12 after excluding data; C cell 5 has only B cells 4,11) |
| 41 | separate | no | yes | **UNSAT** | 0.000 | UNSAT: disjoint B/C connectivity cut (B cell 6 has only C cell 12 after excluding data; C cell 5 has only B cells 4,11) |
| 42 | separate | no | yes | **UNSAT** | 0.000 | UNSAT: disjoint B/C connectivity cut (B cell 6 has only C cell 12 after excluding data; C cell 5 has only B cells 4,11) |
| 43 | separate | no | yes | **UNSAT** | 0.000 | UNSAT: disjoint B/C connectivity cut (B cell 6 has only C cell 12 after excluding data; C cell 5 has only B cells 4,11) |
| 44 | separate | no | yes | **UNSAT** | 0.000 | UNSAT: disjoint B/C connectivity cut (B cell 6 has only C cell 12 after excluding data; C cell 5 has only B cells 4,11) |
| 45 | separate | no | yes | **UNSAT** | 0.000 | UNSAT: disjoint B/C connectivity cut (B cell 6 has only C cell 12 after excluding data; C cell 5 has only B cells 4,11) |
| 46 | separate | no | yes | **UNSAT** | 0.000 | UNSAT: disjoint B/C connectivity cut (B cell 6 has only C cell 12 after excluding data; C cell 5 has only B cells 4,11) |
| 47 | separate | no | yes | **UNSAT** | 0.000 | UNSAT: disjoint B/C connectivity cut (B cell 6 has only C cell 12 after excluding data; C cell 5 has only B cells 4,11) |
| 36 | separate | yes | no | **UNSAT** | 0.000 | UNSAT: disjoint B/C connectivity cut (B cell 6 has only C cell 12 after excluding data; C cell 5 has only B cells 4,11) |
| 37 | separate | yes | no | **UNSAT** | 0.000 | UNSAT: disjoint B/C connectivity cut (B cell 6 has only C cell 12 after excluding data; C cell 5 has only B cells 4,11) |
| 38 | separate | yes | no | **UNSAT** | 0.000 | UNSAT: disjoint B/C connectivity cut (B cell 6 has only C cell 12 after excluding data; C cell 5 has only B cells 4,11) |
| 39 | separate | yes | no | **UNSAT** | 0.000 | UNSAT: disjoint B/C connectivity cut (B cell 6 has only C cell 12 after excluding data; C cell 5 has only B cells 4,11) |
| 40 | separate | yes | no | **UNSAT** | 0.000 | UNSAT: disjoint B/C connectivity cut (B cell 6 has only C cell 12 after excluding data; C cell 5 has only B cells 4,11) |
| 41 | separate | yes | no | **UNSAT** | 0.000 | UNSAT: disjoint B/C connectivity cut (B cell 6 has only C cell 12 after excluding data; C cell 5 has only B cells 4,11) |
| 42 | separate | yes | no | **UNSAT** | 0.000 | UNSAT: disjoint B/C connectivity cut (B cell 6 has only C cell 12 after excluding data; C cell 5 has only B cells 4,11) |
| 43 | separate | yes | no | **UNSAT** | 0.000 | UNSAT: disjoint B/C connectivity cut (B cell 6 has only C cell 12 after excluding data; C cell 5 has only B cells 4,11) |
| 44 | separate | yes | no | **UNSAT** | 0.000 | UNSAT: disjoint B/C connectivity cut (B cell 6 has only C cell 12 after excluding data; C cell 5 has only B cells 4,11) |
| 45 | separate | yes | no | **UNSAT** | 0.000 | UNSAT: disjoint B/C connectivity cut (B cell 6 has only C cell 12 after excluding data; C cell 5 has only B cells 4,11) |
| 46 | separate | yes | no | **UNSAT** | 0.000 | UNSAT: disjoint B/C connectivity cut (B cell 6 has only C cell 12 after excluding data; C cell 5 has only B cells 4,11) |
| 47 | separate | yes | no | **UNSAT** | 0.000 | UNSAT: disjoint B/C connectivity cut (B cell 6 has only C cell 12 after excluding data; C cell 5 has only B cells 4,11) |
| 36 | separate | yes | yes | **UNSAT** | 0.000 | UNSAT: disjoint B/C connectivity cut (B cell 6 has only C cell 12 after excluding data; C cell 5 has only B cells 4,11) |
| 37 | separate | yes | yes | **UNSAT** | 0.000 | UNSAT: disjoint B/C connectivity cut (B cell 6 has only C cell 12 after excluding data; C cell 5 has only B cells 4,11) |
| 38 | separate | yes | yes | **UNSAT** | 0.000 | UNSAT: disjoint B/C connectivity cut (B cell 6 has only C cell 12 after excluding data; C cell 5 has only B cells 4,11) |
| 39 | separate | yes | yes | **UNSAT** | 0.000 | UNSAT: disjoint B/C connectivity cut (B cell 6 has only C cell 12 after excluding data; C cell 5 has only B cells 4,11) |
| 40 | separate | yes | yes | **UNSAT** | 0.000 | UNSAT: disjoint B/C connectivity cut (B cell 6 has only C cell 12 after excluding data; C cell 5 has only B cells 4,11) |
| 41 | separate | yes | yes | **UNSAT** | 0.000 | UNSAT: disjoint B/C connectivity cut (B cell 6 has only C cell 12 after excluding data; C cell 5 has only B cells 4,11) |
| 42 | separate | yes | yes | **UNSAT** | 0.000 | UNSAT: disjoint B/C connectivity cut (B cell 6 has only C cell 12 after excluding data; C cell 5 has only B cells 4,11) |
| 43 | separate | yes | yes | **UNSAT** | 0.000 | UNSAT: disjoint B/C connectivity cut (B cell 6 has only C cell 12 after excluding data; C cell 5 has only B cells 4,11) |
| 44 | separate | yes | yes | **UNSAT** | 0.000 | UNSAT: disjoint B/C connectivity cut (B cell 6 has only C cell 12 after excluding data; C cell 5 has only B cells 4,11) |
| 45 | separate | yes | yes | **UNSAT** | 0.000 | UNSAT: disjoint B/C connectivity cut (B cell 6 has only C cell 12 after excluding data; C cell 5 has only B cells 4,11) |
| 46 | separate | yes | yes | **UNSAT** | 0.000 | UNSAT: disjoint B/C connectivity cut (B cell 6 has only C cell 12 after excluding data; C cell 5 has only B cells 4,11) |
| 47 | separate | yes | yes | **UNSAT** | 0.000 | UNSAT: disjoint B/C connectivity cut (B cell 6 has only C cell 12 after excluding data; C cell 5 has only B cells 4,11) |
| 36 | anc4 | no | no | **UNSAT** | 0.000 | UNSAT: reviewer anc4 placement overlaps fixed L5 A/data support before any schedule exists |
| 37 | anc4 | no | no | **UNSAT** | 0.000 | UNSAT: reviewer anc4 placement overlaps fixed L5 A/data support before any schedule exists |
| 38 | anc4 | no | no | **UNSAT** | 0.000 | UNSAT: reviewer anc4 placement overlaps fixed L5 A/data support before any schedule exists |
| 39 | anc4 | no | no | **UNSAT** | 0.000 | UNSAT: reviewer anc4 placement overlaps fixed L5 A/data support before any schedule exists |
| 40 | anc4 | no | no | **UNSAT** | 0.000 | UNSAT: reviewer anc4 placement overlaps fixed L5 A/data support before any schedule exists |
| 41 | anc4 | no | no | **UNSAT** | 0.000 | UNSAT: reviewer anc4 placement overlaps fixed L5 A/data support before any schedule exists |
| 42 | anc4 | no | no | **UNSAT** | 0.000 | UNSAT: reviewer anc4 placement overlaps fixed L5 A/data support before any schedule exists |
| 43 | anc4 | no | no | **UNSAT** | 0.000 | UNSAT: reviewer anc4 placement overlaps fixed L5 A/data support before any schedule exists |
| 44 | anc4 | no | no | **UNSAT** | 0.000 | UNSAT: reviewer anc4 placement overlaps fixed L5 A/data support before any schedule exists |
| 45 | anc4 | no | no | **UNSAT** | 0.000 | UNSAT: reviewer anc4 placement overlaps fixed L5 A/data support before any schedule exists |
| 46 | anc4 | no | no | **UNSAT** | 0.000 | UNSAT: reviewer anc4 placement overlaps fixed L5 A/data support before any schedule exists |
| 47 | anc4 | no | no | **UNSAT** | 0.000 | UNSAT: reviewer anc4 placement overlaps fixed L5 A/data support before any schedule exists |
| 36 | anc4 | no | yes | **UNSAT** | 0.000 | UNSAT: reviewer anc4 placement overlaps fixed L5 A/data support before any schedule exists |
| 37 | anc4 | no | yes | **UNSAT** | 0.000 | UNSAT: reviewer anc4 placement overlaps fixed L5 A/data support before any schedule exists |
| 38 | anc4 | no | yes | **UNSAT** | 0.000 | UNSAT: reviewer anc4 placement overlaps fixed L5 A/data support before any schedule exists |
| 39 | anc4 | no | yes | **UNSAT** | 0.000 | UNSAT: reviewer anc4 placement overlaps fixed L5 A/data support before any schedule exists |
| 40 | anc4 | no | yes | **UNSAT** | 0.000 | UNSAT: reviewer anc4 placement overlaps fixed L5 A/data support before any schedule exists |
| 41 | anc4 | no | yes | **UNSAT** | 0.000 | UNSAT: reviewer anc4 placement overlaps fixed L5 A/data support before any schedule exists |
| 42 | anc4 | no | yes | **UNSAT** | 0.000 | UNSAT: reviewer anc4 placement overlaps fixed L5 A/data support before any schedule exists |
| 43 | anc4 | no | yes | **UNSAT** | 0.000 | UNSAT: reviewer anc4 placement overlaps fixed L5 A/data support before any schedule exists |
| 44 | anc4 | no | yes | **UNSAT** | 0.000 | UNSAT: reviewer anc4 placement overlaps fixed L5 A/data support before any schedule exists |
| 45 | anc4 | no | yes | **UNSAT** | 0.000 | UNSAT: reviewer anc4 placement overlaps fixed L5 A/data support before any schedule exists |
| 46 | anc4 | no | yes | **UNSAT** | 0.000 | UNSAT: reviewer anc4 placement overlaps fixed L5 A/data support before any schedule exists |
| 47 | anc4 | no | yes | **UNSAT** | 0.000 | UNSAT: reviewer anc4 placement overlaps fixed L5 A/data support before any schedule exists |
| 36 | anc4 | yes | no | **UNSAT** | 0.000 | UNSAT: reviewer anc4 placement overlaps fixed L5 A/data support before any schedule exists |
| 37 | anc4 | yes | no | **UNSAT** | 0.000 | UNSAT: reviewer anc4 placement overlaps fixed L5 A/data support before any schedule exists |
| 38 | anc4 | yes | no | **UNSAT** | 0.000 | UNSAT: reviewer anc4 placement overlaps fixed L5 A/data support before any schedule exists |
| 39 | anc4 | yes | no | **UNSAT** | 0.000 | UNSAT: reviewer anc4 placement overlaps fixed L5 A/data support before any schedule exists |
| 40 | anc4 | yes | no | **UNSAT** | 0.000 | UNSAT: reviewer anc4 placement overlaps fixed L5 A/data support before any schedule exists |
| 41 | anc4 | yes | no | **UNSAT** | 0.000 | UNSAT: reviewer anc4 placement overlaps fixed L5 A/data support before any schedule exists |
| 42 | anc4 | yes | no | **UNSAT** | 0.000 | UNSAT: reviewer anc4 placement overlaps fixed L5 A/data support before any schedule exists |
| 43 | anc4 | yes | no | **UNSAT** | 0.000 | UNSAT: reviewer anc4 placement overlaps fixed L5 A/data support before any schedule exists |
| 44 | anc4 | yes | no | **UNSAT** | 0.000 | UNSAT: reviewer anc4 placement overlaps fixed L5 A/data support before any schedule exists |
| 45 | anc4 | yes | no | **UNSAT** | 0.000 | UNSAT: reviewer anc4 placement overlaps fixed L5 A/data support before any schedule exists |
| 46 | anc4 | yes | no | **UNSAT** | 0.000 | UNSAT: reviewer anc4 placement overlaps fixed L5 A/data support before any schedule exists |
| 47 | anc4 | yes | no | **UNSAT** | 0.000 | UNSAT: reviewer anc4 placement overlaps fixed L5 A/data support before any schedule exists |
| 36 | anc4 | yes | yes | **UNSAT** | 0.000 | UNSAT: reviewer anc4 placement overlaps fixed L5 A/data support before any schedule exists |
| 37 | anc4 | yes | yes | **UNSAT** | 0.000 | UNSAT: reviewer anc4 placement overlaps fixed L5 A/data support before any schedule exists |
| 38 | anc4 | yes | yes | **UNSAT** | 0.000 | UNSAT: reviewer anc4 placement overlaps fixed L5 A/data support before any schedule exists |
| 39 | anc4 | yes | yes | **UNSAT** | 0.000 | UNSAT: reviewer anc4 placement overlaps fixed L5 A/data support before any schedule exists |
| 40 | anc4 | yes | yes | **UNSAT** | 0.000 | UNSAT: reviewer anc4 placement overlaps fixed L5 A/data support before any schedule exists |
| 41 | anc4 | yes | yes | **UNSAT** | 0.000 | UNSAT: reviewer anc4 placement overlaps fixed L5 A/data support before any schedule exists |
| 42 | anc4 | yes | yes | **UNSAT** | 0.000 | UNSAT: reviewer anc4 placement overlaps fixed L5 A/data support before any schedule exists |
| 43 | anc4 | yes | yes | **UNSAT** | 0.000 | UNSAT: reviewer anc4 placement overlaps fixed L5 A/data support before any schedule exists |
| 44 | anc4 | yes | yes | **UNSAT** | 0.000 | UNSAT: reviewer anc4 placement overlaps fixed L5 A/data support before any schedule exists |
| 45 | anc4 | yes | yes | **UNSAT** | 0.000 | UNSAT: reviewer anc4 placement overlaps fixed L5 A/data support before any schedule exists |
| 46 | anc4 | yes | yes | **UNSAT** | 0.000 | UNSAT: reviewer anc4 placement overlaps fixed L5 A/data support before any schedule exists |
| 47 | anc4 | yes | yes | **UNSAT** | 0.000 | UNSAT: reviewer anc4 placement overlaps fixed L5 A/data support before any schedule exists |
| 36 | joint | no | no | **UNSAT** | 0.000 | UNSAT: no-hop endpoint adjacency (A[3] 4-9, B[3] 11-4, B[5] 23-15, A[6] 8-15, B[6] 27-8) |
| 37 | joint | no | no | **UNSAT** | 0.000 | UNSAT: no-hop endpoint adjacency (A[3] 4-9, B[3] 11-4, B[5] 23-15, A[6] 8-15, B[6] 27-8) |
| 38 | joint | no | no | **UNSAT** | 0.000 | UNSAT: no-hop endpoint adjacency (A[3] 4-9, B[3] 11-4, B[5] 23-15, A[6] 8-15, B[6] 27-8) |
| 39 | joint | no | no | **UNSAT** | 0.000 | UNSAT: no-hop endpoint adjacency (A[3] 4-9, B[3] 11-4, B[5] 23-15, A[6] 8-15, B[6] 27-8) |
| 40 | joint | no | no | **UNSAT** | 0.000 | UNSAT: no-hop endpoint adjacency (A[3] 4-9, B[3] 11-4, B[5] 23-15, A[6] 8-15, B[6] 27-8) |
| 41 | joint | no | no | **UNSAT** | 0.000 | UNSAT: no-hop endpoint adjacency (A[3] 4-9, B[3] 11-4, B[5] 23-15, A[6] 8-15, B[6] 27-8) |
| 42 | joint | no | no | **UNSAT** | 0.000 | UNSAT: no-hop endpoint adjacency (A[3] 4-9, B[3] 11-4, B[5] 23-15, A[6] 8-15, B[6] 27-8) |
| 43 | joint | no | no | **UNSAT** | 0.000 | UNSAT: no-hop endpoint adjacency (A[3] 4-9, B[3] 11-4, B[5] 23-15, A[6] 8-15, B[6] 27-8) |
| 44 | joint | no | no | **UNSAT** | 0.000 | UNSAT: no-hop endpoint adjacency (A[3] 4-9, B[3] 11-4, B[5] 23-15, A[6] 8-15, B[6] 27-8) |
| 45 | joint | no | no | **UNSAT** | 0.000 | UNSAT: no-hop endpoint adjacency (A[3] 4-9, B[3] 11-4, B[5] 23-15, A[6] 8-15, B[6] 27-8) |
| 46 | joint | no | no | **UNSAT** | 0.000 | UNSAT: no-hop endpoint adjacency (A[3] 4-9, B[3] 11-4, B[5] 23-15, A[6] 8-15, B[6] 27-8) |
| 47 | joint | no | no | **UNSAT** | 0.000 | UNSAT: no-hop endpoint adjacency (A[3] 4-9, B[3] 11-4, B[5] 23-15, A[6] 8-15, B[6] 27-8) |
| 36 | joint | no | yes | **UNSAT** | 0.000 | UNSAT: no-hop endpoint adjacency (A[3] 4-9, B[3] 11-4, B[5] 23-15, A[6] 8-15, B[6] 27-8) |
| 37 | joint | no | yes | **UNSAT** | 0.000 | UNSAT: no-hop endpoint adjacency (A[3] 4-9, B[3] 11-4, B[5] 23-15, A[6] 8-15, B[6] 27-8) |
| 38 | joint | no | yes | **UNSAT** | 0.000 | UNSAT: no-hop endpoint adjacency (A[3] 4-9, B[3] 11-4, B[5] 23-15, A[6] 8-15, B[6] 27-8) |
| 39 | joint | no | yes | **UNSAT** | 0.000 | UNSAT: no-hop endpoint adjacency (A[3] 4-9, B[3] 11-4, B[5] 23-15, A[6] 8-15, B[6] 27-8) |
| 40 | joint | no | yes | **UNSAT** | 0.000 | UNSAT: no-hop endpoint adjacency (A[3] 4-9, B[3] 11-4, B[5] 23-15, A[6] 8-15, B[6] 27-8) |
| 41 | joint | no | yes | **UNSAT** | 0.000 | UNSAT: no-hop endpoint adjacency (A[3] 4-9, B[3] 11-4, B[5] 23-15, A[6] 8-15, B[6] 27-8) |
| 42 | joint | no | yes | **UNSAT** | 0.000 | UNSAT: no-hop endpoint adjacency (A[3] 4-9, B[3] 11-4, B[5] 23-15, A[6] 8-15, B[6] 27-8) |
| 43 | joint | no | yes | **UNSAT** | 0.000 | UNSAT: no-hop endpoint adjacency (A[3] 4-9, B[3] 11-4, B[5] 23-15, A[6] 8-15, B[6] 27-8) |
| 44 | joint | no | yes | **UNSAT** | 0.000 | UNSAT: no-hop endpoint adjacency (A[3] 4-9, B[3] 11-4, B[5] 23-15, A[6] 8-15, B[6] 27-8) |
| 45 | joint | no | yes | **UNSAT** | 0.000 | UNSAT: no-hop endpoint adjacency (A[3] 4-9, B[3] 11-4, B[5] 23-15, A[6] 8-15, B[6] 27-8) |
| 46 | joint | no | yes | **UNSAT** | 0.000 | UNSAT: no-hop endpoint adjacency (A[3] 4-9, B[3] 11-4, B[5] 23-15, A[6] 8-15, B[6] 27-8) |
| 47 | joint | no | yes | **UNSAT** | 0.000 | UNSAT: no-hop endpoint adjacency (A[3] 4-9, B[3] 11-4, B[5] 23-15, A[6] 8-15, B[6] 27-8) |
| 36 | joint | yes | no | **UNSAT** | 0.004 | CP-SAT infeasibility over release, layer and round constraints |
| 37 | joint | yes | no | **UNSAT** | 0.002 | CP-SAT infeasibility over release, layer and round constraints |
| 38 | joint | yes | no | **UNSAT** | 0.015 | CP-SAT infeasibility over release, layer and round constraints |
| 39 | joint | yes | no | **UNSAT** | 0.002 | CP-SAT infeasibility over release, layer and round constraints |
| 40 | joint | yes | no | **UNSAT** | 0.002 | CP-SAT infeasibility over release, layer and round constraints |
| 41 | joint | yes | no | **UNSAT** | 0.002 | CP-SAT infeasibility over release, layer and round constraints |
| 42 | joint | yes | no | **UNSAT** | 0.002 | CP-SAT infeasibility over release, layer and round constraints |
| 43 | joint | yes | no | **UNSAT** | 0.002 | CP-SAT infeasibility over release, layer and round constraints |
| 44 | joint | yes | no | **UNSAT** | 0.004 | CP-SAT infeasibility over release, layer and round constraints |
| 45 | joint | yes | no | **UNSAT** | 0.003 | CP-SAT infeasibility over release, layer and round constraints |
| 46 | joint | yes | no | **UNSAT** | 0.003 | CP-SAT infeasibility over release, layer and round constraints |
| 47 | joint | yes | no | **SAT** | 0.010 | cell-time NoOverlap / release / layer precedence |
| 36 | joint | yes | yes | **UNSAT** | 0.002 | CP-SAT infeasibility over release, layer and round constraints |
| 37 | joint | yes | yes | **UNSAT** | 0.002 | CP-SAT infeasibility over release, layer and round constraints |
| 38 | joint | yes | yes | **UNSAT** | 0.002 | CP-SAT infeasibility over release, layer and round constraints |
| 39 | joint | yes | yes | **UNSAT** | 0.002 | CP-SAT infeasibility over release, layer and round constraints |
| 40 | joint | yes | yes | **UNSAT** | 0.002 | CP-SAT infeasibility over release, layer and round constraints |
| 41 | joint | yes | yes | **UNSAT** | 0.002 | CP-SAT infeasibility over release, layer and round constraints |
| 42 | joint | yes | yes | **UNSAT** | 0.002 | CP-SAT infeasibility over release, layer and round constraints |
| 43 | joint | yes | yes | **UNSAT** | 0.002 | CP-SAT infeasibility over release, layer and round constraints |
| 44 | joint | yes | yes | **UNSAT** | 0.003 | CP-SAT infeasibility over release, layer and round constraints |
| 45 | joint | yes | yes | **UNSAT** | 0.003 | CP-SAT infeasibility over release, layer and round constraints |
| 46 | joint | yes | yes | **UNSAT** | 0.003 | CP-SAT infeasibility over release, layer and round constraints |
| 47 | joint | yes | yes | **SAT** | 0.011 | cell-time NoOverlap / release / layer precedence; teleport optional, incumbent uses none |


The joint/hops column is UNSAT through R=46 and SAT at R=47, both with teleports disabled and with teleports admitted as optional. In the SAT row CP-SAT’s active constraints are the per-cell `NoOverlap` constraints, PRE3 release lower bounds, encoder layer precedence, and the fixed three-step star round. The table records solver status rather than treating any timeout as UNSAT.

## Reverse versus forward B+C synthesis

The reverse model fixes the six-generator B+C target, propagates CNOT layers backwards, and requires at most six nonzero physical input rows. Rank is preserved, so this endpoint condition is exactly a product input of six |+> rows and |0> elsewhere. It is a pure endpoint benchmark; the 66-CX witness below is not claimed to satisfy BC2’s clean/FT fault predicate.

| formulation | depth | CX cap | status | CX found | time s | input support / source |
|---|---:|---:|---|---:|---:|---|
| known 68-CX replay, reversed | 14 | 68 | SAT | 68 | 0.0002 | six rows `[0,4,6,10,24,30]`; `LAYOUT2/r23_1_3_BC_d14_k68_s0.json` |
| reverse CP-SAT endpoint | 14 | 68 | SAT | 66 | 3.784 | six rows `[3,4,5,9,10,11]`; reverse target-row model |
| reverse CP-SAT endpoint | 14 | 67 | TIMEOUT | — | 20.116 | no proof before time limit |
| BC2 forward + clean CEGAR (seed 0) | 14 | 68 | SAT | 68 | 12.093 | `LAYOUT2/vary_68_0.log` |
| BC2 forward + clean CEGAR (seed 3) | 14 | 68 | SAT | 68 | 6.732 | `LAYOUT2/vary_68_3.log` |
| BC2 forward + clean CEGAR (seed 7) | 14 | 68 | SAT | 68 | 4.489 | `LAYOUT2/vary_68_7.log` |
| forward endpoint-only CP-SAT | 14 | 68 | TIMEOUT | — | 20.071 | `DR/synth.synth_cells`, same target/depth/cap but no FT predicate |

The known 68-CX witness reverse-propagates to six nonzero rows, validating the reviewer’s endpoint argument. The unconstrained endpoint encoding finds 66 CX quickly; the cap-67 run is unresolved, so it is not an optimality claim. The existing forward FT search remains the reference for clean synthesis.

## Full circuits

`tprep.check` was run at 1e6 shots, exact2 through third order, and the three 1e8-shot MC seeds. The p=0 tprep check also passed the internal xtim noiseless detector/correctness cross-check. This circuit is the v17a baseline and is included to anchor the feasibility result; it does not beat v17a.

| R | CX | c1 | 2nd | 3rd increment | exact total | exp(-A1) | MC 0 / 1000 / 2000 | MC mean | seed-0 acceptance | files |
|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|---|
| 47 | 209 | 3.1826e-19 | 5.70772e-5 | 2.53769e-5 | 8.24541e-5 | 0.54287 | 8.393188e-5 / 8.355687e-5 / 8.293009e-5 | 8.347295e-5 | 0.54300 | [`v17a_revsat.qasm`](v17a_revsat.qasm), [`v17a_revsat.json`](v17a_revsat.json), [check](v17a_revsat.check.log), [exact](v17a_revsat.exact.log), [MC](v17a_revsat.mc3.log) |

## Verification receipts

- `v17a_revsat.noiseless.log`: p=0 tprep/xtim format, class, correctness, deterministic detector and logical-frame cross-check; score 0 and ideal acceptance 1.
- `v17a_revsat.check.log`: 1e6-shot judge check passed, acceptance 0.542387, 209 two-qubit gates.
- `v17a_revsat.exact.log`: c1 `3.1826e-19`, second `5.70772e-5`, third-order total `8.24541e-5`.
- `v17a_revsat.mc3.log`: seeds 0/1000/2000 and mean `8.347295e-5`.
- `occupancy.py` and `feasibility.jsonl`: 144 solver receipts; `reverse_bc.py` and `reverse_bench.json`: reverse/forward benchmark receipts.

The occupancy synthesis is complete for the stated fixed-L5 embeddings and endpoint candidates. It does not prove unrestricted placement optimality, unrestricted teleport endpoint choices outside the enumerated L5 set, or FT validity of the 66-CX pure endpoint witness; those are deliberately labelled as model scope rather than inferred results.
