Main session: I interrupted your turn on purpose (your owl containers keep running; collect their results) because
CONTRACT has finished and measured much of your new scope. Read work/lanes/CONTRACT/REPORT.md, AUDIT.md and
results.json now (read only). Its findings:
- Reviewer 18's bound reduction holds (case-by-case audit, no counterexample); floor 2.1892512824770078e-5.
- Option (a), late growth: all 24 minimal three-CX CSS encoders into C4 fail; best growth + contraction with a perfect
  incoming 7-qubit state 8.717e-5; full circuit 1.366e-4 (grid-native witness 3.318e-4, A 0.48).
- Option (b), early growth: storage before both outer checks, B reusing A's cells, four Z-constraint readouts:
  full 1.105e-4 at A 0.372; the last encoded B check + contraction alone (noise from tick 58 only) 5.156e-5; ZZ(D,K)
  storage 8.661e-5 full, 5.505e-5 for its outer check + tail alone.
- Option (c): best complete alternative (C as the unmeasured-helper checker, 21-CX B/C, 9-CX verified A, ready at
  tick 44) 4.368e-5 at A 0.521; with its resource preparation made perfect still 3.611e-5, i.e. no better than v37h.
- Geometry: with D movable a connected 8-cell bus touching all seven non-square (path K-D-H-L) tiles exists.
So far every C4 variant's own check + contraction costs more than v37h's whole circuit. Finish the four prices you
started (C4 and its X/Z dual, with and without an inner XXXX check). Continue a variant only if an optimistic
diagnostic of it (resource preparation perfect, or noise only from its outer check on) is below 3.4e-5; when none is,
close the lane with the measured obstacle per variant in REPORT.md and stop (stop your owl containers by ID). Other
rules, hosts and the finalist criterion as in CONTINUE4.md.
