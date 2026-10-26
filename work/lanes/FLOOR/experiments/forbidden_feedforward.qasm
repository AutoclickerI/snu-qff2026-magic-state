OPENQASM 2.0;
include "qelib1.inc";
qreg q[36];
creg c[8];
measure q[0] -> c[0];
if(c==1) x q[1];
