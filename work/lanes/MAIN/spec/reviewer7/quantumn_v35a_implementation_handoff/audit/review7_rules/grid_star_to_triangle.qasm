OPENQASM 2.0;
include "qelib1.inc";
qreg q[36];
creg c[1];
reset q[7];
h q[7];
reset q[1];
h q[1];
reset q[6];
h q[6];
reset q[8];
h q[8];
h q[1];
cx q[7],q[1];
h q[1];
h q[6];
cx q[7],q[6];
h q[6];
h q[8];
cx q[7],q[8];
h q[8];
sdg q[7];
h q[7];
measure q[7] -> c[0];
sdg q[1];
sdg q[6];
sdg q[8];
// Endpoint on [1,6,8]: (Z1 Z6 Z8)^c[0] |triangle>.
// This is an endpoint certificate, not a7-qubit competition submission.
