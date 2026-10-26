# Current GLOBAL transplant packet

Use [global_v37g_bcflip.qasm](../cand/global_v37g_bcflip.qasm) and matching JSON. The parent is v37g, SHA256 `79fc464667ef82bc8b9b9113a5807a1d9459132e4a4f72fb8a8e68ceaaf6645c`.

The sole semantic edit reverses **CX25→24 to CX24→25 at zero-based tick36**. The checked M25 at37 stays in place. Data ordering, all other operations and detector rows match the parent; see [verified delta](../logs/v37g_delta_verified.json).

Exact L=3.6190305632615202e-05, A=0.50032228639581333; improvement=2.0930892712194536e-08; J relative to v37g=-1.0472192098070637e-08. Selection is lowest L at A>=0.5002. Full QASM SHA256: `10f7b7cd5522c0670541f92addd3b3baaa4a44c73dded7c8099fd2f7a56e8eb8`.

The 1e6 judge check has gates_ok=True and passed=True. The six raw output stabilizers, ideal target and all single faults also pass. [best_resource.json](best_resource.json) binds the exact parent, delta, circuit and evidence.

The earlier75-CX R46 encoder is preserved in [r46_resource75.json](r46_resource75.json). Its added early CNOT needs q25 before v37g releases it: removing CX25→19@30 to advance the reset makes detector15 nondeterministic. That direct port is invalid. Other valid Bell-source swaps and paired reversals tie numerically; they add no measured gain beyond the single reversal.

[RUNTIME.md](../RUNTIME.md) retains the global_bc3_fast slowdown diagnosis. Its prefix MX repairs are independent of this one-CNOT transplant.
