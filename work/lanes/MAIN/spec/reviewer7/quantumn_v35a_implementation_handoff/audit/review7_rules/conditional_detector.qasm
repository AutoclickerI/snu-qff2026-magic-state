OPENQASM 2.0;
include "qelib1.inc";
qreg q[36];
creg c[2];
h q[35];
t q[35];
h q[35];
measure q[35] -> c[0];
h q[0];
t q[0];
cx q[0],q[1];
cx q[1],q[0];
cx q[0],q[1];
h q[2];
h q[6];
cx q[6],q[0];
cx q[6],q[7];
cx q[7],q[6];
cx q[6],q[7];
cx q[1],q[7];
h q[8];
cx q[7],q[8];
cx q[8],q[7];
cx q[7],q[8];
cx q[7],q[6];
cx q[8],q[7];
cx q[7],q[1];
cx q[1],q[2];
cx q[7],q[13];
cx q[13],q[7];
cx q[7],q[13];
cx q[8],q[7];
cx q[2],q[8];
cx q[7],q[1];
cx q[1],q[7];
cx q[7],q[1];
cx q[8],q[7];
cx q[7],q[1];
cx q[1],q[2];
cx q[2],q[1];
cx q[1],q[2];

// POSTSELECT(0) c[0]
// DETECTOR c[0]
// FRAME_X(0)
// FRAME_Z(0)
