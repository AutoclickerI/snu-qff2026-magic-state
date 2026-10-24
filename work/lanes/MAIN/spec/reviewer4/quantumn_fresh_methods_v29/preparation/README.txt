PREPARATION REPLAY SCRIPTS
=========================

Expected bundle layout:
    evaluator/frontend.py
    evaluator/examples/v29c.qasm and v29c.json
    preparation/clean_bus_round.py
    preparation/prefix_v11.qasm
    preparation/frame_syndrome_screen.py
    preparation/frame_pairs.py

From preparation/, using Python with NumPy:
    OPENBLAS_NUM_THREADS=1 python3 clean_bus_round.py
    OPENBLAS_NUM_THREADS=1 python3 frame_syndrome_screen.py
    OPENBLAS_NUM_THREADS=1 python3 frame_pairs.py

clean_bus_round.py recreates the five direct/bus circuits and their ideal and
single-fault checks. The bundled prefix is the first 204 lines of the original
v11_A1i_alap45.qasm used by the experiment. These are grid-free probes, not
valid grid embeddings or submitted circuits.

frame_syndrome_screen.py screens logical-frame choices by single-fault detector
syndrome on unchanged v29c. frame_pairs.py then prices the distinct-channel pairs.
These are screening calculations, not finite-p full-circuit gains.

Replay validation: direct R33 and bus R34 generated QASM bytes are identical to
the original experiment. The v29c screen reproduces all essential counts and
every stored safe-nonidentity and top-frame-benefit row exactly. Validation JSON
receipts are included. The pair script is an unchanged copy using the portable
screen module; it was not rerun during packaging.
