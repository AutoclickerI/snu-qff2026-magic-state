# ENDSTATE attachment interface

From the repository root, with all three thread variables set to 1:

```sh
.venv/bin/python work/lanes/SEPBC/endstate_emit.py \
  work/lanes/ENDSTATE/witness12_h1.json \
  --prefix v29 --choice 0 --route-seed 0 \
  --out work/lanes/SEPBC/endstate_new
```

This writes QASM, judge metadata, the complete native operation plan, a build
receipt, and a full categorical third-order screen. It validates native timing,
adjacency and noiseless correctness. The screen does not replace the required
unchanged CLI check:

```sh
.venv/bin/python work/lanes/EVAL/exact2.py \
  work/lanes/SEPBC/endstate_new.qasm --third --top 30 --procs 4
.venv/bin/python work/lanes/SEPBC/endstate_ablate.py \
  work/lanes/SEPBC/endstate_new --procs 2
```

`--out` accepts a bare stem (placed in SEPBC), a repository-relative path, or an
absolute path. This lane's invocations write only in SEPBC. `--list-choices`
prints the first 64 relative placements and common code automorphisms, ordered
by Manhattan routing distance for search initialization, not fidelity ranking.
For a geometry portfolio:

```sh
.venv/bin/python work/lanes/SEPBC/endstate_search.py \
  work/lanes/ENDSTATE/witness12_h1.json --prefix v29 \
  --tag endstate_new --per-geometry 2 --route-seeds 2 \
  --processes 3 --seconds 3 --emit 4 --alap
```

The source prefix snapshots in `inputs/*.prefix.json` are ENDSTATE's independently
verified causal extractions. `v23` has 75 CX and data `[0,20,7,4,3,15,8]`;
`v29` has 81 CX and data `[0,20,7,10,3,16,8]`. The v29 core extraction omits the
later blue-check package; the earlier pilot preserving that package is separately
recorded in the report.

## Fragment contract

- `ops`: an ordered native program. Each operation has `name`, `qs`, and a unique
  `bit` for M/MX. Supported names are R/RESET, RX, CX, M/MEASURE, MX, H, S,
  S_DAG, X, Y, Z. Every non-data wire starts with R/RX. Native measurement IDs
  are names, not assumed to equal their position in the final circuit.
- `detectors`: lists of the fragment's measurement-bit IDs. These already include
  its teleport/helper frame corrections. The emitter offsets all fragment IDs;
  it does not rederive or discard the supplied frame.
- `final`: role arrays `d`, `a`, `b`, `c`, in logical-code order. The encoded data
  input is `input_data_qubits`, or `final.d` when omitted. Data are coherently
  routed to those input cells; output metadata follows `final.d` with the same
  common Steane automorphism. Fragment-internal data relocation is rejected:
  `input_data_qubits` must currently equal `final.d`. Additional block moves
  are supported.
- `blocks` and `order`: encoder recipes and block order as in witness12_h1.
  Untagged sequential-block fragments use these to identify preparation noise.
  **Interleaved or helper-assisted fragments must tag every op with `region`:**
  `encoder_a`, `encoder_b`, `encoder_c`, `block_teleport`, or `round`.
- Time-indexed fragments can supply `t` per operation and fragment `R`. Round
  operations retain `t-R` while pre-round operations are rescheduled. A per-op
  `round_offset` is an explicit alternative. It can be negative for early A
  coupling. All data-consuming operations wait for the actual routed state.
  Without offsets, the standard D→A/B→C, B→D, and readout phases are used.

Additional moves per block qubit, measured helpers, and reset reuse are ordinary
native operations in this contract; there is no one-move cap in the emitter.
Their ideal validity is supplied by ENDSTATE and rechecked on the full circuit.
Operation tags are essential for meaningful noise ablations.

## Scheduling scope

All legal fragment symmetries/translations and all 168 common Steane
automorphisms are represented. The portfolio covers all 48 relative geometries
for the current full-grid witness. It samples two low-distance automorphisms and
two constructive routes per geometry. Data routes are collision-free coherent
two-CX transfers, with source-zero readout checks. CP-SAT minimizes R for each
chosen route/fragment dependency order, then places preparations late. A final
full-circuit ALAP pass preserves physical per-wire ordering.

Cell lifetimes include destination initialization through source measurement,
all live data states, every prefix reset interval, and every fragment reset
interval. Prefix operations and preparations are scheduled jointly. Preparations
may borrow a prefix cell between resets or before its first use. When an initial
prefix measurement expects implicit |0>, early borrowing requires a real noisy
restoring reset; the solver inserts and prices it. Tagged fragment preparations
may also borrow a data destination before the routed state arrives. The final
CLI regression reproduces the verified A12 circuit byte for byte.

The emitter preserves cultivation interactions and each component's physical
per-wire dependencies. It does not claim globally optimal routes or fidelity.
OPTIMAL is conditional on the selected routes, component dependencies and the
R objective. The earlier R>=63/R>=51 relaxed bounds apply to the pilot model
that required final prefix release, not this expanded model. Counterfactual
noise removals are diagnostics, not attainable scores or lower bounds.

Time-indexed, extra-move and helper-assisted inputs need a full emitted-circuit
check on arrival; the current catalog contains only the original native witness.
Do not interpret interface support as a verified result for a missing fragment.

Each returned fragment can be fed directly to the CLI when it appears. The lane
uses finite catalog snapshots during active work; no unattended polling daemon
is installed.
