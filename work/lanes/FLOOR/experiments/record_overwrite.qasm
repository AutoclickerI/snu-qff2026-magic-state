OPENQASM 2.0;
include "qelib1.inc";
qreg q[36];
creg c[8];
measure q[0] -> c[0];
measure q[1] -> c[0];
// DETECTOR c[0]
// FRAME_X(0) c[0]
// FRAME_Z(0)
