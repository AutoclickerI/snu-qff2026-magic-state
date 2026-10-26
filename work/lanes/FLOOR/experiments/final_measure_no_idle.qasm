OPENQASM 2.0;
include "qelib1.inc";
qreg q[36];
creg c[8];
measure q[1] -> c[0];
h q[0];
id q[0];
id q[0];
