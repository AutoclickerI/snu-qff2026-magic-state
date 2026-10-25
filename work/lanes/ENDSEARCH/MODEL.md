# ENDSEARCH model and coverage contract

For encoded CSS resources, transversal CX preserves each block's Steane
stabilizer space. Every measured block therefore supplies three deterministic
Hamming parity checks in its read basis. Additional deterministic logical
parities and affine logical Pauli frames come from a Choi-state GF(2) solve.
The Choi reference is never measured; existence of both X_ref X_out and
Z_ref Z_out modulo measured operators proves identity on *arbitrary* logical
input on every branch, including when retained helpers are traced out.

The search includes every pure CSS state of the ancillary *logical qubits*,
not only product |0_L>, |+_L>: all subspaces of GF(2)^(n-1), with independent
X-generators and their orthogonal Z-space. This includes logical Bell pairs
and encoded GHZ resources. Ancillary labels are quotiented by all (n-1)!
permutations, with D fixed; every possible output block is considered.
A tick is any nonempty matching of directed CXs. Repeated edges remain legal.
Measurements happen one tick after a block's last gate. An omitted read leaves
a retained helper. There are 3^(n-1) X/Z/unmeasured read assignments per output.
Both connected and disconnected interaction graphs are covered: an initial
Bell/CSS resource can entangle components that have no transversal CX between
them. A block with no CX is read at tick 0 or retained. The separate
`-DONLY_DISCONNECTED` sweep checks those cases with the same Choi test.

Per-index exact second-order calculation:
- Propagate all 15 post-CX Paulis (weight p/15) and idle X/Y/Z (p/3).
- A fault on one index passes block syndrome checks iff every measured record
  flip is zero. A pair on *different* indices also requires both flips zero:
  two distinct nonzero Hamming columns cannot cancel.
- A pair at one index gives at most one output Pauli. If its record flips
  cancel, affine frames cancel too, so the judge corrects it.
- Thus c1=0 and c2=21*[0.5*(rX+rY)^2+rZ^2+2*rY*rZ]/225, where r are
  undetected per-index rates in units p/15. Measurement faults do not contribute
  to c2; their same-index partners remain correctable. They affect all orders.
- This is TERM's exact second-order terminal model, extended by automatic
  propagation and a general ideal instrument solve. It is not a fit.

The reported frontier requires incoming full-rank checking: an initial X_i
and Z_i must each reach a measured record, giving three Hamming rows per axis.
Rank-0/3 assignments are counted but excluded from that frontier. They remain
an unresolved boundary problem under the certified universal bound; this does
not prove they cannot improve a different complete circuit.
Resource logical-error visibility is also separate from terminal c1: a verified
resource may be necessary even when a perfect-resource tail has c1=0.

Non-encoded literal product and physical cat/GHZ resources are not equivalent
to the encoded logical resource family. For those, the three readout syndrome
rows need not be deterministic; the encoded rate formula must not be reused.
Their complete physical stabilizer instruments require a separate solve. The
certified universal bound 1.3657850790536654e-5 applies to all of them, as does
the measured-partner floor when its structural premise holds. Neither bound
excludes an improvement over v37b; any unenumerated remainder will be reported
as open, not silently merged into an exhaustive claim.

## Resource-independent oracle bound for the unenumerated physical family
For any fixed schedule, output choice and measurement bases, pretend *every*
measured physical bit is a deterministic detector. This over-rejects faults:
all zero-record-flip faults certainly pass every real deterministic detector
and do not change any affine frame. Two such faults at distinct code indices
therefore contribute exactly TERM's positive pair cost. For any first-order
safe instrument (N0=N1=0), normalization does not alter c2, and all other
accepted two-fault contributions are nonnegative. Hence that rate cost is a
rigorous second-order LOWER BOUND independent of resource type or entanglement.
`search.cpp -DONLY_RELAX` enumerates this bound before any resource/ideal filter,
including physically impossible instruments. It covers literal product/cat/
physical-Bell resources at 3-4 ticks where the full physical enumeration is too
large. It must not be compared to a finite-p all-orders value as though exact.
The certified BOUND channel factorization supplies the separate all-orders
lower bound 1.3657850790536654e-5 for every omitted family. A lower bound below a
candidate does not certify that candidate globally optimal.


The terminal sweep assumes every perfect resource is already present at tick 0
and charges subsequent idle noise. Interleaving nontransversal preparation
with the round changes that boundary and is outside its second-order bound.
Full suffixes also test just-in-time schedules: each ancillary block becomes
ready at its first coupling, which can occur after the first round tick.
Those experiments include every preparation gate, idle and measurement.
