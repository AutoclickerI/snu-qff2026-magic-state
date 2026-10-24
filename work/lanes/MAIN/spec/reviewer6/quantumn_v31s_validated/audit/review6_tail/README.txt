REVIEW 6: SX GAUGE PORTS, COMPOSITIONS AND RUNTIME AUDIT
=====================================================

Source: AutoclickerI/quantumn commit
abf26aa98bede59bb07f7da838dd1b3a3fdf76f0.

Outcome
-------
The physical SX/SXDG round gauge improves the expected noise-model loss on
both fresh baselines. The strongest composed expectation is
4.906329891346021e-5, with 192 CX and native depth 48. However, the combined
A-decoder + SX candidates trigger a slow official noisy-sampling path.
They are not the practical promotion recommendation at present.

The architecture lane's original v31s A partial decoder is the fast option:
    input snapshot: inputs/v31s_a_decode.qasm and .json
    expected loss: 4.9485457947061475e-5
    acceptance:    0.5366494669060742
    CX / depth:    191 / 48
Its official 1e6-shot check passed in about 2.67 s in the validation lane.
The validation lane manages the separate official 1e8-shot run and receipt.

REPORT.txt records all model results and the operational limitation.
XTIM_AUDIT.txt gives the bounded source audit and failed runtime repairs.
All models and scores are local review artifacts; no remote job, push or
submission was performed from this lane.

Reproduce the model results
--------------------------
Python 3.12 and NumPy 2.3.5 were used. From this directory:

    OPENBLAS_NUM_THREADS=1 python3 sparse_walsh.py v31s_a_decode_sx 72 canonical
    OPENBLAS_NUM_THREADS=1 python3 sparse_walsh.py v31s_a_decode_sx_c28_29 72 canonical

The command evaluates acceptance and all 72 nonzero decoder moments. A
completed score has 73 entries in its results list and a final loss field.
There is no Monte Carlo or fault-order truncation. The reported numerical
cutoff bound excludes floating-point roundoff.

Regenerate the already-priced circuits and small certificates:

    python3 build_ports.py
    python3 build_ports.py inputs/v30g_a_decode inputs/v31s_a_decode
    python3 add_c_edge.py
    python3 terminal_order_probes.py
    python3 reset3_probe.py

terminal_order_probes.py produces two physics-identical traversal orders,
not new physical loss candidates. reset3_probe.py changes preparation noise
and its two circuits were independently repriced at all fault orders.

Input snapshots
---------------
inputs/v30g and inputs/v31s are the pinned repository baselines, with their
committed full all-orders receipts. inputs/v30g_a_decode and v31s_a_decode
are the fresh architecture lane's A-readout ports and their completed
receipts. Source and QASM hashes are retained in candidate metadata.

Evaluator scope and provenance
------------------------------
The independent frontend supports this flat H/CX/T/Tdg/reset/measurement
family with added native S/Sdg/SX/SXdg and logical parity frames. Explicit
POSTSELECT is unsupported. Its sparse kernel assumptions are checked when
preparing a score. It is not a substitute for the official general frontend.

The evaluator was carried forward from review5_tail, itself derived from
reaudit_evaluation/portable. Basis/Engine definitions originate from
AutoclickerI/quantumn EVAL code at
57e99b97dd2dd6c19fab3f7d706eaaaa9f165610.

judge_subset files originate from the official judge commit
76fe47c0324f1c1f8b72a7d55af200e88043b522; its MIT license is included.
Official runtime checks use the separate untouched validator installation
with xtim 3.1.3+qff2, qiskit 2.5.2 and stim 1.16.0. The model receipts in
this directory are expectation calculations, not official Monte Carlo scores.
