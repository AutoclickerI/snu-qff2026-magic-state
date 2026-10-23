# PARITY lane: logical-X parity check on block A

## Ideal-filter danger (ideal_danger.py)
Danger of A's single faults that survive a filter on X-type word M (undetected = even |Z support on M|):
- s7307: raw 6.67e-4, vector [ZL,ZLZ0..6] = [0,3,3,0,4,0,0,0] p/15. Residual 0 only for M={2,4,5}.
- exact (EXENC/prepA_L5_exact.json): raw 5.33e-4, [0,5,0,0,3,0,0,0]. Residual 0 for M={2,4,5} and {1,4,6}.
Weight-4 stabilizer words detect j in S instead (complement of a line); {0,1,3,6} also covers s7307.

## Geometry: no legal gadget on layout L5
Cells (r*6+c): A code order a=[1,14,8,9,2,16,15]; d=[0,20,7,10,3,22,21] sits next to every A cell and holds data
(idle from ~step 30 to the round). A's only non-data neighbours are 13 (touches 14) and 17 (touches 16);
free cells 18,24,30-35 are not adjacent to A. Any check word needs >=3 touched cells, only codes 1 and 5
(cells 14, 16) are reachable, and 13 and 17 cannot be joined into a cat without crossing data or A.
M={2,4,5} -> cells 8,2,16 (neighbours 7,3 are data); {1,4,6} -> 14,2,15 (3, 21 data); weight-4 sets
{1,14,9,15},{1,8,9,16} -> d cells. Early timing (using B/C cells before their preps) needs A prepared
~20 steps early; A's idle Z errors are exactly the danger, so that loses. Late timing has no free cell
(every round qubit is busy at R+1).

## Ceiling (adjacency rule switched off, not submittable): cb_ceil_late.qasm
cand_best base (ST_BC/cand_best.qasm, rebuilt identically by drive.py): exact 3rd 1.0359e-4 (coordinator figure).
Late timing, M={2,4,5}, 3-qubit cat on cells 33-35 (cx 33->34, 33->35 before R; anc->a at R+1; A and anc read at R+2).
First order 5.2e-19, 2nd 5.903e-5, 3rd 8.545e-5 (-17.5%), exp(-A1) 0.5348 (base 0.546).
So the gain is large if the geometry allowed it; extra cat CX = 2, extra cells 3, no extra steps.

## Needed to realise it
A layout where A's cells for the check word each have a free (non-data) neighbour and the ancilla cells form a
connected cat (or one ancilla reaches all three targets, i.e. targets in a "+" or L around one free cell... only
same-colour cells at distance 2 share a neighbour, so a 3-target single-ancilla check needs three A cells
around one free cell). Then B/C preps must be re-synthesised for the new cells. Not attempted (outside this lane).

Files: merge.py (copy with gadget option), drive.py, ideal_danger.py, exact_any.py (exact2 without adjacency; thread caps set).
No MC / tprep.check run: no legal circuit exists.
