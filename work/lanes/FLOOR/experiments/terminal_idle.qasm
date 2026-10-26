OPENQASM 2.0;
include "qelib1.inc";
qreg q[36];
creg c[8];
h q[0];
cx q[0],q[1];
measure q[1] -> c[0];
