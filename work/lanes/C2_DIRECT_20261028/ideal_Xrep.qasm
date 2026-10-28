OPENQASM 2.0;
include "qelib1.inc";
qreg q[36];
creg c[7];
reset q[6];
h q[6];
reset q[20];
h q[20];
reset q[19];
h q[19];
reset q[10];
h q[10];
reset q[2];
reset q[22];
reset q[16];
barrier q[2],q[6],q[7],q[8],q[9],q[10],q[13],q[14],q[15],q[16],q[19],q[20],q[21],q[22];
t q[19];
barrier q[2],q[6],q[7],q[8],q[9],q[10],q[13],q[14],q[15],q[16],q[19],q[20],q[21],q[22];
cx q[19],q[2];
barrier q[2],q[6],q[7],q[8],q[9],q[10],q[13],q[14],q[15],q[16],q[19],q[20],q[21],q[22];
cx q[19],q[22];
barrier q[2],q[6],q[7],q[8],q[9],q[10],q[13],q[14],q[15],q[16],q[19],q[20],q[21],q[22];
cx q[6],q[19];
cx q[20],q[22];
cx q[10],q[16];
barrier q[2],q[6],q[7],q[8],q[9],q[10],q[13],q[14],q[15],q[16],q[19],q[20],q[21],q[22];
cx q[6],q[2];
cx q[20],q[16];
cx q[10],q[22];
barrier q[2],q[6],q[7],q[8],q[9],q[10],q[13],q[14],q[15],q[16],q[19],q[20],q[21],q[22];
cx q[6],q[16];
cx q[20],q[19];
cx q[10],q[2];
reset q[7];
reset q[14];
reset q[13];
reset q[9];
reset q[8];
reset q[21];
reset q[15];
barrier q[2],q[6],q[7],q[8],q[9],q[10],q[13],q[14],q[15],q[16],q[19],q[20],q[21],q[22];
cx q[6],q[7];
cx q[20],q[14];
cx q[19],q[13];
cx q[10],q[9];
cx q[2],q[8];
cx q[22],q[21];
cx q[16],q[15];
barrier q[2],q[6],q[7],q[8],q[9],q[10],q[13],q[14],q[15],q[16],q[19],q[20],q[21],q[22];
cx q[6],q[7];
cx q[20],q[14];
cx q[19],q[13];
cx q[10],q[9];
cx q[2],q[8];
cx q[22],q[21];
cx q[16],q[15];
barrier q[2],q[6],q[7],q[8],q[9],q[10],q[13],q[14],q[15],q[16],q[19],q[20],q[21],q[22];
measure q[7] -> c[0];
measure q[14] -> c[1];
measure q[13] -> c[2];
measure q[9] -> c[3];
measure q[8] -> c[4];
measure q[21] -> c[5];
measure q[15] -> c[6];
id q[6];
id q[20];
id q[19];
id q[10];
id q[2];
id q[22];
id q[16];
// DETECTOR c[0]
// DETECTOR c[1]
// DETECTOR c[2]
// DETECTOR c[3]
// DETECTOR c[4]
// DETECTOR c[5]
// DETECTOR c[6]
